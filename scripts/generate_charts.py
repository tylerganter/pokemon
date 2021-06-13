#!/usr/bin/env python
"""Get basic info for database

Running main will (if selected) acquire
    poketypes           - fire, water, electric, etc.
    move categories     - physical, special or status
    poketype chart      - square matrix of effectiveness
                            (fire does x2 (double damage) to grass, etc)
and write these all to CSV
"""
import argparse
import os

from pokemon.pokemondb import PokemonDB


REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def main(out: str, gens: list):
    for gen in gens:
        pokedb = PokemonDB(gen=gen, out_base_dir=out)

        print(pokedb.poketypes)
        print(pokedb.move_categories)
        print(pokedb.poketype_chart)
        print(pokedb.attackdex)
        print(pokedb.learnsets)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate charts.")
    parser.add_argument(
        "--out", type=str, help="Base directory", default=os.path.join(REPO_DIR, "out")
    )
    parser.add_argument(
        "gens", metavar="N", type=int, nargs="+", help="Poke-gens to process"
    )
    main(**vars(parser.parse_args()))
