"""

"""

# Standard library imports
import os

# Third party imports
import numpy as np
import pandas as pd

# Local application imports
from context import settings


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
    # METHOD = 'mean'
    # METHOD = 'median'
    METHOD = 'harmonic_mean'
    # METHOD = 'min'

    settings.init(GEN=1, METHOD=METHOD)

    with pd.HDFStore(settings.result_filepath, mode='r') as store:
        results = store['result']
        vectors = store['vectors']

    """find best/worst attack and defense values (and pokemon)"""

    # TODO find best/worst attack and defense
    # print(np.argmin(vectors.values, axis=0))
    # print(defense_vector.index[np.argmin(vectors.values, axis=0)])
    # print(defense_vector.index[np.argmax(vectors.values, axis=0)])

    # temp = defense_vector.append(pd.DataFrame(np.max(vectors.values, axis=0)))
    # temp =
    # temp = defense_vector.index[np.argmax(vectors.values, axis=0)]
    # temp = pd.DataFrame(temp, columns=['worst'])

    # temp = temp.append(defense_vector)

    # print(temp.head(n=20))
    # print(pd.DataFrame(defense_vector), )

    # print(results.head())
    # print(results.dtypes)

    # print(defense_vector.head(n=20))
    # print(defense_vector.iloc[120:140])

    """Attack Result"""

    results = results.sort_values(by=['a_score'], ascending=False)
    results = results.reset_index(drop=True)
    print(results.head(n=10))

    """Defense Result"""

    results = results.sort_values(by=['d_score'])
    results = results.reset_index(drop=True)
    print(results.head(n=10))

    """Histograms"""

    # TODO histogram ATTACK and DEFENSE
    # for a given pokemon:
    #   attack is a row
    #   defense is a column

    # TODO this is broken because results have been sorted but vectors arent
    # IDX = 0
    # hist_max_combo_vector(vectors.iloc[IDX], results.iloc[IDX])

    # TODO plot grid matrix with colors
    # sort columns and rows by best/worst attack/defense
