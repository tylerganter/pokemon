"""

simple:
    poketypes (list of strings)

Tables:
    poketype_chart
    poke_dex
    attack_dex
    poke_attack_junction
"""

from __future__ import division, print_function
# from __future__ import absolute_import #TODO why doesn't pycharm like this?

import os
import numpy as np
import pandas as pd
import re

from utils import *

# TODO get attack_dex TOTAL and SPEED

def _check_gen():
    global __gen__

    __gen__ = int(__gen__)

    assert __gen__ >= 1 and __gen__ <= 7

def get_poketypes():
    """

    :param gen: generation number
    :return: a list of poketypes
    """
    _check_gen()

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

    # TODO this is temporary, until the correct types for old games are found
    return poketypes[:18]

    if __gen__ == 1:
        return poketypes[:15]
    elif __gen__ < 6:
        return poketypes[:17]
    else:
        return poketypes[:18]

def get_move_categories():
    return ['physical', 'special', 'status']

def get_poketype_chart():
    def get_chart_soup():
        if __gen__ < 6:
            url = 'https://pokemondb.net/type/old'

            soup = url_to_soup(url)

            chart_soup = soup.find_all('table', attrs={"class": "type-table"})

            if __gen__ == 1:
                chart_soup = chart_soup[1]
            else:
                chart_soup = chart_soup[0]

        else:
            url = 'https://pokemondb.net/type'

            soup = url_to_soup(url)

            chart_soup = soup.find('table', attrs={"class": "type-table"})

        return chart_soup

    def get_defense_poketypes(chart_soup):
        poketypes = chart_soup.thead.tr.find_all('th', recursive=False)

        poketypes.pop(0)

        poketypes = [str(poketype.a['title']).lower() for poketype in poketypes]

        for i, poketype in enumerate(poketypes):
            assert poketype == get_poketypes()[i]

        if __gen__ == 1:
            poketypes = poketypes[:15]
        elif __gen__ < 6:
            poketypes = poketypes[:17]

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

    def write_to_store(poketype_chart, col_names):
        project_path = \
            os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
        filepath = os.path.join(project_path,
                                'webapp/tables/gen_{:d}.hdf5'.format(__gen__))

        with pd.HDFStore(filepath, mode='a') as store:
            store['poketype_chart'] = \
                pd.DataFrame(poketype_chart, columns=poketypes)

    _check_gen()

    chart_soup = get_chart_soup()

    poketypes = get_defense_poketypes(chart_soup)

    poketype_chart = fill_chart(chart_soup, poketypes)

    write_to_store(poketype_chart, poketypes)

def get_poke_dex():
    """

    :return:
    """
    def get_col_names(pokedex_soup):
        soup_col_names = []

        for row_soup in pokedex_soup.thead.tr.find_all('th', recursive=False):
            soup_col_names.append(row_soup.div.contents[0])

        return soup_col_names

    def get_soup_rows(pokedex_soup):
        return pokedex_soup.tbody.find_all('tr', recursive=False)

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

            elif col_name in ['HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def']:
                val = str(cell_soup.contents[0])

                assert int(val) > 0 and int(val) < 300
                pokemon.append(val)
                stat_map = {
                    'HP': 'STAT_hp',
                    'Attack': 'STAT_attack',
                    'Defense': 'STAT_defense',
                    'Sp. Atk': 'STAT_sp_attack',
                    'Sp. Def': 'STAT_sp_defense'
                }
                col_names.append(stat_map[col_name])

            else:
                continue

        return pokemon, col_names

    def write_to_store(poke_dex, col_names):
        project_path = \
            os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
        filepath = os.path.join(project_path,
                                'webapp/tables/gen_{:d}.hdf5'.format(__gen__))

        with pd.HDFStore(filepath, mode='a') as store:
            store['poke_dex'] = pd.DataFrame(poke_dex, columns=col_names)

    _check_gen()

    # max national number for this gen
    cutoffs = [151, 251, 386, 493, 649, 721, 809]
    nat_no_cutoff = cutoffs[__gen__ - 1]

    # url = "https://pokemondb.net/pokedex/stats/gen{}".format(__gen__)
    url = 'https://pokemondb.net/pokedex/all'
    soup = url_to_soup(url)

    # filepath = '/Users/Tyler/Desktop/POKEMON/all_with_stats.html'
    # soup = file_to_soup(filepath)

    pokedex_soup = soup.find('table', attrs={"id": "pokedex"})

    soup_col_names = get_col_names(pokedex_soup)
    soup_rows = get_soup_rows(pokedex_soup)

    poke_dex = []

    for row_number, row_soup in enumerate(soup_rows):
        pokemon, col_names = row_to_pokemon_info(row_soup, soup_col_names)

        if int(pokemon[col_names.index('nat_no')]) > nat_no_cutoff:
            # that's all the pokemon for this gen
            break

        poke_dex.append(pokemon)

        if row_number % 100 == 0:
            print('Processing: {0} - {1}'.format(*pokemon))

    write_to_store(poke_dex=poke_dex,
                   col_names=col_names)

