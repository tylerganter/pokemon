#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Example for reading the data from the database

"""

# Standard library imports

# Third party imports
import pandas as pd

# Local application imports
import settings

if __name__ == '__main__':
    settings.init(GEN=1)

    with pd.HDFStore(settings.store_filepath, mode='r') as store:
        print(store.keys())

        """Basics"""
        # print(store['poketypes'])
        # print(store['move_categories'])
        # print(store['poketype_chart'])

        """Large Data Tables"""

        # print(store['pokedex'].head())
        # print(store['attackdex'].head())

        print(store['learnsets'].head())
        print(store['learnsets'].tail())

        """Assign to variables"""

        # poketypes = store['poketypes']
        # move_categories = store['move_categories']
        # poketype_chart = store['poketype_chart']
        # pokedex = store['pokedex']
        # attackdex = store['attackdex']
        # learnsets = store['learnsets']
