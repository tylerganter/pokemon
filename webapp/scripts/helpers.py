"""

"""

import numpy as np
import pandas as pd

import settings


class SingleTon(object):
    __instance = None
    def __new__(cls):
        if SingleTon.__instance is None:
            SingleTon.__instance = object.__new__(cls)
        return SingleTon.__instance

class SortedMoves(SingleTon):
    @property
    def sorted_moves(self):
        if not hasattr(self, '_sorted_moves'):
            self._sorted_moves = self._sorted_moves_per_poketype()

        return self._sorted_moves

    def _sorted_moves_per_poketype(self):
        """
        compute the effective power of each move and then split by poketype and sort

        :param gen:
        :return: a dictionary where each key is a poketype
                and each value is a dataframe of moves of that poketype
                sorted by effective power
        """
        with pd.HDFStore(settings.store_filepath, mode='r') as store:
            poketypes = store['poketypes']
            # move_categories = store['move_categories']
            # poketype_chart = store['poketype_chart']
            # pokedex = store['pokedex']
            attackdex = store['attackdex']
            # learnsets = store['learnsets']

        # compute and set the effective power
        effective_power = attackdex['power'] * attackdex['accuracy'] / 100 \
                          * attackdex['repeat'] / attackdex['turns_used']

        attackdex['effective_power'] = effective_power

        sorted_moves = {}

        for poketype in poketypes['poketype']:
            subdex = attackdex[attackdex['poketype'] == poketype]

            subdex = subdex.sort_values(by=['effective_power'], ascending=False)

            sorted_moves[poketype] = subdex

        return sorted_moves

def from_poketype_chart(poketype_chart, attack_poketype, defending_pokemon):
    attack_row_index = list(poketype_chart.columns).index(attack_poketype)

    attack_row = poketype_chart.iloc[attack_row_index]

    defending_poketypes = [dpt for dpt
                           in defending_pokemon['poketypes'].split(';')
                           if len(dpt) > 0]

    effectiveness = np.product([float(attack_row[dpt])
                                for dpt in defending_poketypes])

    return effectiveness

def effective_damage(attack, poketype_chart,
                     attacking_pokemon=None, defending_pokemon=None):
    """

    :param attack: attack dictionary
    :param attacking_pokemon: Pokemon dictionary
    :param defending_pokemon: Pokemon dictionary
    :return: the damage value
    """

    """Acquire the necessary values"""

    level = 100

    power = float(attack['power'])
    accuracy = float(attack['accuracy'])
    repeat = float(attack['repeat'])
    turns_used = float(attack['turns_used'])

    critical_prob = 0
    # critical_prob = attack.critical_prob  # TODO use this?

    if attacking_pokemon is not None:
        # choose attack or special attack stat
        if attack['category'] == 'physical':
            attack_stat = float(attacking_pokemon['attack'])
        elif attack['category'] == 'special':
            attack_stat = float(attacking_pokemon['sp_attack'])
        else:
            raise AttributeError

        STAB = attack['poketype'] in attacking_pokemon['poketypes'].split(';')
    else:
        # defaults
        attack_stat = 100
        STAB = False

    if defending_pokemon is not None:
        if attack['category'] == 'physical':
            defense_stat = float(defending_pokemon['defense'])
        elif attack['category'] == 'special':
            defense_stat = float(defending_pokemon['sp_defense'])
        else:
            raise AttributeError

        poketype_effectiveness = from_poketype_chart(poketype_chart,
                                                     attack['poketype'],
                                                     defending_pokemon)

    else:
        # defaults
        defense_stat = 100
        poketype_effectiveness = 1

    """Compute damage"""

    # compute the basic damage
    damage = (2 * level / 5 + 2) * power * attack_stat / defense_stat
    damage = damage / 50 + 2

    # simpler but less accurate formula
    # damage = power * attack_stat / defense_stat

    # apply critical hit probability
    if settings.__gen__ > 5:
        damage = damage * (1 + 0.5 * critical_prob)
    elif settings.__gen__ > 1:
        damage = damage * (1 + 1 * critical_prob)

    # apply same-type attack bonus
    damage = damage * (1 + 0.5 * STAB)

    # apply type effectiveness
    damage = damage * poketype_effectiveness

    # apply accuracy and repeat and number of turns used
    damage = damage * (accuracy / 100) * repeat / turns_used

    return damage
