"""
initializer common to acquiring and using data

"""

import os

__gen__ = 1

project_path = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]

store_filepath_template = os.path.join(project_path,
                                       'webapp/data/database/gen_{:d}.hdf5')

store_filepath = None # must be initialized in init()

def init(GEN=1):
    global __gen__, store_filepath

    __gen__ = int(GEN)
    assert __gen__ >= 1 and __gen__ <= 7, 'invalid __gen__'

    store_filepath = store_filepath_template.format(__gen__)
