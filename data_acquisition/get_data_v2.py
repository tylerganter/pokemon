#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

This is a potential second version of get_data.py

The current version is getting data from pokemondb.net
It is a good site however many of the changes for newer game versions aren't
isolated to their own webpage

"""

# TODO start here...
# use javascript json? or something else? do research to find CLEANEST option
# - looking for completely isolated GENs with pokedex, attackdex and learn sets
# - also flags would be useful; e.g. turns used flag

# Standard library imports
import os
import json

# Third party imports
import numpy as np
import pandas as pd

# Local application imports
import settings
from context import web_utils



# run javascript and export to json
# type_data.js
# pokedex.js
# move_data.js
# https://github.com/Zarel/Pokemon-Showdown/blob/master/data/moves.js
path = '/Users/Tyler/Software_Development/repos/honko-damagecalc/js/data'


"""Smogon Website URLs"""

gen_to_path = ['RB', 'GS', 'RS', 'DP', 'BW', 'XY', 'SM']

# TODO CONTINUE HERE
# shift get_data functions to here using SMOGON
# when getting pokedex: get url per pokemon


def get_json():
    """
    List of pokemon with specific info
        row: pokemon
        col: ...

    :return:
        tuple: DataFrame, name_of_dataframe (string)
    """

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
        col_names = []

        for col_name, cell_soup in zip(soup_col_names,
                                       row_soup.find_all('td',
                                                         recursive=False)):
            if col_name == '#':
                # national number
                nat_no = cell_soup.find_all('span', recursive=False)[1]
                nat_no = str(nat_no.contents[0])

                assert int(nat_no) > 0 and int(nat_no) < 1000
                pokemon.append(nat_no)
                col_names.append('nat_no')

            elif col_name == 'Name':
                name = str(cell_soup.a.contents[0])

                assert len(name) > 0 and len(name) < 20
                pokemon.append(name)
                col_names.append('name')

                try:
                    sub_name = str(cell_soup.small.contents[0])

                    assert len(sub_name) > 0 and len(sub_name) < 20

                except AttributeError:
                    sub_name = ''

                pokemon.append(sub_name)
                col_names.append('sub_name')

            elif col_name == 'Type':
                poketype1 = cell_soup.find_all('a', recursive=False)[0]
                poketype1 = str(poketype1.contents[0]).lower()

                assert poketype1 in get_poketypes()
                pokemon.append(poketype1)
                col_names.append('poketype1')

                if len(cell_soup.find_all('a', recursive=True)) > 1:
                    poketype2 = cell_soup.find_all('a', recursive=False)[1]
                    poketype2 = str(poketype2.contents[0]).lower()

                    assert poketype2 in get_poketypes()
                else:
                    poketype2 = ''

                pokemon.append(poketype2)
                col_names.append('poketype2')

            elif col_name in ['Total', 'HP', 'Attack', 'Defense', 'Sp. Atk',
                              'Sp. Def', 'Speed']:
                val = str(cell_soup.contents[0])

                assert int(val) > 0 and int(val) < 1000
                pokemon.append(val)
                stat_map = {
                    'Total': 'STAT_total',
                    'HP': 'STAT_hp',
                    'Attack': 'STAT_attack',
                    'Defense': 'STAT_defense',
                    'Sp. Atk': 'STAT_sp_attack',
                    'Sp. Def': 'STAT_sp_defense',
                    'Speed': 'STAT_speed'
                }
                col_names.append(stat_map[col_name])

            else:
                continue

        return pokemon, col_names

    def get_json_obj(soup):
        smogon_soup = soup.find('script', attrs={"type": "text/javascript"})
        smogon_json = str(smogon_soup.contents[0]).strip()
        smogon_json = smogon_json[smogon_json.find('{"pokemon":')::]

        try:
            json_obj = json.loads(smogon_json)
        except ValueError as err:
            if str(err).startswith('Extra data: line 1 column'):
                smogon_json = smogon_json[:int(str(err).split()[5]) - 1]

                json_obj = json.loads(smogon_json)
            else:
                raise err

        return json_obj

    base_url = 'https://www.smogon.com/dex/{}'
    base_url = base_url.format(gen_to_path[settings.__gen__ - 1])
    pokedex_url = os.path.join(base_url, 'pokemon')
    attackdex_url = os.path.join(base_url, 'moves')

    soup = web_utils.url_to_soup(pokedex_url)

    # TODO continue here:
    #   test for all gens
    #   is there a different format? more data? for other gens
    #   how to get url_name...
    json_obj = get_json_obj(soup)

    keys = [
        u'abilities',       # doesn't read for some reason
        u'moveflags',       # interesting...
        u'items',
        u'formats',
        u'natures',
        u'moves',           # attackdex
        u'pokemon',         # pokedex
        u'types'            # type chart
    ]

    pokedex_json = json_obj['pokemon']


    pokedex = []
    # skip: nat_no
    col_names = ['name',
                 'poketypes', # joined by ';'
                 'hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed',
                 'abilities', 'url_name']

    pokemon_keys = [u'genfamily', u'evos', u'cap', u'alts', u'name']

    for pokemon_json in pokedex_json:
        alts = pokemon_json['alts'][0]

        pokemon = [
            pokemon_json['name'],
            ';'.join(alts['types']),
            alts['hp'],
            alts['atk'],
            alts['def'],
            alts['spa'],
            alts['spd'],
            alts['spe'],
        ]

        pokedex.append(pokemon)

    asdf = 0


    # for row_number, row_soup in enumerate(soup_rows):
    #     pokemon, col_names = row_to_pokemon_info(row_soup, soup_col_names)
    #
    #     if int(pokemon[col_names.index('nat_no')]) > nat_no_cutoff:
    #         # that's all the pokemon for this gen
    #         break
    #
    #     poke_dex.append(pokemon)
    #
    #     if row_number % 100 == 0:
    #         print('Processing: {0} - {1}'.format(*pokemon))

    return (pd.DataFrame(pokedex, columns=col_names),
            'pokedex')


if __name__ == '__main__':
    # GENS = range(1, 7+1)
    GENS = [3]

    functions = [get_json]
    # functions = []

    # for GEN in range(1, 8):
    for GEN in GENS:
        settings.init(GEN=GEN)

        with pd.HDFStore(settings.store_filepath, mode='a') as store:
            for func in functions:
                df, df_name = func()

                # print(df.head())

                # store[df_name] = df
