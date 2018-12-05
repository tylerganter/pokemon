"""

"""

# Standard library imports
import os

# Third party imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Local application imports
from context import settings
# from formulas import effective_damage

def get_pokemon(pokedex, name, subname=''):
    pokemons = pokedex[(pokedex['name'] == name)]
    return pokemons[(pokemons['subname'] == subname)].iloc[0]

def get_move(attackdex, name):
    return attackdex[attackdex['name'] == name].iloc[0]

def add_ad_score(results):
    # ad_score = results['a_score'] - results['d_score']
    ad_score = results['a_score'] / results['d_score']

    results['ad_score'] = pd.Series(ad_score, index=results.index)

    return results

def add_best_worst(results):
    full_pokemon_names = results['pokemon'] + results['subname']

    # temp = full_pokemon_names[np.argmax(vectors.values, axis=1)].values
    # results['+A name'] = pd.Series(temp, index=results.index)
    # temp = np.max(vectors.values, axis=1)
    # results['+A'] = pd.Series(temp, index=results.index).round(decimals=1)
    temp = full_pokemon_names[np.argmin(vectors.values, axis=1)].values
    results['-A name'] = pd.Series(temp, index=results.index)
    temp = np.min(vectors.values, axis=1)
    results['-A'] = pd.Series(temp, index=results.index).round(decimals=1)
    temp = full_pokemon_names[np.argmax(vectors.values, axis=0)].values
    results['-D name'] = pd.Series(temp, index=results.index)
    temp = np.max(vectors.values, axis=0)
    results['-D'] = pd.Series(temp, index=results.index).round(decimals=1)
    # temp = full_pokemon_names[np.argmin(vectors.values, axis=0)].values
    # results['+D name'] = pd.Series(temp, index=results.index)
    # temp = np.min(vectors.values, axis=0)
    # results['+D'] = pd.Series(temp, index=results.index).round(decimals=1)

    return results

def hist_max_combo_vector(mc_vector, result):
    import matplotlib.pyplot as plt
    bins = np.exp((np.linspace(np.log(min(mc_vector)),
                               np.log(max(mc_vector)), num=30)))
    plt.xscale('log')
    plt.hist(mc_vector, bins=bins)

    title = 'min: {}'.format(np.min(mc_vector))
    title += '\nmax: {}'.format(np.max(mc_vector))
    title += '\nmean: {}'.format(np.mean(mc_vector))
    title += '\nmedian: {}'.format(np.median(mc_vector))
    plt.xlabel(title)

    # plt.title(str(result))
    plt.title(result['pokemon'] + result['subname'])

    plt.show()


if __name__ == '__main__':
    """Settings"""

    # METHOD = 'mean'
    # METHOD = 'median'
    METHOD = 'harmonic_mean'
    # METHOD = 'min'

    settings.init(GEN=3, METHOD=METHOD)

    # number of top pokemon to show
    N = 10

    """Load Data"""

    with pd.HDFStore(settings.result_filepath, mode='r') as store:
        results = store['result']
        vectors = store['vectors']

        temp = results[results['pokemon'] == 'Slaking']
        print(temp)

    # with pd.HDFStore(settings.store_filepath, mode='r') as store:
    #     # poketypes = store['poketypes']
    #     # move_categories = store['move_categories']
    #     poketype_chart = store['poketype_chart']
    #     pokedex = store['pokedex']
    #     attackdex = store['attackdex']
    #     learnsets = store['learnsets']

    """find attack - defense score"""

    results = add_ad_score(results)

    """find best/worst attack and defense values (and pokemon)"""

    results = add_best_worst(results)

    """round"""

    results['a_score'] = results['a_score'].round(decimals=1)
    results['d_score'] = results['d_score'].round(decimals=1)
    results['ad_score'] = results['ad_score'].round(decimals=1)

    """Attack Result"""

    # results = results.sort_values(by=['a_score'], ascending=False)
    # results = results.reset_index(drop=True)
    # print(results.head(n=N))

    """Defense Result"""

    # results = results.sort_values(by=['d_score'])
    # results = results.reset_index(drop=True)
    # print(results.head(n=N))

    """Combined Result"""

    results = results.sort_values(by=['ad_score'], ascending=False)
    results = results.reset_index(drop=True)
    print(results.head(n=N))

    """Histograms"""

    # TODO plot grid matrix with colors
    # sort columns and rows by best/worst attack/defense

    """Grid Image"""

    full_pokemon_names = np.array(results['pokemon'] + results['subname'])

    z = vectors.values
    xticks = full_pokemon_names
    yticks = full_pokemon_names


    # attack_indices = (-np.array(results['a_score'])).argsort()
    # defense_indices = np.array(results['d_score']).argsort()

    attack_indices = defense_indices = (-np.array(results['ad_score'])).argsort()

    z = z[attack_indices, :]
    z = z[:, defense_indices]
    yticks = yticks[attack_indices]
    xticks = xticks[defense_indices]

    z = z[:N,:N]
    z = np.log(z)

    plt.imshow(z, cmap=plt.get_cmap('RdYlGn'))

    plt.xticks(range(z.shape[1]), xticks[:z.shape[1]], rotation=45)
    plt.yticks(range(z.shape[1]), yticks[:z.shape[1]], rotation=45)

    plt.xlabel('Defending Pokemon')
    plt.ylabel('Attacking Pokemon')
    plt.show()

    # TODO histogram ATTACK and DEFENSE
    # for a given pokemon:
    #   attack is a row
    #   defense is a column

    # TODO this is broken because results have been sorted but vectors arent
    # IDX = 0
    # hist_max_combo_vector(vectors.iloc[IDX], results.iloc[IDX])


