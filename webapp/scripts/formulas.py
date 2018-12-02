"""
DummyAttacks - just poketype
DummyPokemon - just single poketype

~~ATTACK~~
    arbitrary # of poketypes
    move
    pokemon (set of moves)

~~DEFENSE~~
    poketype
    pokemon

effective attack strength

best A poketype (set) for all D poketypes       DummyAttack, DummyPokemon
best A poketype (set) for all D pokemon         DummyAttack, Pokemon
best A pokemon for all D poketypes              4 Attacks & Pokemon, DummyPokemon
best A pokemon for all D pokemon                4 Attacks & Pokemon, Pokemon

best D poketype for all A poketypes
best D pokemon  for all A poketypes
best D pokemon for all A pokemon
    (max damage move for A pokemon)

best A pokemon (set?) for all D pokemon

BEST POKEMON:
best average damage given and taken
"""

from __future__ import division

def from_poketype_chart(poketype_chart, attack_poketype, defending_pokemon):
    # TODO find a better solution for this...
    # and also make a solution for gen 1 (dark and steel)
    if defending_pokemon['poketype1'] == 'fairy':
        defending_pokemon['poketype1'] = 'normal'
    if defending_pokemon['poketype2'] == 'fairy':
        defending_pokemon['poketype2'] = ''

    attack_row_index = list(poketype_chart.columns).index(attack_poketype)

    attack_row = poketype_chart.iloc[attack_row_index]

    effectiveness = float(attack_row[defending_pokemon['poketype1']])

    if len(defending_pokemon['poketype2']) > 0:
        effectiveness = effectiveness \
                        * float(attack_row[defending_pokemon['poketype2']])

    return effectiveness

def effective_damage(__gen__, attack, poketype_chart,
                     attacking_pokemon=None, defending_pokemon=None):
    """

    :param attack: PokeAttack object
    :param attacking_pokemon: Pokemon object
    :param defending_pokemon: Pokemon object
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
            attack_stat = float(attacking_pokemon['STAT_attack'])
        elif attack['category'] == 'special':
            attack_stat = float(attacking_pokemon['STAT_sp_attack'])
        else:
            raise AttributeError

        STAB = attack['poketype'] in [attacking_pokemon['poketype1'],
                                      attacking_pokemon['poketype2']]
    else:
        # defaults
        attack_stat = 100
        STAB = False

    if defending_pokemon is not None:
        if attack['category'] == 'physical':
            defense_stat = float(defending_pokemon['STAT_defense'])
        elif attack['category'] == 'special':
            defense_stat = float(defending_pokemon['STAT_sp_defense'])
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

    # apply critical hit probability
    if __gen__ > 5:
        damage = damage * (1 + 0.5 * critical_prob)
    elif __gen__ > 1:
        damage = damage * (1 + 1 * critical_prob)

    # apply same-type attack bonus
    damage = damage * (1 + 0.5 * STAB)

    # apply type effectiveness
    damage = damage * poketype_effectiveness

    # apply accuracy and repeat and number of turns used
    damage = damage * (accuracy / 100) * repeat / turns_used

    return damage
