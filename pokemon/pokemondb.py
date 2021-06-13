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
    def gen(self):
        return self._gen

    @property
    def poketypes(self):
        if not hasattr(self, "_poketypes"):
            self._poketypes = get_poketypes(gen=self.gen)
        return self._poketypes

    @property
    def move_categories(self):
        if not hasattr(self, "_move_categories"):
            self._move_categories = get_move_categories()
        return self._move_categories

    @property
    def poketype_chart(self):
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
    def pokedex(self):
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
    def attackdex(self):
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
    def learnsets(self):
        if not hasattr(self, "_learnsets"):
            filepath = os.path.join(self._save_dir, "learnsets.csv")
            if os.path.isfile(filepath):
                self._learnsets = pd.read_csv(filepath)
            else:
                self._learnsets = scrape_learnsets(
                    pokedex=self.pokedex, attackdex=self.attackdex, gen=self.gen
                )
                os.makedirs(self._save_dir, exist_ok=True)
                self._learnsets.to_csv(filepath, index=False)
            self._learnsets = self._learnsets.set_index(self.attackdex["name"])
        return self._learnsets
