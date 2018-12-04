#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""

# Standard library imports
import os
import re

# Third party imports
import numpy as np
import pandas as pd

# Local application imports
import settings
from context import web_utils
from basics import get_poketypes, get_move_categories


def _bad_conditional_solution_POKEMON(pokemon):
    (nat_no, name, subname, urlname, poketypes,
     hp, attack, defense, sp_attack, sp_defense, speed) = pokemon

    poketypes = poketypes.split(';')
    stats = (hp, attack, defense, sp_attack, sp_defense, speed)

    """modify the data"""

    if subname.startswith('Partner'):
        return None, False

    if settings.__gen__ <= 6:
        if subname.startswith('Alolan'):
            return None, False

    if settings.__gen__ <= 5:
        if subname.startswith('Mega'):
            return None, False

        if 'fairy' in poketypes:
            poketypes = [(x if x != 'fairy' else 'normal') for x in poketypes]
            poketypes = list(set(poketypes))

    if settings.__gen__ == 1:
        if 'dark' in poketypes or 'steel' in poketypes:
            poketypes = [x for x in poketypes if x not in ['dark', 'steel']]

    """check values"""

    assert int(nat_no) > 0 and int(nat_no) < 1000
    assert len(name) > 0 and len(name) < 20
    assert len(subname) >= 0 and len(subname) < 20
    assert len(urlname) > 0 and len(urlname) < 20
    assert len(poketypes) > 0
    for poketype in poketypes:
        assert poketype in get_poketypes()[0].values
    for stat in stats:
        assert int(stat) > 0 and int(stat) < 300

    pokemon = [nat_no, name, subname, urlname, ';'.join(poketypes),
               hp, attack, defense, sp_attack, sp_defense, speed]

    return pokemon, True

