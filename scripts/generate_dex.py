#!/usr/bin/env python
"""

Get pokemon info for database

Running main will (if selected) acquire:
    pokedex - list of pokemon with stats
    attackdex - list of attacks with stats
    learnsets - matrix linking pokemon to moves they can learn
and write these all to the HDF5 store

"""
import argparse
import os

import numpy as np
import pandas as pd

from pokemon.charts import (
    POKEDEX_FILENAME,
    ATTACKDEX_FILENAME,
    LEARNSETS_FILENAME,
    load_poketypes,
    load_move_categories,
    load_poketype_chart,
)
from pokemon.web.utils import url_to_soup


REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class PokemonDB:
    # max national number for this gen
    CUTOFFS = [151, 251, 386, 493, 649, 721, 809]

    def __init__(self, gen: int, out_base_dir: str):
        self._gen = gen
        self._save_dir = os.path.join(out_base_dir, f"gen_{gen}")

        self._pokedex = None
        self._attackdex = None
        self._learnsets = None

    @property
    def poketypes(self):
        if not hasattr(self, "_poketypes"):
            self._poketypes = load_poketypes(self._save_dir)
        return self._poketypes

    @property
    def move_categories(self):
        if not hasattr(self, "_move_categories"):
            self._move_categories = load_move_categories(self._save_dir)
        return self._move_categories

    @property
    def poketype_chart(self):
        if not hasattr(self, "_poketype_chart"):
            self._poketype_chart = load_poketype_chart(self._save_dir)
        return self._poketype_chart

    @property
    def pokedex(self):
        return self._pokedex

    def scrape_pokedex(self):
        nat_no_cutoff = self.CUTOFFS[self._gen - 1]

        # url = f"https://pokemondb.net/pokedex/stats/gen{gen}"
        url = "https://pokemondb.net/pokedex/all"
        soup = url_to_soup(url)
        # filepath = '/Users/Tyler/Desktop/POKEMON/all_with_stats.html'
        # soup = file_to_soup(filepath)

        pokedex_soup = soup.find("table", attrs={"id": "pokedex"})

        soup_col_names = [
            row_soup.div.contents[0]
            for row_soup in pokedex_soup.thead.tr.find_all("th", recursive=False)
        ]
        soup_rows = pokedex_soup.tbody.find_all("tr", recursive=False)

        pokedex = []
        col_names = [
            "nat_no",
            "name",
            "subname",
            "urlname",
            "poketypes",
            "hp",
            "attack",
            "defense",
            "sp_attack",
            "sp_defense",
            "speed",
        ]

        for i, row_soup in enumerate(soup_rows):
            pokemon = self._row_to_pokemon_info(row_soup, soup_col_names, col_names)

            if int(pokemon[col_names.index("nat_no")]) > nat_no_cutoff:
                # that's all the pokemon for this gen
                break

            if i % 50 == 0:
                print("Processing: {0} - {1}".format(*pokemon))

            pokemon, use_pokemon = self._filter_pokemon(pokemon)
            if use_pokemon:
                pokedex.append(pokemon)

        self._pokedex = pd.DataFrame(pokedex, columns=col_names)
        self._pokedex = self._pokedex.set_index("nat_no")
        self._pokedex.to_csv(os.path.join(self._save_dir, POKEDEX_FILENAME))

    def scrape_attackdex(self):
        attackdex = []
        col_names = [
            "name",
            "urlname",
            "poketype",
            "category",
            "power",
            "accuracy",
            "repeat",
            "turns_used",
        ]

        for cur_gen in range(1, self._gen + 1):
            url = "https://pokemondb.net/move/generation/{}".format(cur_gen)
            soup = url_to_soup(url)

            attackdex_soup = soup.find("table", attrs={"id": "moves"})

            soup_col_names = [
                row_soup.div.contents[0]
                for row_soup in attackdex_soup.thead.tr.find_all("th", recursive=False)
            ]
            soup_rows = attackdex_soup.tbody.find_all("tr", recursive=False)

            for row_number, row_soup in enumerate(soup_rows):
                move = self._row_to_move_info(row_soup, soup_col_names, col_names)

                if row_number % 20 == 0:
                    print(f"Processing: Gen{cur_gen} - {move[0]}")

                move, use_move = self._filter_move(move)
                if use_move:
                    attackdex.append(move)

        self._attackdex = pd.DataFrame(attackdex, columns=col_names)
        self._attackdex.to_csv(
            os.path.join(self._save_dir, ATTACKDEX_FILENAME), index=False
        )

    def scrape_learnsets(self):
        """
        attack <-> pokemon

        Creates a new DataFrame to be stored in the HDF5 store

        the columns are pokemon and col_name = pokemon name
            note: pokemon names are not necessarily 1-to-1 with the pokedex

        each row is a move in the attackdex
            the rows are 1-to-1 with the attackdex

        """
        if self._pokedex is None:
            raise ValueError("Must scrape pokedex before scraping learn set")

        if self._attackdex is None:
            raise ValueError("Must scrape attackdex before scraping learn set")

        if self._gen == 7:
            url_template = "https://pokemondb.net/pokedex/{}"
        else:
            url_template = "https://pokemondb.net/pokedex/{}/moves/%d" % self._gen

        # pokemon<->attack junction table
        pokemon_names = []
        learn_sets = np.zeros((self._attackdex.shape[0], 0), dtype=bool)

        # for each pokemon
        for i, pokemon in self._pokedex.iterrows():
            # if pokemon['name'] not in ['Bulbasaur', 'Deoxys']:
            #         continue

            full_name = "|".join([pokemon["name"], pokemon["subname"]])

            print(f"processing: {i}/{self._pokedex.shape[0]} - {full_name}")

            learn_set = self._get_learn_set(pokemon, url_template)

            # update the junction table
            pokemon_names.append(full_name)
            temp = np.expand_dims(self._attackdex["name"].isin(learn_set), axis=1)
            learn_sets = np.hstack((learn_sets, temp))

            # if i > 2:
            #     break
            # break

        self._learnsets = pd.DataFrame(learn_sets, columns=pokemon_names)
        self._learnsets.to_csv(
            os.path.join(self._save_dir, LEARNSETS_FILENAME), index=False
        )

    @staticmethod
    def _row_to_pokemon_info(row_soup, soup_col_names, col_names):
        pokemon = [0] * len(col_names)

        for col_name, cell_soup in zip(
            soup_col_names, row_soup.find_all("td", recursive=False)
        ):

            if col_name == "#":
                # national number
                nat_no = cell_soup.find_all("span", recursive=False)[1]
                nat_no = str(nat_no.contents[0])

                pokemon[col_names.index("nat_no")] = nat_no

            elif col_name == "Name":
                name = str(cell_soup.a.contents[0])

                pokemon[col_names.index("name")] = name

                try:
                    sub_name = str(cell_soup.small.contents[0])

                except AttributeError:
                    sub_name = ""

                pokemon[col_names.index("subname")] = sub_name

                url_name = str(cell_soup.a["href"]).split("/")[-1]

                pokemon[col_names.index("urlname")] = url_name

            elif col_name == "Type":
                poketypes = []

                for poketype_soup in cell_soup.find_all("a", recursive=False):
                    poketype = str(poketype_soup.contents[0]).lower()

                    poketypes.append(poketype)

                pokemon[col_names.index("poketypes")] = ";".join(poketypes)

            elif col_name in ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]:
                val = str(cell_soup.contents[0])

                stat_map = {
                    "HP": "hp",
                    "Attack": "attack",
                    "Defense": "defense",
                    "Sp. Atk": "sp_attack",
                    "Sp. Def": "sp_defense",
                    "Speed": "speed",
                }

                pokemon[col_names.index(stat_map[col_name])] = val

            else:
                continue

        # Exceptions...
        if pokemon[col_names.index("name")] in ["Slakoth", "Slaking"]:
            # These guys only attack every other turn...
            pokemon[col_names.index("attack")] = str(
                int(int(pokemon[col_names.index("attack")]) / 2)
            )
            pokemon[col_names.index("sp_attack")] = str(
                int(int(pokemon[col_names.index("sp_attack")]) / 2)
            )

        return pokemon

    def _filter_pokemon(self, pokemon):
        (
            nat_no,
            name,
            subname,
            urlname,
            poketypes,
            hp,
            attack,
            defense,
            sp_attack,
            sp_defense,
            speed,
        ) = pokemon

        poketypes = [pt for pt in poketypes.split(";") if len(pt) > 0]
        stats = (hp, attack, defense, sp_attack, sp_defense, speed)

        # modify the data

        if subname.startswith("Partner"):
            return None, False

        if self._gen <= 6:
            if subname.startswith("Alolan"):
                return None, False

        if self._gen <= 5:
            if subname.startswith("Mega") or subname.startswith("Primal"):
                return None, False

            if "fairy" in poketypes:
                poketypes = [(x if x != "fairy" else "normal") for x in poketypes]
                poketypes = list(set(poketypes))

        if self._gen == 1:
            if "dark" in poketypes or "steel" in poketypes:
                poketypes = [x for x in poketypes if x not in ["dark", "steel"]]

        # check values
        assert int(nat_no) > 0 and int(nat_no) < 1000
        assert len(name) > 0 and len(name) < 20
        assert len(subname) >= 0 and len(subname) < 20
        assert len(urlname) > 0 and len(urlname) < 20
        assert len(poketypes) > 0
        for poketype in poketypes:
            assert poketype in self.poketypes.values
        for stat in stats:
            assert int(stat) > 0 and int(stat) < 300

        pokemon = [
            nat_no,
            name,
            subname,
            urlname,
            ";".join(poketypes),
            hp,
            attack,
            defense,
            sp_attack,
            sp_defense,
            speed,
        ]

        return pokemon, True

    @staticmethod
    def _row_to_move_info(row_soup, soup_col_names, col_names):
        """

        :param row_soup:
        :param soup_col_names:
        :return:
            a list with values:
                name
                poketype
                category    physical or special
                power
                accuracy    out of 100
                repeat      number of times the move hits
                turns_used  number of turns used (e.g. solarbeam, hyperbeam)
        """
        move = [0] * len(col_names)

        for col_name, cell_soup in zip(
            soup_col_names, row_soup.find_all("td", recursive=False)
        ):
            try:
                if col_name == "Name":
                    # get NAME
                    name = str(cell_soup.a.contents[0])

                    move[col_names.index("name")] = name

                    # get URL NAME
                    url_name = str(cell_soup.a["href"]).split("/")[-1]

                    move[col_names.index("urlname")] = url_name

                elif col_name == "Type":
                    poketype = str(cell_soup.a.contents[0]).lower()

                    move[col_names.index("poketype")] = poketype

                elif col_name == "Cat.":
                    # if cell_soup.span is None:
                    #     category = "unknown"
                    # else:
                    #     category = str(cell_soup.span["title"]).lower()

                    category = cell_soup.img.attrs["title"].lower()

                    move[col_names.index("category")] = category

                elif col_name == "Power":
                    power = cell_soup.contents[0]
                    try:
                        power = int(power)

                    except ValueError:
                        power = 0

                    move[col_names.index("power")] = power

                elif col_name == "Acc.":
                    accuracy = cell_soup.contents[0]
                    try:
                        accuracy = int(accuracy)

                    except ValueError:
                        if str(accuracy) == "∞":
                            accuracy = 100
                        else:
                            accuracy = -1

                    move[col_names.index("accuracy")] = accuracy

                elif col_name == "Effect":
                    if len(cell_soup.contents) > 0:
                        effect = str(cell_soup.contents[0])
                    else:
                        effect = ""

                    repeat = 1
                    turns_used = 1

                    if "User must recharge next turn." in effect:
                        turns_used = 2

                    elif (
                        "attacks on second." in effect
                        and "Flies up on first turn" not in effect
                        and "Digs underground on first turn" not in effect
                        and "Springs up on first turn" not in effect
                        and "Dives underwater on first turn" not in effect
                        and "Disappears on first turn" not in effect
                    ):
                        turns_used = 2

                    elif "Hits twice" in effect:
                        repeat = 2

                    elif "Hits 2-5 times" in effect:
                        repeat = 3.5

                    elif "Inflicts damage equal to user's level." in effect:
                        # assume pokemon are all level 100
                        move[col_names.index("power")] = 100

                    elif "This attack never misses." in effect:
                        move[col_names.index("accuracy")] = 100

                    elif "User faints." in effect:
                        # skip suicide moves
                        move[col_names.index("power")] = -1

                    move[col_names.index("repeat")] = repeat
                    move[col_names.index("turns_used")] = turns_used

                else:
                    continue

            except (ValueError, IndexError, TypeError) as err:
                print("Error processing: {}".format(move))
                raise err

        return move

    @staticmethod
    def poketype_is_special(poketype):
        """
        before gen IV the category (physical or special) was determined by
        poketype

        :param poketype:
        :return: boolean True>>special  False>>physical
        """
        if poketype in [
            "normal",
            "fighting",
            "poison",
            "ground",
            "flying",
            "bug",
            "rock",
            "ghost",
            "steel",
        ]:
            return False
        elif poketype in [
            "fire",
            "water",
            "electric",
            "grass",
            "ice",
            "psychic",
            "dragon",
            "dark",
        ]:
            return True
        else:
            raise AttributeError("invalid poketype: %s for GenIII" % poketype)

    def _filter_move(self, move):
        (name, url_name, poketype, category, power, accuracy, repeat, turns_used) = move

        # clean up

        if category == "status":
            # we don't need status moves
            return None, False

        if category == "unknown" or power in [0, -1] or accuracy == -1:
            # there's something funny about this move...skip it
            return None, False

        # GEN specific changes

        if self._gen <= 5:
            poketype = "normal" if poketype == "fairy" else poketype

        if self._gen <= 3:
            assert category in ["physical", "special"]
            category = "special" if self.poketype_is_special(poketype) else "physical"

        if self._gen == 1:
            if poketype in ["dark", "steel"]:
                poketype = "normal"

        # check values
        assert len(name) > 0 and len(name) < 30
        assert len(url_name) > 0 and len(url_name) < 30
        assert poketype in self.poketypes.values, str(move)
        assert category in self.move_categories.values
        assert power > 0 and power < 300, str(move)
        assert accuracy > 0 and accuracy <= 100

        move = [name, url_name, poketype, category, power, accuracy, repeat, turns_used]

        return move, True

    @staticmethod
    def _get_moves_tables_soup(pokemon, url_template):
        url = url_template.format(pokemon["urlname"])

        soup = url_to_soup(url)
        soup = soup.find("div", attrs={"class": "tabset-moves-game"})
        soup = soup.find("div", attrs={"class": "sv-tabs-panel-list"})

        returned_tables_soup = []

        tables_soup = soup.find_all("table", attrs={"class": "data-table"})

        for table_soup in tables_soup:
            # find out how many tab-panels deep this table is
            observed_classes = []
            table_soup_ancestor = table_soup
            while "tabset-moves-game" not in observed_classes:
                table_soup_ancestor = table_soup_ancestor.parent
                observed_classes += list(table_soup_ancestor["class"])

            # if it's more than one, we need to check if this table
            # is applicable to this pokemon sub name
            if observed_classes.count("tabs-panel-list") > 1:
                panel_soup = table_soup.parent.parent

                # get tab name
                href = "#" + str(panel_soup["id"])
                tab_list_soup = panel_soup.parent.parent.find(
                    "div", attrs={"class": "tabs-tab-list"}
                )
                tab_soup = tab_list_soup.find("a", attrs={"href": href})
                tab_name = str(tab_soup.contents[0])

                if (len(pokemon["subname"]) == 0 and tab_name != pokemon["name"]) or (
                    len(pokemon["subname"]) > 0 and tab_name != pokemon["subname"]
                ):
                    # print(pokemon['name']
                    #       + '-' + pokemon['subname']
                    #       + ' ~~~ ' + tab_name)
                    continue

            returned_tables_soup.append(table_soup)

        assert len(returned_tables_soup) > 0

        return returned_tables_soup

    @staticmethod
    def _get_learn_set(pokemon, url_template):
        """the set of moves this pokemon can learn"""
        learn_set = set()

        moves_tables_soup = PokemonDB._get_moves_tables_soup(pokemon, url_template)

        # for each list of moves
        for moves_table_soup in moves_tables_soup:
            thead_cells = moves_table_soup.thead.tr.find_all("th", recursive=False)

            col_names = [str(cell.div.contents[0]) for cell in thead_cells]
            if "Move" not in col_names:
                # this is not a moves list (shouldn't happen)
                continue

            # name of each move in the table
            name_cells = moves_table_soup.find_all("td", attrs={"class": "cell-name"})

            # for each move
            for name_cell in name_cells:
                move_name = str(name_cell.a.contents[0])

                learn_set.add(move_name)

        assert len(learn_set) > 0

        return learn_set


def main(out: str, gens: list):
    for gen in gens:
        pokemon_db = PokemonDB(gen, out_base_dir=out)

        pokemon_db.scrape_pokedex()
        pokemon_db.scrape_attackdex()
        pokemon_db.scrape_learnsets()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate charts.")
    parser.add_argument(
        "--out", type=str, help="Base directory", default=os.path.join(REPO_DIR, "out")
    )
    parser.add_argument(
        "gens", metavar="N", type=int, nargs="+", help="Poke-gens to process"
    )
    main(**vars(parser.parse_args()))
