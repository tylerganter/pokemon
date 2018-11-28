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

# TODO
# global __gen__
__gen__ = 1

def from_poketype_chart(attack_poketype, defending_poketypes):
    #TODO
    return 1

def effective_damage(attack, attacking_pokemon=None, defending_pokemon=None):
    """

    :param attack: PokeAttack object
    :param attacking_pokemon: Pokemon object
    :param defending_pokemon: Pokemon object
    :return: the damage value
    """

    """Acquire the necessary values"""

    level = 100

    power = attack.power
    critical_prob = attack.critical_prob
    accuracy = attack.accuracy
    num_turns = attack.num_turns

    if attacking_pokemon is not None:
        # choose attack or special attack stat
        if attack.is_special:
            attack_stat = attacking_pokemon.sp_attack
        else:
            attack_stat = attacking_pokemon.attack

        STAB = attack.poketype in attacking_pokemon.poketypes
    else:
        # defaults
        attack_stat = 100
        STAB = False

    if defending_pokemon is not None:
        if attack.is_special:
            defense_stat = defending_pokemon.sp_defense
        else:
            defense_stat = defending_pokemon.defense

        poketype_effectiveness = \
            from_poketype_chart(attack.poketype, defending_pokemon.poketypes)
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

    # apply accuracy and number of turns
    damage = damage * accuracy / num_turns

    # TODO factor in HP?

    return damage
