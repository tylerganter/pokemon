"""

"""

# Standard library imports
import os
from itertools import combinations

# Third party imports
import numpy as np
import pandas as pd

# Local application imports
import settings
from harmonic_mean import harmonic_mean
from helpers import SortedMoves, effective_damage
import dex_exceptions


def modifier_function(damage, move, attacking_pokemon, defending_pokemon):
    """

    :param damage:              scalar
    :param move:                pandas Series
    :param attacking_pokemon:   pandas Series
    :param defending_pokemon:   pandas Series
    :return: modified scalar
    """

    # damage is now a ratio of the defending pokemon's health
    damage = damage / (float(defending_pokemon['hp']) / 100)

    # damage = damage * np.sum([float(defending_pokemon[key])
    #                           for key in ('hp',
    #                                       'attack',
    #                                       'defense',
    #                                       'sp_attack',
    #                                       'sp_defense',
    #                                       'speed')]) / 600

    return damage

def score_function(mc_vector):
    """

    :param mc_vector: <# of pokemon> length vector
    :return:
    """

    if settings.__method__ == 'min':
        score = min(mc_vector)
    elif settings.__method__ == 'mean':
        score = np.mean(mc_vector)
    elif settings.__method__ == 'median':
        score = np.median(mc_vector)
    elif settings.__method__ == 'harmonic_mean':
        score = harmonic_mean(mc_vector)
    else:
        raise AttributeError

    return score

def compute_defense_scores(damage_matrix):
    """"""

    defense_matrix = damage_matrix.values

    if settings.__method__ == 'min':
        defense_vector = np.max(defense_matrix, axis=0)
    elif settings.__method__ == 'mean':
        defense_vector = np.zeros(damage_matrix.shape[1])

        for i in range(len(defense_vector)):
            # skip zeros (situations where the attacker cannot harm the
            # defender) Examples:
            #               Ditto   attacking anyone
            #               Metapod attacking Haunter
            temp = defense_matrix[:, i]
            temp = temp[temp > 0]

            defense_vector[i] = harmonic_mean(temp)

    elif settings.__method__ == 'median':
        defense_vector = np.median(defense_matrix, axis=0)
    elif settings.__method__ == 'harmonic_mean':
        defense_vector = np.mean(defense_matrix, axis=0)

    else:
        raise AttributeError

    return defense_vector

def add_defense_scores(moves_and_scores, damage_matrix):
    defense_scores = compute_defense_scores(damage_matrix)

    moves_and_scores['d_score'] = pd.Series(defense_scores,
                                            index=moves_and_scores.index,
                                            dtype='int16')

    return moves_and_scores

def _single_pokemon_pokemon(attacking_pokemon_row, store_data):
    """"""
    (poketype_chart, pokedex, attackdex, learnsets) \
        = (store_data[key] for key in ('poketype_chart', 'pokedex',
                                       'attackdex', 'learnsets'))

    attacking_pokemon = pokedex.iloc[attacking_pokemon_row]

    """Strongest attack of each poketype"""

    def get_best_move_per_poketype(pokemon, pokedex, attackdex, learnsets):
        full_name = '|'.join([pokemon['name'], pokemon['subname']])

        cur_pokemon_moves = attackdex[learnsets[full_name]]['name']

        best_move_per_poketype = {}

        for poketype, poketype_moves in SortedMoves().sorted_moves.items():
            # moves of specific poketype that this pokemon can learn
            moves = \
                poketype_moves[poketype_moves['name'].isin(cur_pokemon_moves)]

            # omit moves that are on the skip list
            moves = moves[~moves['name'].isin(dex_exceptions.move_skip_list)]

            # there are any...
            if moves.shape[0] > 0:
                # save the best one
                best_move_per_poketype[poketype] = moves.iloc[0]

        return best_move_per_poketype

    best_move_per_poketype = get_best_move_per_poketype(attacking_pokemon,
                                                        pokedex,
                                                        attackdex,
                                                        learnsets)

    poketypes = list(best_move_per_poketype.keys())

    """Fill matrix: Attack X Defending pokemon"""

    damage_matrix = np.zeros((len(poketypes), pokedex.shape[0]))

    for row, poketype in enumerate(poketypes):
        move = best_move_per_poketype[poketype]

        for col, defending_pokemon in pokedex.iterrows():
            damage = effective_damage(move, poketype_chart,
                                      attacking_pokemon=attacking_pokemon,
                                      defending_pokemon=defending_pokemon)

            damage = modifier_function(damage, move,
                                       attacking_pokemon, defending_pokemon)

            damage_matrix[row, col] = damage

    """Find 4 rows that maximize the sum across columns"""

    best_combo = None
    best_damage_vector = None

    for combo in combinations(range(len(poketypes)), min(len(poketypes), 4)):
        # acquire the subset for this combo of attack types
        combo_matrix = damage_matrix[combo, :]

        # select the max (best) for each attack/defense pair
        max_combo_vector = np.max(combo_matrix, axis=0)

        score = score_function(max_combo_vector)

        if best_combo is None or score > best_combo['a_score']:
            move_poketypes = [poketypes[i] for i in combo]
            move_names = [best_move_per_poketype[poketype]['name']
                          for poketype in move_poketypes]

            best_combo = {
                'a_score': score,
                'move_names': move_names
            }
            best_damage_vector = max_combo_vector

    best_moves_and_scores = -1 * np.ones(6, dtype='int16')
    for idx, move_name in enumerate(best_combo['move_names']):
        move_index = attackdex.index[attackdex['name'] == move_name].tolist()[0]
        best_moves_and_scores[idx] = move_index
    best_moves_and_scores[4] = best_combo['a_score']

    best_damage_vector = np.round(best_damage_vector).astype('int16')

    return best_moves_and_scores, best_damage_vector

