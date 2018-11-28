import numpy as np
import pandas as pd

gen = 3

filepath = '../tables/gen_{:d}.hdf5'.format(gen)
with pd.HDFStore(filepath, mode='r') as store:
    poke_dex = store['poke_dex']

print(poke_dex.head())