def get_attack_dex():
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
    def get_col_names(attackdex_soup):
        soup_col_names = []

        for row_soup in attackdex_soup.thead.tr.find_all('th', recursive=False):
            soup_col_names.append(row_soup.div.contents[0])

        return soup_col_names

    def get_soup_rows(attackdex_soup):
        return attackdex_soup.tbody.find_all('tr', recursive=False)

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

    def row_to_move_info(row_soup, soup_col_names):
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
        move = []
        col_names = []

        for col_name, cell_soup in zip(soup_col_names,
                                       row_soup.find_all('td',
                                                         recursive=False)):
            try:
                if col_name == 'Name':
                    name = str(cell_soup.a.contents[0])

                    assert len(name) > 0 and len(name) < 30
                    move.append(name)
                    col_names.append('name')

                elif col_name == 'Type':
                    poketype = str(cell_soup.a.contents[0]).lower()

                    assert poketype in get_poketypes()
                    move.append(poketype)
                    col_names.append('poketype')

                elif col_name == 'Cat.':
                    if cell_soup.span is None:
                        return None, None

                    category = str(cell_soup.span['title']).lower()

                    assert category in get_move_categories()
                    move.append(category)
                    col_names.append('category')

                    if category == 'status':
                        return None, None

                elif col_name == 'Power':
                    power = cell_soup.contents[0]
                    try:
                        power = int(power)
                        assert power > 0 and power < 300

                    except ValueError:
                        power = -1

                    move.append(power)
                    col_names.append('power')

                elif col_name == 'Acc.':
                    accuracy = cell_soup.contents[0]
                    try:
                        accuracy = int(accuracy)
                        assert accuracy > 0 and accuracy <= 100

                    except ValueError:
                        if str(accuracy) == '∞':
                            accuracy = 100
                        else:
                            accuracy = -1

                    move.append(accuracy)
                    col_names.append('accuracy')

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

                    move.append(repeat)
                    col_names.append('repeat')
                    move.append(turns_used)
                    col_names.append('turns_used')

                else:
                    continue

            except (ValueError, IndexError, TypeError) as err:
                print('Error processing: {}'.format(move))
                raise err
                # return None, None

        if (move[col_names.index('power')] == -1
            or move[col_names.index('accuracy')] == -1):
            return None, None

        return move, col_names

    def write_to_store(attack_dex, col_names):
        project_path = \
            os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
        filepath = os.path.join(project_path,
                                'webapp/tables/gen_{:d}.hdf5'.format(__gen__))

        with pd.HDFStore(filepath, mode='a') as store:
            store['attack_dex'] = pd.DataFrame(attack_dex, columns=col_names)

    _check_gen()

    attack_dex = []

    for CURRENT_GEN in range(1, __gen__ + 1):
        url = 'https://pokemondb.net/move/generation/{}'.format(CURRENT_GEN)
        soup = url_to_soup(url)

        attackdex_soup = soup.find('table', attrs={"id": "moves"})

        soup_col_names = get_col_names(attackdex_soup)
        soup_rows = get_soup_rows(attackdex_soup)

        col_names = None

        for row_number, row_soup in enumerate(soup_rows):
            move, temp_col_names = row_to_move_info(row_soup, soup_col_names)

            if move is None:
                # skip any problem moves
                continue

            if col_names is None:
                col_names = temp_col_names

            if row_number % 20 == 0:
                print('Processing: Gen{} - {}'.format(CURRENT_GEN, move[0]))

            attack_dex.append(move)

    write_to_store(attack_dex=attack_dex,
                   col_names=col_names)

