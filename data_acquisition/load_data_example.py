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
        print(store['poketype_chart'])
