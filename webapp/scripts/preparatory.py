"""

"""

# Standard library imports
import os
from itertools import combinations

# Third party imports
import numpy as np
import pandas as pd

# Local application imports
from context import settings


def sorted_moves_per_poketype():
    """
    compute the effective power of each move and then split by poketype and sort

    :param gen:
    :return: a dictionary where each key is a poketype
            and each value is a dataframe of moves of that poketype
            sorted by effective power
    """

    with pd.HDFStore(settings.store_filepath, mode='r') as store:
        poketypes = store['poketypes']
        # move_categories = store['move_categories']
        # poketype_chart = store['poketype_chart']
        # pokedex = store['pokedex']
        attackdex = store['attackdex']
        # learnsets = store['learnsets']

    # compute and set the effective power
    effective_power = attackdex['power'] * attackdex['accuracy'] / 100 \
                      * attackdex['repeat'] / attackdex['turns_used']

    attackdex['effective_power'] = effective_power

    sorted_moves = {}

    for poketype in poketypes['poketype']:
        subdex = attackdex[attackdex['poketype'] == poketype]

        subdex = subdex.sort_values(by=['effective_power'], ascending=False)

        sorted_moves[poketype] = subdex

    return sorted_moves
