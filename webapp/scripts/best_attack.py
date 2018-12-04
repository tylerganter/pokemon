"""

"""

# TODO CONTINUE HERE
# fix gen 4...
# weight functions
# filter attacks

# TODO Clear some attacks: future sight, outrage, focus punch
# TODO add "exceptions" to the same general file (ditto...)

# TODO make the different weight functions store to different files
# TODO try different weight functions
# TODO externalize the weight functions

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


def _single_pokemon_pokemon(attacking_pokemon_row, store_data):
    """"""
    (poketype_chart, pokedex, attackdex, learnsets) \
        = (store_data[key] for key in ('poketype_chart', 'pokedex',
                                       'attackdex', 'learnsets'))

    attacking_pokemon = pokedex.iloc[attacking_pokemon_row]

    """exceptions..."""

    # TODO better solution for this?
    if attacking_pokemon['name'] in ['Ditto',
                                     'Wobbuffet',
                                     'Smeargle',
                                     'Wynaut']:
        best_combo = {
            'score': 0,
            'move_poketypes': [''] * 4,
            'move_names': [''] * 4
        }
        return best_combo

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

    """Fill matrix: Attack X defending pokemon"""

    damage_matrix = np.zeros((len(poketypes), pokedex.shape[0]))

    for row, poketype in enumerate(poketypes):
        move = best_move_per_poketype[poketype]

        for col, defending_pokemon in pokedex.iterrows():
            damage = effective_damage(move, poketype_chart,
                                      attacking_pokemon=attacking_pokemon,
                                      defending_pokemon=defending_pokemon)

            # TODO process_presum (move this elsewhere as a function)
            # damage = damage / (float(defending_pokemon['hp']) / 100)

            damage = damage * np.sum([float(defending_pokemon[key])
                                      for key in ('hp',
                                                  'attack',
                                                  'defense',
                                                  'sp_attack',
                                                  'sp_defense',
                                                  'speed')]) / 600

            damage_matrix[row, col] = damage

    """Apply weights if so desired"""

    # TODO play with this!
    # TODO process_post_sum
    # damage_matrix = damage_matrix**0.1

    """Find 4 rows that maximize the sum across columns"""

    best_combo = None

    for combo in combinations(range(len(poketypes)), min(len(poketypes), 4)):
        # acquire the subset for this combo of attack types
        combo_matrix = damage_matrix[combo, :]

        # select the max (best) for each attack/defense pair
        max_combo_matrix = np.max(combo_matrix, axis=0)

        score = np.sum(max_combo_matrix) / len(max_combo_matrix)

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

    return best_combo

def pokemon_pokemon(overwrite=False):
    """
    best A pokemon for all D pokemon
      4 Attacks & Pokemon, Pokemon
    """
    filepath = 'webapp/data/results/gen_{:d}_simple.hdf5'.format(settings.__gen__)
    # filepath = 'results/gen_{:d}_2.hdf5'.format(settings.__gen__)
    filepath = os.path.join(settings.project_path, filepath)

    if overwrite or not os.path.exists(filepath):
        results = []
        num_processed = 0
    else:
        with pd.HDFStore(filepath, mode='r') as store:
            stored_result = store['result']
            num_processed = stored_result.shape[0]
            results = list(stored_result.values)

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

    for index, pokemon in pokedex.iterrows():
        # if index < 13:
        #     continue
        # if index > 50:
        #     break

        if not overwrite and index < num_processed:
            continue

        full_name = '|'.join([pokemon['name'], pokemon['subname']])
        print('processing: %3d/%3d - %s' % (index, pokedex.shape[0],
                                            full_name))

        best_combo = _single_pokemon_pokemon(index, store_data)

        cur_result = [pokemon['name'], pokemon['subname']] \
                     + best_combo['move_names'] \
                     + [best_combo['score']]

        results.append(cur_result)

        with pd.HDFStore(filepath, mode='a') as store:
            store['result'] = pd.DataFrame(results, columns=col_names)

    return pd.DataFrame(results, columns=col_names)


if __name__ == '__main__':
    settings.init(GEN=2)

    # sorted_moves = sorted_moves_per_poketype()

    result = pokemon_pokemon(overwrite=False)

    result = result.sort_values(by=['score'])
    print(result)
