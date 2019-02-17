"""
initializer common to acquiring and using data

"""

import os

__gen__ = 1
__method__ = 'harmonic_mean'

webapp_path = os.path.abspath(os.path.dirname(__file__))
webapp_path = os.path.abspath(os.path.join(webapp_path, '..'))
store_filepath_template = os.path.join(webapp_path,
                                       'data/database/gen_{:d}.hdf5')
result_filepath_template = os.path.join(webapp_path,
                                        'data/results/gen_{0:d}_{1}.hdf5')

# must be initialized in init()
store_filepath = None
result_filepath = None


def init(GEN=1, METHOD='harmonic_mean'):
    global __gen__, __method__, store_filepath, result_filepath

    __gen__ = int(GEN)
    assert __gen__ >= 1 and __gen__ <= 7, 'invalid __gen__'

    __method__ = str(METHOD)
    assert __method__ in ['mean', 'median', 'harmonic_mean', 'min']

    store_filepath = store_filepath_template.format(__gen__)

    result_filepath = result_filepath_template.format(*[__gen__, __method__])