def get_poke_attack_junction():
    """
    attack <-> pokemon

    Creates a new DataFrame to be stored in the HDF5 store

    the columns are pokemon and col_name = pokemon name
        note: pokemon names are not necessarily 1-to-1 with the poke_dex

    each row is a move in the attack_dex
        the rows are 1-to-1 with the attack_dex

    """
    def get_moves_tables_soup(pokemon):
        pokemon_name = pokemon['name']

        if pokemon_name[-1] == '♀':
            pokemon_name = pokemon_name[:-1] + '-f'
        elif pokemon_name[-1] == '♂':
            pokemon_name = pokemon_name[:-1] + '-m'
        elif pokemon_name == 'Mr. Mime':
            pokemon_name = 'mr-mime'
        elif pokemon_name == 'Mime Jr.':
            pokemon_name = 'mime-jr'
        elif pokemon_name in ['Ho-oh', 'Porygon-Z']:
            pass
        else:
            pokemon_name = re.sub(r'\W+', '', pokemon_name)

        url = url_template.format(pokemon_name)
        soup = url_to_soup(url)
        tables_soup = soup.find_all('table', attrs={"class": "data-table"})

        return tables_soup

    def get_learn_set(pokemon):
        """the set of moves this pokemon can learn"""
        learn_set = set()

        moves_tables_soup = get_moves_tables_soup(pokemon)

        # for each list of moves
        for moves_table_soup in moves_tables_soup:
            thead_cells = \
                moves_table_soup.thead.tr.find_all('th', recursive=False)

            col_names = [str(cell.div.contents[0]) for cell in thead_cells]
            if 'Move' not in col_names:
                # this is not a moves list (shouldn't happen)
                continue

            # name of each move in the table
            name_cells = moves_table_soup.find_all('td',
                                                   attrs={"class": "cell-name"})

            # for each move
            for name_cell in name_cells:
                move_name = str(name_cell.a.contents[0])

                learn_set.add(move_name)

        assert len(learn_set) > 0

        return learn_set

    def write_to_store(pa_junction, col_names):
        project_path = \
            os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
        filepath = os.path.join(project_path,
                                'webapp/tables/gen_{:d}.hdf5'.format(__gen__))

        with pd.HDFStore(filepath, mode='a') as store:
            store['pa_junction'] = pd.DataFrame(pa_junction, columns=col_names)

    _check_gen()

    if __gen__ == 7:
        raise NotImplementedError
    else:
        url_template = 'https://pokemondb.net/pokedex/{}/moves/%d' % __gen__

    filepath = '../webapp/tables/gen_{:d}.hdf5'.format(__gen__)

    with pd.HDFStore(filepath, mode='r') as store:
        # poketype_chart = store['poketype_chart']
        poke_dex = store['poke_dex']
        attack_dex = store['attack_dex']

    # pokemon<->attack junction table
    pa_col_names = []
    pa_junction = np.zeros((attack_dex.shape[0], 0), dtype=bool)

    processed = {}

    # for each pokemon
    for index, pokemon in poke_dex.iterrows():
        if pokemon['name'] in processed:
            continue
        else:
            print('processing: %3d/%3d - %s' % (index, poke_dex.shape[0],
                                                pokemon['name']))
            processed[pokemon['name']] = None

        learn_set = get_learn_set(pokemon)

        # update the junction table
        pa_col_names.append(pokemon['name'])
        temp = np.expand_dims(attack_dex['name'].isin(learn_set), axis=1)
        pa_junction = np.hstack((pa_junction, temp))

        # if index > 10:
        #     break

    write_to_store(pa_junction, col_names=pa_col_names)




if __name__ == '__main__':
    __gen__ = 4
    # get_poke_attack_junction()

    # for __gen__ in range(1, 8):
    for __gen__ in range(5, 7):
        # get_poketype_chart()
        # get_poke_dex()
        # get_attack_dex()
        get_poke_attack_junction()
