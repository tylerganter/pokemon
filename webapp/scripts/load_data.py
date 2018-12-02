import pandas as pd

def load_data(gen):
    filepath = '../tables/gen_{:d}.hdf5'.format(gen)

    with pd.HDFStore(filepath, mode='r') as store:
        poketype_chart = store['poketype_chart']
        poke_dex = store['poke_dex']
        attack_dex = store['attack_dex']
        pa_junction = store['pa_junction']

    return poketype_chart, poke_dex, attack_dex, pa_junction

if __name__ == '__main__':
    __gen__ = 3

    poketype_chart, poke_dex, attack_dex, pa_junction = load_data(__gen__)

    print(poketype_chart)

    print(poke_dex.head())
    print(poke_dex.tail())

    print(attack_dex.head())
    print(attack_dex.tail())

    print(pa_junction.head())