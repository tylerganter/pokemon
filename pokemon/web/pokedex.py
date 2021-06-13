import pandas as pd

from ..basics import get_poketypes
from .utils import url_to_soup


# max national number for this gen
NAT_NO_CUTOFFS = [151, 251, 386, 493, 649, 721, 809]


def scrape_pokedex(gen: int = 1, verbose=False) -> pd.DataFrame:
    poketypes = get_poketypes(gen=gen)

    nat_no_cutoff = NAT_NO_CUTOFFS[gen - 1]

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
        pokemon = _row_to_pokemon_info(row_soup, soup_col_names, col_names)

        if int(pokemon[col_names.index("nat_no")]) > nat_no_cutoff:
            # that's all the pokemon for this gen
            break

        if verbose and i % 50 == 0:
            print(f"Processing: {pokemon[0]} - {pokemon[1]}")

        pokemon, use_pokemon = _filter_pokemon(pokemon, gen=gen, poketypes=poketypes)
        if use_pokemon:
            pokedex.append(pokemon)

    return pd.DataFrame(pokedex, columns=col_names).set_index("nat_no")


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


def _filter_pokemon(pokemon, gen, poketypes):
    (
        nat_no,
        name,
        subname,
        urlname,
        types,
        hp,
        attack,
        defense,
        sp_attack,
        sp_defense,
        speed,
    ) = pokemon

    types = [pt for pt in types.split(";") if len(pt) > 0]
    stats = (hp, attack, defense, sp_attack, sp_defense, speed)

    # modify the data

    if subname.startswith("Partner"):
        return None, False

    if gen <= 6:
        if subname.startswith("Alolan"):
            return None, False

    if gen <= 5:
        if subname.startswith("Mega") or subname.startswith("Primal"):
            return None, False

        if "fairy" in types:
            types = [(x if x != "fairy" else "normal") for x in types]
            types = list(set(types))

    if gen == 1:
        if "dark" in types or "steel" in types:
            types = [x for x in types if x not in ["dark", "steel"]]

    # check values
    assert int(nat_no) > 0 and int(nat_no) < 1000
    assert len(name) > 0 and len(name) < 20
    assert len(subname) >= 0 and len(subname) < 20
    assert len(urlname) > 0 and len(urlname) < 20
    assert len(types) > 0
    for poketype in types:
        assert poketype in poketypes.values
    for stat in stats:
        assert int(stat) > 0 and int(stat) < 300

    pokemon = [
        nat_no,
        name,
        subname,
        urlname,
        ";".join(types),
        hp,
        attack,
        defense,
        sp_attack,
        sp_defense,
        speed,
    ]

    return pokemon, True
