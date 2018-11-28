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

def get_name(general_soup):
    "find the row below this entry"
    # TODO write this for stat_soup and take all columns after the furst found

    cell_name = 'English name'

    assert cell_name in str(general_soup), 'The needed cell is not in this ' \
                                           'table'

    general_soup_rows = general_soup.find_all('tr', recursive=False)
    for row_num, row_soup in enumerate(general_soup_rows):
        if cell_name in str(row_soup):
            next_row_soup = general_soup_rows[row_num + 1]

            for col_num, col_content in \
                    enumerate(row_soup.find_all('td', recursive=False)):
                if cell_name in str(col_content):
                    name = next_row_soup.find_all('td',
                                                  recursive=False)[col_num]

                    name = str(name.contents[0].strip())

                    return name

def get_pokemon(nat_no, url):
    # pull the webpage
    try:
        response = requests.get(url)
    except (requests.exceptions.MissingSchema,
            requests.exceptions.ConnectionError) as err:
        raise(err)

    # initialise the pokemon (dictionary)
    pokemon = {'nat_no': nat_no}

    # parse
    soup = BeautifulSoup(response.text, features='lxml')
    general_soup = soup.find('a', attrs={"name": "general"}).parent.next_sibling
    stats_soup = soup.find('a', attrs={"name": "stats"}).parent.next_sibling

    # General
    pokemon['name'] = get_name(general_soup)

    import sys
    sys.exit()
    # TODO CONTINUE HERE

    poketype1, poketype2 = general_td[29:31]
    poketype1, poketype2 = (str(x.find('img')['src'])
                            for x in (poketype1, poketype2))
    poketype1, poketype2 = (re.split('/|\.', x)[-2]
                            for x in (poketype1, poketype2))
    poketype2 = 'None' if poketype2 == 'na' else poketype2

    pokemon['poketype1'] = poketype1
    pokemon['poketype2'] = poketype2

    # Stats
    stats_td = stats_soup.find_all('td')

    pokemon['STAT_hp'] = int(stats_td[9].contents[0])
    pokemon['STAT_attack'] = int(stats_td[10].contents[0])
    pokemon['STAT_defense'] = int(stats_td[11].contents[0])
    pokemon['STAT_sp_attack'] = int(stats_td[12].contents[0])
    pokemon['STAT_sp_defense'] = int(stats_td[13].contents[0])

    return pokemon

def get_poke_dex(gen=1):
    """

    :param gen:
    :return:
    """
    gen = int(gen)
    assert gen >= 1 and gen <= 7

    # TODO this function only works for gen3...
    if gen == 1:
        count = 151
        url = 'https://www.serebii.net/pokedex/%03d.shtml'
    elif gen == 2:
        count = 251
        url = 'https://www.serebii.net/pokedex-gs/%03d.shtml'
    elif gen == 3:
        count = 386
        url = 'https://www.serebii.net/pokedex-rs/%03d.shtml'
    elif gen == 4:
        count = 493
        url = 'https://www.serebii.net/pokedex-dp/%03d.shtml'
    elif gen == 5:
        count = 649
        url = 'https://www.serebii.net/pokedex-bw/%03d.shtml'
    elif gen == 6:
        count = 721
        url = 'https://www.serebii.net/pokedex-xy/%03d.shtml'
    elif gen == 7:
        count = 809
        url = 'https://www.serebii.net/pokedex-sm/%03d.shtml'
    else:
        raise AttributeError

    columns = [
        'nat_no',
        'name',
        'poketype1',
        'poketype2',
        'STAT_hp',
        'STAT_attack',
        'STAT_defense',
        'STAT_sp_attack',
        'STAT_sp_defense'
    ]

    poke_dex = None

    # for nat_no in range(140, count+1):
    for nat_no in [4, 20, 109, 150, 151, 152, 386]:
        pokemon = get_pokemon(nat_no, url % nat_no)
        for key, val in pokemon.items():
            print(key, val)
    #     import sys
    #     sys.exit()
    #
    #     pokemon = np.array([[pokemon[col] for col in columns]])
    #
    #     if poke_dex is None:
    #         poke_dex = pokemon
    #     else:
    #         poke_dex = np.append(poke_dex, pokemon, axis=0)
    #
    #     if nat_no % 20 == 0 or True:
    #         print('Processing: {0} - {1}'.format(*pokemon[0]))
    #
    # project_path = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
    # filepath = os.path.join(project_path,
    #                         'webapp/tables/gen_{:d}.hdf5'.format(gen))
    #
    # with pd.HDFStore(filepath, mode='w') as store:
    #     store['poke_dex'] = pd.DataFrame(poke_dex, columns=columns)

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
    get_poke_dex(gen=3)