from functools import lru_cache
import os

import pandas as pd

from .basics import get_poketypes, get_move_categories
from .web import (
    scrape_poketype_chart,
    scrape_pokedex,
    scrape_attackdex,
    scrape_learnsets,
)


class PokemonDB:
    def __init__(self, gen: int, out_base_dir: str):
        self._gen = gen
        self._save_dir = os.path.join(out_base_dir, f"gen_{gen}")

    @property
    def gen(self) -> int:
        return self._gen

    @property
    def poketypes(self) -> pd.DataFrame:
        if not hasattr(self, "_poketypes"):
            self._poketypes = get_poketypes(gen=self.gen)
        return self._poketypes

    @property
    def move_categories(self) -> pd.DataFrame:
        if not hasattr(self, "_move_categories"):
            self._move_categories = get_move_categories()
        return self._move_categories

    @property
    def poketype_chart(self) -> pd.DataFrame:
        if not hasattr(self, "_poketype_chart"):
            filepath = os.path.join(self._save_dir, "poketype_chart.csv")
            if os.path.isfile(filepath):
                self._poketype_chart = pd.read_csv(filepath)
            else:
                self._poketype_chart = scrape_poketype_chart(gen=self.gen)
                os.makedirs(self._save_dir, exist_ok=True)
                self._poketype_chart.to_csv(filepath, index=False)
        return self._poketype_chart

    @property
    def pokedex(self) -> pd.DataFrame:
        if not hasattr(self, "_pokedex"):
            filepath = os.path.join(self._save_dir, "pokedex.csv")
            if os.path.isfile(filepath):
                self._pokedex = pd.read_csv(
                    filepath, index_col=0, converters={"subname": lambda x: str(x)}
                )
            else:
                self._pokedex = scrape_pokedex(gen=self.gen)
                os.makedirs(self._save_dir, exist_ok=True)
                self._pokedex.to_csv(filepath)
        return self._pokedex

    @property
    def attackdex(self) -> pd.DataFrame:
        if not hasattr(self, "_attackdex"):
            filepath = os.path.join(self._save_dir, "attackdex.csv")
            if os.path.isfile(filepath):
                self._attackdex = pd.read_csv(filepath)
            else:
                self._attackdex = scrape_attackdex(gen=self.gen)
                os.makedirs(self._save_dir, exist_ok=True)
                self._attackdex.to_csv(filepath, index=False)
        return self._attackdex

    @property
    def learnsets(self) -> pd.DataFrame:
        if not hasattr(self, "_learnsets"):
            filepath = os.path.join(self._save_dir, "learnsets.csv")
            if os.path.isfile(filepath):
                self._learnsets = pd.read_csv(filepath, dtype=bool)
            else:
                self._learnsets = scrape_learnsets(
                    pokedex=self.pokedex, attackdex=self.attackdex, gen=self.gen
                )
                os.makedirs(self._save_dir, exist_ok=True)
                self._learnsets.astype(int).to_csv(filepath, index=False)
            self._learnsets = self._learnsets.set_index(self.attackdex["name"])
        return self._learnsets

    @lru_cache()
    def get_effective_power(self) -> pd.Series:
        return (
            self.attackdex["power"]
            * self.attackdex["accuracy"]
            / 100
            * self.attackdex["repeat"]
            / self.attackdex["turns_used"]
        )

    @lru_cache()
    def get_sorted_moves_per_poketype(self) -> dict:
        """compute the effective power of each move and then split by poketype and sort

        :param gen:
        :return: a dictionary where each key is a poketype
                and each value is a dataframe of moves of that poketype
                sorted by effective power
        """
        sorted_moves = {}

        for poketype in self.poketypes["poketype"]:
            attackdex = self.attackdex.copy()
            attackdex["effective_power"] = self.get_effective_power()
            subdex = attackdex[self.attackdex["poketype"] == poketype]
            sorted_moves[poketype] = subdex.sort_values(
                by=["effective_power"], ascending=False
            )

        return sorted_moves
