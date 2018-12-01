"""

"""

from __future__ import division, print_function
# from __future__ import absolute_import #TODO why doesn't pycharm like this?

import os
import numpy as np
import pandas as pd
from itertools import combinations

from load_data import load_data

def sorted_moves_per_poketype(gen=3):
    """
    compute the effective power of each move and then split by poketype and sort

    :param gen:
    :return: a dictionary where each key is a poketype
            and each value is a dataframe of moves of that poketype
            sorted by effective power
    """
    poketype_chart, poke_dex, attack_dex = load_data(gen=gen)
    poketypes = list(poketype_chart.columns)

    print(list(attack_dex.columns))

    sorted_attacks = {}

    for poketype in poketypes:
        subdex = attack_dex[attack_dex['poketype']==poketype]

        effective_power = attack_dex['power'] * attack_dex['accuracy'] / 100 \
                          * attack_dex['repeat'] / attack_dex['turns_used']

        subdex['effective_power'] = effective_power

        subdex = subdex.sort_values(by=['effective_power'], ascending=False)

        sorted_attacks[poketype] = subdex

    return sorted_attacks

def poketype_poketype(num_attack_poketypes=4, gen=3):
    """
    Best attack poketype (set) for all defense poketypes
    :return:
    """
    poketype_chart, poke_dex, attack_dex = load_data(gen=gen)
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

def pokemon_pokemon():
    # best A pokemon for all D pokemon                4 Attacks & Pokemon, Pokemon
    pass

if __name__ == '__main__':
    # num_attack_poketypes = 4
    # result = poketype_poketype(num_attack_poketypes=num_attack_poketypes)
    # keys = list(result.keys())
    # keys.sort(reverse=True)
    # for key in keys[:2]:
    #     for move_set in result[key]:
    #         print('%5.1f - %s' % (key, move_set))

    sorted_moves_per_poketype()
