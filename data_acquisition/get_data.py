"""

"""

from __future__ import absolute_import, division, print_function

import os
import requests
import re
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

def get_poketypes(gen=1):
    """

    :param gen: generation number
    :return: a list of poketypes
    """
    gen = int(gen)
    assert gen >= 1 and gen <= 7

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

    if gen == 1:
        return poketypes[:15]
    elif gen < 6:
        return poketypes[:17]
    else:
        return poketypes[:18]

def get_poketype_chart(gen=1):
    gen = int(gen)
    assert gen >= 1 and gen <= 7

    # for gen 6-7
    url = 'https://bulbapedia.bulbagarden.net/wiki/Type'
    # for gen 1 and gen 2-5
    url = 'https://bulbapedia.bulbagarden.net/wiki/Type/Type_chart'

    return []

def row_to_pokemon_info(row_soup, soup_col_names):
    """

    :param row_soup:
    :param soup_col_names:
    :return:
        a list with values:
            National Number
            Name
            Sub Name (mega evolution or other, empty otherwise)
            Poketype 1
            Poketype 2 (or empty string)
            HP
            Attack
            Defense
            Sp. Attack
            Sp. Defense

    """

    pokemon = []

    for col_name, cell_soup in zip(soup_col_names,
                                   row_soup.find_all('td', recursive=False)):
        if col_name == '#':
            # national number
            nat_no = cell_soup.find_all('span', recursive=False)[1]
            nat_no = str(nat_no.contents[0])

            assert int(nat_no) > 0 and int(nat_no) < 1000
            pokemon.append(nat_no)

        elif col_name == 'Name':
            name = str(cell_soup.a.contents[0])

            assert len(name) > 0 and len(name) < 20
            pokemon.append(name)

            try:
                sub_name = cell_soup.small.contents[0]

                assert len(sub_name) > 0 and len(sub_name) < 20
                pokemon.append(str(sub_name))

            except AttributeError:
                pokemon.append('')

        elif col_name == 'Type':
            poketype1 = cell_soup.find_all('a', recursive=False)[0]
            poketype1 = str(poketype1.contents[0]).lower()

            # TODO input the correct gen
            assert poketype1 in get_poketypes(gen=7)
            pokemon.append(poketype1)

            if len(cell_soup.find_all('a', recursive=True)) > 1:
                poketype2 = cell_soup.find_all('a', recursive=False)[1]
                poketype2 = str(poketype2.contents[0]).lower()

                # TODO input the correct gen
                assert poketype2 in get_poketypes(gen=7)
            else:
                poketype2 = ''

            pokemon.append(poketype2)

        elif col_name in ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def']:
            val = str(cell_soup.contents[0])

            assert int(val) > 0 and int(val) < 300
            pokemon.append(val)

        else:
            continue

    col_names = [
        'nat_no',
        'name',
        'sub_name',
        'poketype1',
        'poketype2',
        'STAT_hp',
        'STAT_attack',
        'STAT_defense',
        'STAT_sp_attack',
        'STAT_sp_defense'
    ]

    return pokemon, col_names

def get_poke_dex(gen=1):
    """

    :param gen:
    :return:
    """
    gen = int(gen)
    assert gen >= 1 and gen <= 7

    # TODO work this out...
    # url = "https://pokemondb.net/pokedex/all"
    url = "https://pokemondb.net/pokedex/stats/gen{}".format(gen)

    # # pull the webpage
    # try:
    #     response = requests.get(url)
    # except (requests.exceptions.MissingSchema,
    #         requests.exceptions.ConnectionError) as err:
    #     raise(err)
    #
    # # parse
    # soup = BeautifulSoup(response.text, features='lxml')

    # TODO TEMPORARY! replace this
    temp_filepath = '/Users/Tyler/Desktop/POKEMON/all_with_stats.html'
    f = open(temp_filepath)
    soup = BeautifulSoup(f.read(), features='lxml')

    pokedex_soup = soup.find('table', attrs={"id": "pokedex"})

    soup_col_names = []
    for row_soup in pokedex_soup.thead.tr.find_all('th', recursive=False):
        soup_col_names.append(row_soup.div.contents[0])
    # print(soup_col_names)

    poke_dex = None

    for row_number, row_soup in \
            enumerate(pokedex_soup.tbody.find_all('tr', recursive=False)):
        pokemon, col_names = row_to_pokemon_info(row_soup, soup_col_names)

        if row_number % 100 == 0:
            print('Processing: {0} - {1}'.format(*pokemon))

        pokemon = np.array([pokemon])

        if poke_dex is None:
            poke_dex = pokemon
        else:
            poke_dex = np.append(poke_dex, pokemon, axis=0)

    project_path = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
    filepath = os.path.join(project_path,
                            'webapp/tables/gen_{:d}.hdf5'.format(gen))

    with pd.HDFStore(filepath, mode='w') as store:
        store['poke_dex'] = pd.DataFrame(poke_dex, columns=col_names)

def get_attack_dex(gen=1):
    """
    key
    name
    poketype
    power
    accuracy
    number_of_turns
    critical_prob
    is_special (if gen3 use the function)

    :param gen:
    :return:
    """
    def is_special(poketype):
        """

        :param poketype:
        :return: boolean True>>special  False>>physical
        """
        if poketype in ['normal', 'fighting', 'poison', 'ground', 'flying',
                        'bug', 'rock', 'ghost', 'steel']:
            return False
        elif poketype in ['fire', 'water', 'electric', 'grass', 'ice',
                          'psychic',
                          'dragon', 'dark']:
            return True
        else:
            raise AttributeError('invalid poketype: %s for GenIII' % poketype)

    pass

def get_poke_attack_junction(gen=1):
    """
    attack <-> pokemon

    :param gen:
    :return:
    """
    pass

if __name__ == '__main__':
    # "https://pokemondb.net/pokedex/stats/gen1"

    get_poke_dex(gen=3)