def pokemon_pokemon(overwrite=False, start_idx=0, end_idx=np.inf):
    """
    best A pokemon for all D pokemon
      4 Attacks & Pokemon, Pokemon
    """
    def load_database():
        with pd.HDFStore(settings.store_filepath, mode='r') as store:
            # poketypes = store['poketypes']
            # move_categories = store['move_categories']
            poketype_chart = store['poketype_chart']
            pokedex = store['pokedex']
            attackdex = store['attackdex']
            learnsets = store['learnsets']

            database = {
                'poketype_chart': poketype_chart,
                'pokedex': pokedex,
                'attackdex': attackdex,
                'learnsets': learnsets
            }

        return database

    def load_results(overwrite, database):
        """initialize or load the results"""

        if overwrite or not os.path.exists(settings.result_filepath):
            num_pokemon = database['pokedex'].shape[0]

            col_names = ['move1', 'move2', 'move3', 'move4',
                         'a_score', 'd_score']
            moves_and_scores = -1 * np.ones((num_pokemon, len(col_names)),
                                            dtype='int16')
            moves_and_scores = pd.DataFrame(moves_and_scores, columns=col_names)

            full_pokemon_names = pokedex['name']
            for index, subname in enumerate(pokedex['subname']):
                if len(subname) > 0:
                    full_pokemon_names.iloc[index] = \
                        full_pokemon_names.iloc[index] + '-' + subname

            damage_matrix = np.zeros((num_pokemon, num_pokemon), dtype='int16')
            damage_matrix = pd.DataFrame(damage_matrix,
                                         columns=full_pokemon_names)
        else:
            with pd.HDFStore(settings.result_filepath, mode='r') as store:
                moves_and_scores = store['moves_and_scores']
                damage_matrix = store['damage_matrix']

        return moves_and_scores, damage_matrix

    database = load_database()
    pokedex = database['pokedex']

    moves_and_scores, damage_matrix = load_results(overwrite=overwrite,
                                                   database=database)

    for index, pokemon in pokedex.iterrows():
        if index < start_idx:
            continue
        if index > end_idx:
            break

        if not overwrite and (moves_and_scores.iloc[index, 0] != -1):
            continue

        # exceptions...
        if pokemon['name'] in dex_exceptions.attacking_pokemon_exceptions:
            continue

        print('processing: %3d/%3d - %s' % (index, pokedex.shape[0],
                                            damage_matrix.columns[index]))

        row_moves_and_scores, damage_vector \
            = _single_pokemon_pokemon(index, database)

        moves_and_scores.iloc[index] = row_moves_and_scores
        damage_matrix.iloc[index] = damage_vector

        # with pd.HDFStore(settings.result_filepath, mode='a') as store:
        #     store['moves_and_scores'] = moves_and_scores.astype('int16')
        #     store['damage_matrix'] = damage_matrix.astype('int16')

    """Add defense scores to results"""

    damage_matrix = damage_matrix.astype('int16')
    moves_and_scores = add_defense_scores(moves_and_scores,
                                          damage_matrix).astype('int16')

    """Write the results"""

    with pd.HDFStore(settings.result_filepath, mode='a') as store:
        store['moves_and_scores'] = moves_and_scores
        store['damage_matrix'] = damage_matrix

    return moves_and_scores, damage_matrix


if __name__ == '__main__':
    # METHOD = 'mean'
    # METHOD = 'median'
    METHOD = 'harmonic_mean'
    # METHOD = 'min'

    settings.init(GEN=3, METHOD=METHOD)

    start_idx = 0
    end_idx = 1000

    moves_and_scores, damage_matrix = pokemon_pokemon(overwrite=False,
                                                      start_idx=start_idx,
                                                      end_idx=end_idx)

    print(moves_and_scores.head())
    print(damage_matrix.head())
