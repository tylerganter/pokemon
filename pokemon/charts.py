import os

import pandas as pd


POKETYPES_FILENAME = "poketypes.csv"
MOVE_CATEGORIES_FILENAME = "move_categories.csv"
POKETYPE_CHART_FILENAME = "poketype_chart.csv"
POKEDEX_FILENAME = "pokedex.csv"
ATTACKDEX_FILENAME = "attackdex.csv"
LEARNSETS_FILENAME = "learnsets.csv"


def load_poketypes(save_dir):
    return pd.read_csv(os.path.join(save_dir, POKETYPES_FILENAME))

def load_move_categories(save_dir):
    return pd.read_csv(os.path.join(save_dir, MOVE_CATEGORIES_FILENAME))

def load_poketype_chart(save_dir):
    return pd.read_csv(os.path.join(save_dir, POKETYPE_CHART_FILENAME))
