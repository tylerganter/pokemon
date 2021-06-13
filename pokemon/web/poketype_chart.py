import numpy as np
import pandas as pd

from ..basics import get_poketypes
from .utils import url_to_soup


def scrape_poketype_chart(gen: int = 1) -> pd.DataFrame:
    """Square matrix of poketype effectiveness
    row: attack type
    col: defense type
    """
    chart_soup = _get_chart_soup(gen=gen)
    poketypes = _get_defense_poketypes(chart_soup, gen=gen)
    poketype_chart = _fill_chart(chart_soup, poketypes)
    return pd.DataFrame(poketype_chart, columns=poketypes)


def _get_chart_soup(gen):
    if gen < 6:
        url = "https://pokemondb.net/type/old"
        soup = url_to_soup(url)
        chart_soup = soup.find_all("table", attrs={"class": "type-table"})
        chart_soup = chart_soup[1] if gen == 1 else chart_soup[0]

    else:
        url = "https://pokemondb.net/type"
        soup = url_to_soup(url)
        chart_soup = soup.find("table", attrs={"class": "type-table"})

    return chart_soup


def _get_defense_poketypes(chart_soup, gen=1):
    poketypes = chart_soup.thead.tr.find_all("th", recursive=False)

    poketypes.pop(0)

    poketypes = [str(poketype.a["title"]).lower() for poketype in poketypes]

    if gen == 1:
        poketypes = poketypes[:15]
    elif gen < 6:
        poketypes = poketypes[:17]

    expected_poketypes = get_poketypes(gen=gen)
    for i, poketype in enumerate(poketypes):
        assert poketype == expected_poketypes.iloc[i]["poketype"]

    return poketypes


def _fill_chart(chart_soup, poketypes):
    poketype_chart = np.ones((len(poketypes), len(poketypes)))

    chart_rows_soup = chart_soup.tbody.find_all("tr", recursive=False)
    chart_rows_soup = chart_rows_soup[: len(poketypes)]

    for i, row_soup in enumerate(chart_rows_soup):
        attack_poketype = str(row_soup.th.a.contents[0]).lower()

        assert attack_poketype == poketypes[i]

        cells_soup = row_soup.find_all("td", recursive=False)

        for j, cell_soup in enumerate(cells_soup):
            if len(cell_soup.contents) > 0:
                effectiveness = str(cell_soup.contents[0])

                if effectiveness == "0":
                    poketype_chart[i, j] = 0
                elif effectiveness == "½":
                    poketype_chart[i, j] = 0.5
                elif effectiveness == "2":
                    poketype_chart[i, j] = 2

    return poketype_chart
