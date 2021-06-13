import numpy as np
import pandas as pd

from .utils import url_to_soup


def scrape_learnsets(
    pokedex: pd.DataFrame, attackdex: pd.DataFrame, gen: int = 1, verbose=True
) -> pd.DataFrame:
    """
    attack <-> pokemon

    Creates a new DataFrame to be stored in the HDF5 store

    the columns are pokemon and col_name = pokemon name
        note: pokemon names are not necessarily 1-to-1 with the pokedex

    each row is a move in the attackdex
        the rows are 1-to-1 with the attackdex

    """
    if gen == 7:
        url_template = "https://pokemondb.net/pokedex/{}"
    else:
        url_template = "https://pokemondb.net/pokedex/{}/moves/%d" % gen

    # pokemon<->attack junction table
    pokemon_names = []
    learn_sets = np.zeros((attackdex.shape[0], 0), dtype=bool)

    # for each pokemon
    for i, pokemon in pokedex.iterrows():
        # if pokemon['name'] not in ['Bulbasaur', 'Deoxys']:
        #         continue

        full_name = pokemon["name"]
        if pokemon["subname"]:
            full_name += f"|{pokemon['subname']}"

        if verbose and int(i) % 5 == 0:
            print(f"processing: {i}/{pokedex.shape[0]} - {full_name}")

        learn_set = _get_learn_set(pokemon, url_template)

        # update the junction table
        pokemon_names.append(full_name)
        temp = np.expand_dims(attackdex["name"].isin(learn_set), axis=1)
        learn_sets = np.hstack((learn_sets, temp))

    return pd.DataFrame(learn_sets, columns=pokemon_names, dtype=int)


def _get_learn_set(pokemon, url_template):
    """the set of moves this pokemon can learn"""
    learn_set = set()

    moves_tables_soup = _get_moves_tables_soup(pokemon, url_template)

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
