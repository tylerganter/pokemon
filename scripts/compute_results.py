from pokemon.best import (
    get_best_move_per_poketype,
    get_best_moves_one_pokemon,
)
from pokemon.pokemondb import PokemonDB


if __name__ == "__main__":
    # METHOD = 'mean'
    # METHOD = 'median'
    METHOD = "harmonic_mean"
    # METHOD = 'min'

    pokedb = PokemonDB(gen=2, out_base_dir="out")

    for nat_no, pokemon in pokedb.pokedex.iterrows():
        # best_moves = get_best_move_per_poketype(pokemon, pokedb)
        # from pprint import pprint
        # pprint(best_moves)

        attacks, damage_vector, attack_score = get_best_moves_one_pokemon(
            pokemon, pokedb
        )

        break

    # for k, v in pokedb.get_sorted_moves_per_poketype().items():
    #     print(k)
    #     print(v)
    #     print()

    # import ipdb; ipdb.set_trace()
    #
    # moves_and_scores, damage_matrix = pokemon_pokemon(
    #     pokedb,
    #     start_idx=0,
    #     end_idx=10,
    # )

    # print(moves_and_scores.head())
    # print(damage_matrix.head())
