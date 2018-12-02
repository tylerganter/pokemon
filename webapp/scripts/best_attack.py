"""

"""

# TODO get gen 1 working (dark and steel types), i.e. get the correct types for pokemon
# TODO get gen 7 junction working
# TODO try different weight functions
# TODO Clear some attacks: future sight, outrage, focus punch

from __future__ import division, print_function
# from __future__ import absolute_import #TODO why doesn't pycharm like this?

import os
import numpy as np
import pandas as pd
from itertools import combinations

from load_data import load_data
from formulas import effective_damage

def sorted_moves_per_poketype():
    """
    compute the effective power of each move and then split by poketype and sort

    :param gen:
    :return: a dictionary where each key is a poketype
            and each value is a dataframe of moves of that poketype
            sorted by effective power
    """
    poketype_chart, poke_dex, attack_dex, pa_junction = load_data(__gen__)
    poketypes = list(poketype_chart.columns)

    # compute and set the effective power
    effective_power = attack_dex['power'] * attack_dex['accuracy'] / 100 \
                      * attack_dex['repeat'] / attack_dex['turns_used']

    attack_dex['effective_power'] = effective_power

    sorted_moves = {}

    for poketype in poketypes:
        subdex = attack_dex[attack_dex['poketype'] == poketype]

        subdex = subdex.sort_values(by=['effective_power'], ascending=False)

        sorted_moves[poketype] = subdex

    return sorted_moves

def poketype_poketype(num_attack_poketypes=4):
    """
    Best attack poketype (set) for all defense poketypes
    :return:
    """
    poketype_chart, poke_dex, attack_dex = load_data(gen=__gen__)
    poketypes = list(poketype_chart.columns)

    result = {}

    for combo in combinations(range(len(poketypes)), num_attack_poketypes):
        # acquire the subset for this combo of attack types
        combo_chart = poketype_chart.values[combo, :]

        # select the max (best) for each attack/defense pair
        max_combo_chart = np.max(combo_chart, axis=0)

        # compute score
        # TODO maybe weigth the equation by an exponential?
        score = sum(max_combo_chart)
        # score = sum(max_combo_chart**0.1)

        combo_types = [poketypes[i] for i in combo]

        # store new result to dictionary
        if score in result:
            result[score] = result[score] + [combo_types]
        else:
            result[score] = [combo_types]

    return result

def poketype_pokemon():
    # best A poketype (set) for all D pokemon         DummyAttack, Pokemon
    pass

def pokemon_poketype():
    # best A pokemon for all D poketypes              4 Attacks & Pokemon, DummyPokemon
    pass

def _single_pokemon_pokemon(attacking_pokemon_row, store_data):
    """"""
    (poketype_chart, poke_dex, attack_dex, pa_junction) = store_data

    attacking_pokemon = poke_dex.iloc[attacking_pokemon_row]

    """exceptions..."""

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

    def get_best_move_per_poketype(pokemon,
                                   poke_dex, attack_dex, pa_junction):

        sorted_moves = sorted_moves_per_poketype()
        cur_pokemon_moves = attack_dex[pa_junction[pokemon['name']]]['name']

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
                                                        poke_dex,
                                                        attack_dex,
                                                        pa_junction)
    poketypes = list(best_move_per_poketype.keys())

    """Fill matrix: Attack X defending pokemon"""

    damage_matrix = np.zeros((len(poketypes), poke_dex.shape[0]))

    for row, poketype in enumerate(poketypes):
        move = best_move_per_poketype[poketype]

        for col, defending_pokemon in poke_dex.iterrows():
            # print(attacking_pokemon['name']
            #       + ' VS '
            #       + defending_pokemon['name'])

            damage = effective_damage(__gen__, move, poketype_chart,
                                      attacking_pokemon=attacking_pokemon,
                                      defending_pokemon=defending_pokemon)

            damage = damage / (float(defending_pokemon['STAT_hp']) / 100)

            damage_matrix[row, col] = damage

    """Apply weights if so desired"""

    # TODO play with this!
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
    project_path = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
    filepath = 'results/gen_{:d}_simple.hdf5'.format(__gen__)
    filepath = os.path.join(project_path, filepath)

    if overwrite or not os.path.exists(filepath):
        results = []
        num_processed = 0
    else:
        with pd.HDFStore(filepath, mode='r') as store:
            stored_result = store['result']
            num_processed = stored_result.shape[0]
            results = list(stored_result.values)

    store_data = load_data(__gen__)
    (poketype_chart, poke_dex, attack_dex, pa_junction) = store_data

    col_names = ['pokemon', 'sub_name',
                 'move1', 'move2', 'move3', 'move4',
                 'score']

    for index, pokemon in poke_dex.iterrows():
        # if index < 13:
        #     continue
        # if index > 300:
        #     break

        if not overwrite and index < num_processed:
            continue

        print('processing: %3d/%3d - %s' % (index, poke_dex.shape[0],
                                            pokemon['name']))

        best_combo = _single_pokemon_pokemon(index, store_data)

        cur_result = [pokemon['name'], pokemon['sub_name']] \
                     + best_combo['move_names'] \
                     + [best_combo['score']]

        results.append(cur_result)

        with pd.HDFStore(filepath, mode='a') as store:
            store['result'] = pd.DataFrame(results, columns=col_names)

    return pd.DataFrame(results, columns=col_names)

if __name__ == '__main__':
    # num_attack_poketypes = 4
    # result = poketype_poketype(num_attack_poketypes=num_attack_poketypes)
    # keys = list(result.keys())
    # keys.sort(reverse=True)
    # for key in keys[:2]:
    #     for move_set in result[key]:
    #         print('%5.1f - %s' % (key, move_set))

    __gen__ = 3

    # sorted_moves_per_poketype()

    result = pokemon_pokemon(overwrite=False)

    # result.sort_values(by=['score'], ascending=False)
    # print(result.head())

    result = result[result['sub_name'] == '']
    result = result.reset_index(drop=True)

    # result = result.iloc[:151]

    result = result.sort_values(by=['score'])
    print(result)

