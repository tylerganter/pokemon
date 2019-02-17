#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Get basic info for database

Running main will (if selected) acquire
    poketypes           - fire, water, electric, etc.
    move categories     - physical, special or status
    poketype chart      - square matrix of effectiveness
                            (fire does x2 (double damage) to grass, etc)
and write these all to the HDF5 store

"""

# Standard library imports

# Third party imports
import numpy as np
import pandas as pd

# Local application imports
from context import settings, web_utils


def get_poketypes():
    """
    list of poketypes

    :return:
        tuple: DataFrame, name_of_dataframe (string)

        DataFrame columns=['poketype']
    """

    poketypes = [
        'normal',
        'fire',
        'water',
        'electric',
        'grass',
        'ice',
        'fighting',
        'poison',
        'ground',
        'flying',
        'psychic',
        'bug',
        'rock',
        'ghost',
        'dragon',
        'dark',
        'steel',
        'fairy'
        ]

    if settings.__gen__ == 1:
        poketypes = poketypes[:15]
    elif settings.__gen__ < 6:
        poketypes = poketypes[:17]
    else:
        poketypes = poketypes[:18]

    return (pd.DataFrame(poketypes, columns=['poketype']),
            'poketypes')


def get_move_categories():
    """

    list of move categories

    :return:
        tuple: DataFrame, name_of_dataframe (string)

        DataFrame columns=['category']
    """

    move_categories = ['physical', 'special', 'status']

    return (pd.DataFrame(move_categories, columns=['category']),
            'move_categories')


def get_poketype_chart():
    """
    Square matrix of poketype effectiveness
        row: attack type
        col: defense type

    :return:
        tuple: DataFrame, name_of_dataframe (string)

        DataFrame columns=<list of poketypes>
    """

    def get_chart_soup():
        if settings.__gen__ < 6:
            url = 'https://pokemondb.net/type/old'

            soup = web_utils.url_to_soup(url)

            chart_soup = soup.find_all('table', attrs={"class": "type-table"})

            if settings.__gen__ == 1:
                chart_soup = chart_soup[1]
            else:
                chart_soup = chart_soup[0]

        else:
            url = 'https://pokemondb.net/type'

            soup = web_utils.url_to_soup(url)

            chart_soup = soup.find('table', attrs={"class": "type-table"})

        return chart_soup

    def get_defense_poketypes(chart_soup):
        poketypes = chart_soup.thead.tr.find_all('th', recursive=False)

        poketypes.pop(0)

        poketypes = [str(poketype.a['title']).lower() for poketype in poketypes]

        if settings.__gen__ == 1:
            poketypes = poketypes[:15]
        elif settings.__gen__ < 6:
            poketypes = poketypes[:17]

        for i, poketype in enumerate(poketypes):
            assert poketype == get_poketypes()[0].iloc[i]['poketype']

        return poketypes

    def fill_chart(chart_soup, poketypes):
        poketype_chart = np.ones((len(poketypes), len(poketypes)))

        chart_rows_soup = chart_soup.tbody.find_all('tr', recursive=False)
        chart_rows_soup = chart_rows_soup[:len(poketypes)]

        for i, row_soup in enumerate(chart_rows_soup):
            attack_poketype = str(row_soup.th.a.contents[0]).lower()

            assert attack_poketype == poketypes[i]

            cells_soup = row_soup.find_all('td', recursive=False)

            for j, cell_soup in enumerate(cells_soup):
                if len(cell_soup.contents) > 0:
                    effectiveness = str(cell_soup.contents[0])

                    if effectiveness == '0':
                        poketype_chart[i, j] = 0
                    elif effectiveness == '½':
                        poketype_chart[i, j] = 0.5
                    elif effectiveness == '2':
                        poketype_chart[i, j] = 2

        return poketype_chart

    chart_soup = get_chart_soup()

    poketypes = get_defense_poketypes(chart_soup)

    poketype_chart = fill_chart(chart_soup, poketypes)

    return (pd.DataFrame(poketype_chart, columns=poketypes),
            'poketype_chart')


if __name__ == '__main__':
    # GENS = range(1, 7+1)
    GENS = [1]

    FUNCTIONS = [get_poketypes, get_move_categories, get_poketype_chart]
    # FUNCTIONS = []

    # for GEN in range(1, 8):
    for GEN in GENS:
        settings.init(GEN=GEN)

        with pd.HDFStore(settings.store_filepath, mode='a') as store:
            for func in FUNCTIONS:
                df, df_name = func()

                store[df_name] = df
