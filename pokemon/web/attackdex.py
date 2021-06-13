import pandas as pd

from ..basics import get_poketypes, get_move_categories
from .utils import url_to_soup


def scrape_attackdex(gen: int = 1, verbose=False) -> pd.DataFrame:
    poketypes = get_poketypes(gen=gen)
    move_categories = get_move_categories()

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

    for cur_gen in range(1, gen + 1):
        url = "https://pokemondb.net/move/generation/{}".format(cur_gen)
        soup = url_to_soup(url)

        attackdex_soup = soup.find("table", attrs={"id": "moves"})

        soup_col_names = [
            row_soup.div.contents[0]
            for row_soup in attackdex_soup.thead.tr.find_all("th", recursive=False)
        ]
        soup_rows = attackdex_soup.tbody.find_all("tr", recursive=False)

        for row_number, row_soup in enumerate(soup_rows):
            move = _row_to_move_info(row_soup, soup_col_names, col_names)

            if verbose and row_number % 20 == 0:
                print(f"Processing: Gen{cur_gen} - {move[0]}")

            move, use_move = _filter_move(move, gen, poketypes, move_categories)
            if use_move:
                attackdex.append(move)

    return pd.DataFrame(attackdex, columns=col_names)


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


def _filter_move(move, gen, poketypes, move_categories):
    (name, url_name, poketype, category, power, accuracy, repeat, turns_used) = move

    # clean up

    if category == "status":
        # we don't need status moves
        return None, False

    if category == "unknown" or power in [0, -1] or accuracy == -1:
        # there's something funny about this move...skip it
        return None, False

    # GEN specific changes

    if gen <= 5:
        poketype = "normal" if poketype == "fairy" else poketype

    if gen <= 3:
        assert category in ["physical", "special"]
        category = "special" if poketype_is_special(poketype) else "physical"

    if gen == 1:
        if poketype in ["dark", "steel"]:
            poketype = "normal"

    # check values
    assert len(name) > 0 and len(name) < 30
    assert len(url_name) > 0 and len(url_name) < 30
    assert poketype in poketypes.values, str(move)
    assert category in move_categories.values
    assert power > 0 and power < 300, str(move)
    assert accuracy > 0 and accuracy <= 100

    move = [name, url_name, poketype, category, power, accuracy, repeat, turns_used]

    return move, True
