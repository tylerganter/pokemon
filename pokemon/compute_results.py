"""

"""
import os
from itertools import combinations

import numpy as np
import pandas as pd

from .dex_exceptions import ATTACKING_POKEMON_EXCEPTIONS, MOVE_SKIP_LIST
from .helpers import effective_damage
from .pokemondb import PokemonDB


def compute_defense_scores(damage_matrix, method="harmonic_mean"):
    """"""

    defense_matrix = damage_matrix.values

    if method == "min":
        defense_vector = np.max(defense_matrix, axis=0)
    elif method == "mean":
        defense_vector = np.zeros(damage_matrix.shape[1])

        for i in range(len(defense_vector)):
            # skip zeros (situations where the attacker cannot harm the
            # defender) Examples:
            #               Ditto   attacking anyone
            #               Metapod attacking Haunter
            temp = defense_matrix[:, i]
            temp = temp[temp > 0]

            defense_vector[i] = harmonic_mean(temp)

    elif method == "median":
        defense_vector = np.median(defense_matrix, axis=0)
    elif method == "harmonic_mean":
        defense_vector = np.mean(defense_matrix, axis=0)

    else:
        raise ValueError

    return defense_vector


def add_defense_scores(moves_and_scores, damage_matrix):
    defense_scores = compute_defense_scores(damage_matrix)

    moves_and_scores["d_score"] = pd.Series(
        defense_scores, index=moves_and_scores.index, dtype="int32"
    )

    return moves_and_scores


def pokemon_pokemon(pokedb: PokemonDB, start_idx=0, end_idx=np.inf):
    """
    best A pokemon for all D pokemon
      4 Attacks & Pokemon, Pokemon
    """
    # @todo(Tyler) CONTINUE HERE
    #   add the rest of this functionality and test in scripts/compute_results.py

    num_pokemon = pokedb.pokedex.shape[0]

    col_names = ["move1", "move2", "move3", "move4", "a_score", "d_score"]
    moves_and_scores = -1 * np.ones((num_pokemon, len(col_names)), dtype="int32")
    moves_and_scores = pd.DataFrame(moves_and_scores, columns=col_names)

    full_pokemon_names = pokedb.pokedex["name"].copy()
    for i, subname in enumerate(pokedb.pokedex["subname"]):
        if subname:
            full_pokemon_names.iloc[i] = full_pokemon_names.iloc[i] + "-" + subname

    damage_matrix = np.zeros((num_pokemon, num_pokemon), dtype="int32")
    damage_matrix = pd.DataFrame(damage_matrix, columns=full_pokemon_names)

    for i, (nat_no, pokemon) in enumerate(pokedb.pokedex.iterrows()):
        if i < start_idx:
            continue
        if i > end_idx:
            break

        # exceptions...
        if pokemon["name"] in ATTACKING_POKEMON_EXCEPTIONS:
            continue

        print(f"processing: {i}/{num_pokemon} - {damage_matrix.columns[i]}")

        row_moves_and_scores, damage_vector = _single_pokemon_pokemon(pokedb, i)

        # moves_and_scores.iloc[i] = row_moves_and_scores
        # damage_matrix.iloc[i] = damage_vector

    return

    """Add defense scores to results"""

    damage_matrix = damage_matrix.astype("int32")
    moves_and_scores = add_defense_scores(moves_and_scores, damage_matrix).astype(
        "int32"
    )

    """Write the results"""

    with pd.HDFStore(result_filepath, mode="a") as store:
        store["moves_and_scores"] = moves_and_scores
        store["damage_matrix"] = damage_matrix

    return moves_and_scores, damage_matrix