def _bad_conditional_solution_MOVE(move):
    def is_special(poketype):
        """
        before gen IV the category (physical or special) was determined by
        poketype

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

    (name, url_name, poketype, category,
     power, accuracy, repeat, turns_used) = move

    """clean up"""

    if category == 'status':
        # we don't need status moves
        return None, False

    if (category == 'unknown'
        or power in [0, -1]
        or accuracy == -1):
        # there's something funny about this move...skip it
        return None, False

    """GEN specific changes"""

    if settings.__gen__ <= 5:
        poketype = poketype if poketype != 'fairy' else 'normal'

    if settings.__gen__ <= 3:
        assert category in ['physical', 'special']
        category = 'special' if is_special(poketype) else 'physical'

    if settings.__gen__ == 1:
        if poketype in ['dark', 'steel']:
            poketype = 'normal'

    """check values"""

    assert len(name) > 0 and len(name) < 30
    assert len(url_name) > 0 and len(url_name) < 30
    assert poketype in get_poketypes()[0].values, str(move)
    assert category in get_move_categories()[0].values
    assert power > 0 and power < 300, str(move)
    assert accuracy > 0 and accuracy <= 100

    move = [name, url_name, poketype, category,
            power, accuracy, repeat, turns_used]

    return move, True

def get_pokedex():
    """

    :return:
    """
    def get_col_names(pokedex_soup):
        soup_col_names = []

        for row_soup in pokedex_soup.thead.tr.find_all('th', recursive=False):
            soup_col_names.append(row_soup.div.contents[0])

        return soup_col_names

    def row_to_pokemon_info(row_soup, soup_col_names, col_names):
        """

        """

        pokemon = [0] * len(col_names)

        for col_name, cell_soup in zip(soup_col_names,
                                       row_soup.find_all('td',
                                                         recursive=False)):

            if col_name == '#':
                # national number
                nat_no = cell_soup.find_all('span', recursive=False)[1]
                nat_no = str(nat_no.contents[0])

                pokemon[col_names.index('nat_no')] = nat_no

            elif col_name == 'Name':
                # get NAME
                name = str(cell_soup.a.contents[0])

                pokemon[col_names.index('name')] = name

                # get SUB NAME

                try:
                    sub_name = str(cell_soup.small.contents[0])

                except AttributeError:
                    sub_name = ''

                pokemon[col_names.index('subname')] = sub_name

                # get URL NAME

                url_name = str(cell_soup.a['href']).split('/')[-1]

                pokemon[col_names.index('urlname')] = url_name

            elif col_name == 'Type':
                poketypes = []

                for poketype_soup in cell_soup.find_all('a', recursive=False):
                    poketype = str(poketype_soup.contents[0]).lower()

                    poketypes.append(poketype)

                pokemon[col_names.index('poketypes')] = ';'.join(poketypes)

            elif col_name in ['HP', 'Attack', 'Defense', 'Sp. Atk',
                              'Sp. Def', 'Speed']:
                val = str(cell_soup.contents[0])

                stat_map = {
                    'HP': 'hp',
                    'Attack': 'attack',
                    'Defense': 'defense',
                    'Sp. Atk': 'sp_attack',
                    'Sp. Def': 'sp_defense',
                    'Speed': 'speed'
                }

                pokemon[col_names.index(stat_map[col_name])] = val

            else:
                continue

        return pokemon

    # max national number for this gen
    cutoffs = [151, 251, 386, 493, 649, 721, 809]
    nat_no_cutoff = cutoffs[settings.__gen__ - 1]

    # url = "https://pokemondb.net/pokedex/stats/gen{}".format(__gen__)
    url = 'https://pokemondb.net/pokedex/all'
    soup = web_utils.url_to_soup(url)

    # filepath = '/Users/Tyler/Desktop/POKEMON/all_with_stats.html'
    # soup = file_to_soup(filepath)

    pokedex_soup = soup.find('table', attrs={"id": "pokedex"})

    soup_col_names = get_col_names(pokedex_soup)
    soup_rows = pokedex_soup.tbody.find_all('tr', recursive=False)

    pokedex = []
    col_names = ['nat_no', 'name', 'subname', 'urlname', 'poketypes',
                 'hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']

    for row_number, row_soup in enumerate(soup_rows):
        pokemon = row_to_pokemon_info(row_soup, soup_col_names, col_names)

        if int(pokemon[col_names.index('nat_no')]) > nat_no_cutoff:
            # that's all the pokemon for this gen
            break

        # if row_number % 50 == 0:
        #     print('Processing: {0} - {1}'.format(*pokemon))

        pokemon, use_pokemon = _bad_conditional_solution_POKEMON(pokemon)
        if use_pokemon:
            pokedex.append(pokemon)

    return (pd.DataFrame(pokedex, columns=col_names),
            'pokedex')

def get_attackdex():
    """

    :param gen:
    :return:
    """
    def get_col_names(attackdex_soup):
        soup_col_names = []

        for row_soup in attackdex_soup.thead.tr.find_all('th', recursive=False):
            soup_col_names.append(row_soup.div.contents[0])

        return soup_col_names

    def get_soup_rows(attackdex_soup):
        return attackdex_soup.tbody.find_all('tr', recursive=False)

    def row_to_move_info(row_soup, soup_col_names, col_names):
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

        for col_name, cell_soup in zip(soup_col_names,
                                       row_soup.find_all('td',
                                                         recursive=False)):
            try:
                if col_name == 'Name':
                    # get NAME
                    name = str(cell_soup.a.contents[0])

                    move[col_names.index('name')] = name

                    # get URL NAME
                    url_name = str(cell_soup.a['href']).split('/')[-1]

                    move[col_names.index('urlname')] = url_name

                elif col_name == 'Type':
                    poketype = str(cell_soup.a.contents[0]).lower()

                    move[col_names.index('poketype')] = poketype

                elif col_name == 'Cat.':
                    if cell_soup.span is None:
                        category = 'unknown'
                    else:
                        category = str(cell_soup.span['title']).lower()

                    move[col_names.index('category')] = category

                elif col_name == 'Power':
                    power = cell_soup.contents[0]
                    try:
                        power = int(power)

                    except ValueError:
                        power = 0

                    move[col_names.index('power')] = power

                elif col_name == 'Acc.':
                    accuracy = cell_soup.contents[0]
                    try:
                        accuracy = int(accuracy)

                    except ValueError:
                        if str(accuracy) == '∞':
                            accuracy = 100
                        else:
                            accuracy = -1

                    move[col_names.index('accuracy')] = accuracy

                elif col_name == 'Effect':
                    if len(cell_soup.contents) > 0:
                        effect = str(cell_soup.contents[0])
                    else:
                        effect = ''

                    repeat = 1
                    turns_used = 1

                    if 'User must recharge next turn.' in effect:
                        turns_used = 2

                    elif  ('attacks on second.' in effect
                           and 'Flies up on first turn' not in effect
                           and 'Digs underground on first turn' not in effect
                           and 'Springs up on first turn' not in effect
                           and 'Dives underwater on first turn' not in effect
                           and 'Disappears on first turn' not in effect):
                        turns_used = 2

                    elif 'Hits twice' in effect:
                        repeat = 2

                    elif 'Hits 2-5 times' in effect:
                        repeat = 3.5

                    elif 'Inflicts damage equal to user\'s level.' in effect:
                        # assume pokemon are all level 100
                        move[col_names.index('power')] = 100

                    elif 'This attack never misses.' in effect:
                        move[col_names.index('accuracy')] = 100

                    elif 'User faints.' in effect:
                        # skip suicide moves
                        move[col_names.index('power')] = -1

                    move[col_names.index('repeat')] = repeat
                    move[col_names.index('turns_used')] = turns_used

                else:
                    continue

            except (ValueError, IndexError, TypeError) as err:
                print('Error processing: {}'.format(move))
                raise err

        return move

    attackdex = []
    col_names = ['name', 'urlname', 'poketype', 'category',
                 'power', 'accuracy', 'repeat', 'turns_used']

    for CURRENT_GEN in range(1, settings.__gen__ + 1):
        url = 'https://pokemondb.net/move/generation/{}'.format(CURRENT_GEN)
        soup = web_utils.url_to_soup(url)

        attackdex_soup = soup.find('table', attrs={"id": "moves"})

        soup_col_names = get_col_names(attackdex_soup)
        soup_rows = get_soup_rows(attackdex_soup)

        for row_number, row_soup in enumerate(soup_rows):
            move = row_to_move_info(row_soup, soup_col_names, col_names)

            # if row_number % 20 == 0:
            #     print('Processing: Gen{} - {}'.format(CURRENT_GEN, move[0]))

            move, use_move = _bad_conditional_solution_MOVE(move)
            if use_move:
                attackdex.append(move)

    return (pd.DataFrame(attackdex, columns=col_names),
            'attackdex')

# TODO CONTINUE HERE
def get_learnsets():
    """
    attack <-> pokemon

    Creates a new DataFrame to be stored in the HDF5 store

    the columns are pokemon and col_name = pokemon name
        note: pokemon names are not necessarily 1-to-1 with the pokedex

    each row is a move in the attackdex
        the rows are 1-to-1 with the attackdex

    """
    def get_moves_tables_soup(pokemon, url_template):
        # TODO delete this
        # pokemon_name = pokemon['name']
        #
        # if pokemon_name[-1] == '♀':
        #     pokemon_name = pokemon_name[:-1] + '-f'
        # elif pokemon_name[-1] == '♂':
        #     pokemon_name = pokemon_name[:-1] + '-m'
        # elif pokemon_name == 'Mr. Mime':
        #     pokemon_name = 'mr-mime'
        # elif pokemon_name == 'Mime Jr.':
        #     pokemon_name = 'mime-jr'
        # elif pokemon_name in ['Ho-oh', 'Porygon-Z']:
        #     pass
        # else:
        #     pokemon_name = re.sub(r'\W+', '', pokemon_name)

        url = url_template.format(pokemon['urlname'])

        soup = web_utils.url_to_soup(url)
        tables_soup = soup.find_all('table', attrs={"class": "data-table"})

        return tables_soup

    def get_learn_set(pokemon, url_template):
        """the set of moves this pokemon can learn"""
        learn_set = set()

        moves_tables_soup = get_moves_tables_soup(pokemon, url_template)

        # # for each list of moves
        # for moves_table_soup in moves_tables_soup:
        #     thead_cells = \
        #         moves_table_soup.thead.tr.find_all('th', recursive=False)
        #
        #     col_names = [str(cell.div.contents[0]) for cell in thead_cells]
        #     if 'Move' not in col_names:
        #         # this is not a moves list (shouldn't happen)
        #         continue
        #
        #     # name of each move in the table
        #     name_cells = moves_table_soup.find_all('td',
        #                                            attrs={"class": "cell-name"})
        #
        #     # for each move
        #     for name_cell in name_cells:
        #         move_name = str(name_cell.a.contents[0])
        #
        #         learn_set.add(move_name)
        #
        # assert len(learn_set) > 0

        return learn_set

    if settings.__gen__ == 7:
        raise NotImplementedError
    else:
        url_template = 'https://pokemondb.net/pokedex/{}/moves/%d' \
                       % settings.__gen__

    with pd.HDFStore(settings.store_filepath, mode='r') as store:
        pokedex = store['pokedex']
        attackdex = store['attackdex']

    # pokemon<->attack junction table
    pokemon_names = []
    learn_sets = np.zeros((attackdex.shape[0], 0), dtype=bool)

    # TODO delete this
    # processed = {}

    # for each pokemon
    for index, pokemon in pokedex.iterrows():
        # TODO delete this
        # if pokemon['name'] in processed and False:
        #     continue
        # else:
        #     print('processing: %3d/%3d - %s' % (index, pokedex.shape[0],
        #                                         pokemon['name']))
        #     processed[pokemon['name']] = None

        # TODO
        if pokemon['name'] != 'Wormadam':
            continue

        print('processing: %3d/%3d - %s' % (index, pokedex.shape[0],
                                            pokemon['name']))

        learn_set = get_learn_set(pokemon, url_template)

        # # update the junction table
        # pa_col_names.append(pokemon['name'])
        # temp = np.expand_dims(attackdex['name'].isin(learn_set), axis=1)
        # pa_junction = np.hstack((pa_junction, temp))

        if index > 10 or True:
            break

    return (pd.DataFrame(learn_sets, columns=pokemon_names),
            'learnsets')


if __name__ == '__main__':
    GENS = range(1, 7+1)
    # GENS = [4]

    functions = [get_pokedex, get_attackdex]
    # functions = [get_learnsets]
    # functions = [get_pokedex, get_attackdex, get_learnsets]
    # functions = []

    # for GEN in range(1, 8):
    for GEN in GENS:
        settings.init(GEN=GEN)

        for func in functions:
            print('GEN%d - %s' % (GEN, func.__name__))

            df, df_name = func()

            print(df.head())
            print(df.tail())
            # print(df)

            # with pd.HDFStore(settings.store_filepath, mode='a') as store:
            #     store[df_name] = df
