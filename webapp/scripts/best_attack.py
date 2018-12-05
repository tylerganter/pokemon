"""

"""

# Standard library imports
import os
from itertools import combinations

# Third party imports
import numpy as np
import pandas as pd

# Local application imports
from context import settings
from preparatory import sorted_moves_per_poketype
from formulas import effective_damage
import exceptions


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
    elif settings.__method__ == 'power':
        if np.min(mc_vector) == 0:
            return 0
        else:
            P = -1
            score = np.power(np.mean(np.power(mc_vector, P)), 1 / P)
    else:
        raise AttributeError

    return score

def defense_scores(vectors):
    # TODO these should be opposite functions!!!

    defense_matrix = vectors.values

    if settings.__method__ == 'min':
        defense_vector = np.max(defense_matrix, axis=0)
    elif settings.__method__ == 'mean':
        defense_vector = np.mean(defense_matrix, axis=0)
    elif settings.__method__ == 'median':
        defense_vector = np.median(defense_matrix, axis=0)
    elif settings.__method__ == 'power':
        # TODO does this need to be an inverse function or something...?
        P = -1
        defense_vector = np.power(np.mean(np.power(defense_matrix, P),
                                          axis=0), 1 / P)
    else:
        raise AttributeError

    return pd.DataFrame(defense_vector, index=vectors.columns)

def _single_pokemon_pokemon(attacking_pokemon_row, store_data):
    """"""
    (poketype_chart, pokedex, attackdex, learnsets) \
        = (store_data[key] for key in ('poketype_chart', 'pokedex',
                                       'attackdex', 'learnsets'))

    attacking_pokemon = pokedex.iloc[attacking_pokemon_row]

    """exceptions..."""

    if attacking_pokemon['name'] in exceptions.attacking_pokemon_exceptions:
        return exceptions.best_combo_exception, np.zeros(pokedex.shape[0])

    """Strongest attack if each poketype"""

    def get_best_move_per_poketype(pokemon, pokedex, attackdex, learnsets):

        sorted_moves = sorted_moves_per_poketype()

        full_name = '|'.join([pokemon['name'], pokemon['subname']])

        cur_pokemon_moves = attackdex[learnsets[full_name]]['name']

        best_move_per_poketype = {}

        for poketype, poketype_moves in sorted_moves.items():
            # moves of specific poketype that this pokemon can learn
            moves = \
                poketype_moves[poketype_moves['name'].isin(cur_pokemon_moves)]

            # omit moves that are on the skip list
            moves = moves[~moves['name'].isin(exceptions.move_skip_list)]

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
    _saved_mc_vector = None

    for combo in combinations(range(len(poketypes)), min(len(poketypes), 4)):
        # acquire the subset for this combo of attack types
        combo_matrix = damage_matrix[combo, :]

        # select the max (best) for each attack/defense pair
        max_combo_vector = np.max(combo_matrix, axis=0)

        score = score_function(max_combo_vector)

        if best_combo is None or score > best_combo['score']:
            move_poketypes = [poketypes[i] for i in combo]
            move_names = [best_move_per_poketype[poketype]['name']
                          for poketype in move_poketypes]

            # extra blank/empty moves due to the pokemon only being capable
            # of less than 4 move types
            num_extra = max(4 - len(move_poketypes), 0)

            best_combo = {
                'score': score,
                'move_poketypes': move_poketypes + [''] * num_extra,
                'move_names': move_names + [''] * num_extra
            }
            _saved_mc_vector = max_combo_vector

    return best_combo, _saved_mc_vector

def pokemon_pokemon(overwrite=False, start_idx=0, end_idx=np.inf):
    """
    best A pokemon for all D pokemon
      4 Attacks & Pokemon, Pokemon
    """
    if overwrite or not os.path.exists(settings.result_filepath):
        results = []
        vectors = []
        num_processed = 0
    else:
        with pd.HDFStore(settings.result_filepath, mode='r') as store:
            stored_result = store['result']
            stored_vectors = store['vectors']
            num_processed = stored_result.shape[0]
            results = list(stored_result.values)
            vectors = list(stored_vectors.values)

    with pd.HDFStore(settings.store_filepath, mode='r') as store:
        # poketypes = store['poketypes']
        # move_categories = store['move_categories']
        poketype_chart = store['poketype_chart']
        pokedex = store['pokedex']
        attackdex = store['attackdex']
        learnsets = store['learnsets']

        store_data = {
            'poketype_chart': poketype_chart,
            'pokedex': pokedex,
            'attackdex': attackdex,
            'learnsets': learnsets
        }

    col_names = ['pokemon', 'subname',
                 'move1', 'move2', 'move3', 'move4',
                 'score']
    full_pokemon_names = pokedex['name'] + pokedex['subname']

    for index, pokemon in pokedex.iterrows():
        if index < start_idx:
            continue
        if index > end_idx:
            break

        if not overwrite and index < num_processed:
            continue

        full_name = '|'.join([pokemon['name'], pokemon['subname']])
        print('processing: %3d/%3d - %s' % (index, pokedex.shape[0],
                                            full_name))

        best_combo, _saved_mc_vector \
            = _single_pokemon_pokemon(index, store_data)

        cur_result = [pokemon['name'], pokemon['subname']] \
                     + best_combo['move_names'] \
                     + [best_combo['score']]

        results.append(cur_result)
        vectors.append(_saved_mc_vector)

        with pd.HDFStore(settings.result_filepath, mode='a') as store:
            store['result'] = pd.DataFrame(results, columns=col_names)
            store['vectors'] = pd.DataFrame(vectors, columns=full_pokemon_names)

    return (pd.DataFrame(results, columns=col_names),
            pd.DataFrame(vectors, columns=full_pokemon_names))

def hist_max_combo_vector(mc_vector, result):
    import matplotlib.pyplot as plt
    bins = np.exp((np.linspace(np.log(min(mc_vector)),
                               np.log(max(mc_vector)), num=30)))
    plt.xscale('log')
    plt.hist(mc_vector, bins=bins)

    title = 'min: {}'.format(np.min(mc_vector))
    title += '\nmax: {}'.format(np.max(mc_vector))
    title += '\nmean: {}'.format(np.mean(mc_vector))
    title += '\nmedian: {}'.format(np.median(mc_vector))
    plt.xlabel(title)

    # plt.title(str(result))
    plt.title(result['pokemon'] + result['subname'])

    plt.show()


if __name__ == '__main__':
    # METHOD = 'mean'
    # METHOD = 'median'
    # METHOD = 'power'
    METHOD = 'min'

    settings.init(GEN=1, METHOD=METHOD)

    start_idx = 0
    end_idx = 1000

    results, vectors = pokemon_pokemon(overwrite=True,
                                       start_idx=start_idx, end_idx=end_idx)

    """"""
    # TODO CONTINUE HERE
    # TODO add defense scores to results
    # then split this into two files:
    #   one goes in data acquisition
    #   the other just reads data and plots histograms

    """Attack Result"""

    results = results.sort_values(by=['score'], ascending=False)
    results = results.reset_index(drop=True)
    print(results.head(n=20))

    """Defense Result"""

    defense_vector = defense_scores(vectors)

    defense_vector = defense_vector.sort_values(by=[0])
    print(defense_vector.head(n=20))

    """Histograms"""

    # TODO histogram ATTACK and DEFENSE
    # for a given pokemon:
    #   attack is a row
    #   defense is a column

    # TODO this is broken because results have been sorted but vectors arent
    # IDX = 0
    # hist_max_combo_vector(vectors.iloc[IDX], results.iloc[IDX])
