import pandas as pd


ALL_POKETYPES = [
    "normal",
    "fire",
    "water",
    "electric",
    "grass",
    "ice",
    "fighting",
    "poison",
    "ground",
    "flying",
    "psychic",
    "bug",
    "rock",
    "ghost",
    "dragon",
    "dark",
    "steel",
    "fairy",
]

MOVE_CATEGORIES = ["physical", "special", "status"]


def get_poketypes(gen: int = 1) -> pd.DataFrame:
    """Poketypes dataframe"""
    if gen == 1:
        poketypes = ALL_POKETYPES[:15]
    elif gen < 6:
        poketypes = ALL_POKETYPES[:17]
    else:
        poketypes = ALL_POKETYPES[:18]

    return pd.DataFrame(poketypes, columns=["poketype"])


def get_move_categories() -> pd.DataFrame:
    """move categories"""
    return pd.DataFrame(MOVE_CATEGORIES, columns=["category"])
