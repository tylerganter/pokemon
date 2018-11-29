import numpy as np
import pandas as pd

gen = 7

filepath = '../tables/gen_{:d}.hdf5'.format(gen)
with pd.HDFStore(filepath, mode='r') as store:
    poke_dex = store['poke_dex']
    attack_dex = store['attack_dex']

print(poke_dex.head())
print(poke_dex.tail())
# print(poke_dex)

print(attack_dex.head())
print(attack_dex.tail())
# print(attack_dex)
