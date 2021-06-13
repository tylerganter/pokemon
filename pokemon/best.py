from itertools import combinations

import numpy as np
import pandas as pd

from .dex_exceptions import MOVE_SKIP_LIST
from .pokemondb import PokemonDB


def get_best_move_per_poketype(pokemon: pd.Series, pokedb: PokemonDB) -> dict:
    full_name = pokemon["name"]
    if pokemon["subname"]:
        full_name += f"|{pokemon['subname']}"

    cur_pokemon_moves = pokedb.attackdex[pokedb.learnsets[full_name].values]["name"]

    best_move_per_poketype = {}

    sorted_moves_per_poketype = pokedb.get_sorted_moves_per_poketype()

    for poketype, poketype_moves in sorted_moves_per_poketype.items():
        # moves of specific poketype that this pokemon can learn
        moves = poketype_moves[poketype_moves["name"].isin(cur_pokemon_moves)]

        # omit moves that are on the skip list
        moves = moves[~moves["name"].isin(MOVE_SKIP_LIST)]

        # there are any...
        if moves.shape[0] > 0:
            # save the best one
            best_move_per_poketype[poketype] = moves.iloc[0]

    return best_move_per_poketype


def compute_effective_damage(
    attack: pd.Series,
    pokedb: PokemonDB,
    attacking_pokemon: pd.Series = None,
    defending_pokemon: pd.Series = None,
    gen: int = 1,
    level: int = 100,
    scale_by_hp: bool = True,
):
    power = float(attack["power"])
    accuracy = float(attack["accuracy"])
    repeat = float(attack["repeat"])
    turns_used = float(attack["turns_used"])

    critical_prob = 0
    # critical_prob = attack.critical_prob  # TODO use this?

    if attacking_pokemon is not None:
        # choose attack or special attack stat
        if attack["category"] == "physical":
            attack_stat = float(attacking_pokemon["attack"])
        elif attack["category"] == "special":
            attack_stat = float(attacking_pokemon["sp_attack"])
        else:
            raise AttributeError

        stab = attack["poketype"] in attacking_pokemon["poketypes"].split(";")
    else:
        # defaults
        attack_stat = 100
        stab = False

    if defending_pokemon is not None:
        if attack["category"] == "physical":
            defense_stat = float(defending_pokemon["defense"])
        elif attack["category"] == "special":
            defense_stat = float(defending_pokemon["sp_defense"])
        else:
            raise AttributeError

        poketype_effectiveness = _from_poketype_chart(
            pokedb.poketype_chart, attack["poketype"], defending_pokemon
        )

    else:
        # defaults
        defense_stat = 100
        poketype_effectiveness = 1

    # Compute damage

    # compute the basic damage
    damage = (2 * level / 5 + 2) * power * attack_stat / defense_stat
    damage = damage / 50 + 2

    # simpler but less accurate formula
    # damage = power * attack_stat / defense_stat

    # apply critical hit probability
    if gen > 5:
        damage = damage * (1 + 0.5 * critical_prob)
    elif gen > 1:
        damage = damage * (1 + 1 * critical_prob)

    # apply same-type attack bonus
    damage = damage * (1 + 0.5 * stab)

    # apply type effectiveness
    damage = damage * poketype_effectiveness

    # apply accuracy and repeat and number of turns used
    damage = damage * (accuracy / 100) * repeat / turns_used

    if scale_by_hp:
        # damage is now a ratio of the defending pokemon's health
        damage = damage / (float(defending_pokemon["hp"]) / 100)

    # damage = damage * np.sum([float(defending_pokemon[key])
    #                           for key in ('hp',
    #                                       'attack',
    #                                       'defense',
    #                                       'sp_attack',
    #                                       'sp_defense',
    #                                       'speed')]) / 600

    return damage


def get_best_moves_one_pokemon(
    attacking_pokemon: pd.Series, pokedb: PokemonDB
) -> (pd.Series, np.ndarray, float):
    """

    Returns:
         attacks: the four best attacks for this pokemon to learn
         damage_vector (array): the maximum damage any of the four moves could cause for
            each defending pokemon of shape: (NUM_POKEMON,)
         attack_score: the "score_function()" average of the `damage_vector`
    """
    # Strongest attack of each poketype
    best_move_per_poketype = get_best_move_per_poketype(attacking_pokemon, pokedb)

    poketypes = list(best_move_per_poketype.keys())

    # Fill damage matrix: Attack X Defending pokemon
    damage_matrix = np.zeros((len(best_move_per_poketype), pokedb.pokedex.shape[0]))
    for row, move in enumerate(best_move_per_poketype.values()):
        for col, (_, defending_pokemon) in enumerate(pokedb.pokedex.iterrows()):
            damage_matrix[row, col] = compute_effective_damage(
                move,
                pokedb,
                attacking_pokemon=attacking_pokemon,
                defending_pokemon=defending_pokemon,
                scale_by_hp=True,
            )

    # Find 4 rows that maximize the sum across columns
    best_combo = None
    best_damage_vector = None

    for combo in combinations(range(len(poketypes)), min(len(poketypes), 4)):
        # acquire the subset for this combo of attack types
        combo_matrix = damage_matrix[combo, :]

        # select the max (best) for each attack/defense pair
        max_combo_vector = np.max(combo_matrix, axis=0)

        score = score_function(max_combo_vector)

        if best_combo is None or score > best_combo["a_score"]:
            move_poketypes = [poketypes[i] for i in combo]
            move_names = [
                best_move_per_poketype[poketype]["name"] for poketype in move_poketypes
            ]

            best_combo = {"a_score": score, "move_names": move_names}
            best_damage_vector = max_combo_vector

    attacks = pokedb.attackdex.loc[pokedb.attackdex["name"].isin(best_combo["move_names"])]
    attack_score = best_combo["a_score"]
    damage_vector = np.round(best_damage_vector).astype("int32")

    return attacks, damage_vector, attack_score


def score_function(mc_vector, method="harmonic_mean"):
    """

    :param mc_vector: <# of pokemon> length vector
    :return:
    """

    if method == "min":
        score = min(mc_vector)
    elif method == "mean":
        score = np.mean(mc_vector)
    elif method == "median":
        score = np.median(mc_vector)
    elif method == "harmonic_mean":
        score = harmonic_mean(mc_vector)
    else:
        raise ValueError

    return score


def harmonic_mean(
    a, axis=None, dtype=None, out=None, keepdims=np._NoValue, P=-1, eps=1e-8
):
    """

    :param a, axis, dtype, out, keepdims: refer to numpy.mean()
    :param P: power to raise to (probably don't change)
    :param eps: for numeric stability
    :return:
    """
    a = np.power(a + eps, P)

    # maybe make sure that there are no zeros in 'a'?
    #   (there is currently no guarantee that 'a' >= 0)

    a = np.mean(a, axis=axis, dtype=dtype, out=out, keepdims=keepdims)

    a = np.power(a, 1 / P)

    return a


def _from_poketype_chart(poketype_chart, attack_poketype, defending_pokemon):
    """Compute effectiveness of the attack on the pokemon"""
    attack_row_index = list(poketype_chart.columns).index(attack_poketype)

    attack_row = poketype_chart.iloc[attack_row_index]

    defending_poketypes = [
        dpt for dpt in defending_pokemon["poketypes"].split(";") if len(dpt) > 0
    ]

    effectiveness = np.product([float(attack_row[dpt]) for dpt in defending_poketypes])

    return effectiveness
