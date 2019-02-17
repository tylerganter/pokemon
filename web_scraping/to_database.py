#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Example for reading the data from the database

"""

# Standard library imports
import os

# Third party imports
import pandas as pd

REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATASTORE_FILEPATH_TEMPLATE = os.path.join(
    REPO_PATH, 'data/gen_{:d}.hdf5')

if __name__ == '__main__':
    gen = 3

    datastore_filepath = DATASTORE_FILEPATH_TEMPLATE.format(gen)

    with pd.HDFStore(datastore_filepath, mode='r') as store:
        print(store.keys())

        """Basics"""
        print(store['poketypes'])
        # print(store['move_categories'])
        # print(store['poketype_chart'])

        """Large Data Tables"""

        # print(store['pokedex'].head())
        # print(store['attackdex'].head())

        # print(store['learnsets'].head())
        # print(store['learnsets'].tail())

        # print(store['pokedex'].iloc[351])

        """Assign to variables"""

        # poketypes = store['poketypes']
        # move_categories = store['move_categories']
        # poketype_chart = store['poketype_chart']
        # pokedex = store['pokedex']
        # attackdex = store['attackdex']
        # learnsets = store['learnsets']
