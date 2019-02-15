"""

Harmonic Mean Function

"""

import numpy as np

def harmonic_mean(a, axis=None, dtype=None, out=None, keepdims=np._NoValue,
                  P=-1, eps=1e-8):
    """

    :param a, axis, dtype, out, keepdims: refer to numpy.mean()
    :param P: power to raise to (probably don't change)
    :param eps: for numeric stability
    :return:
    """

    a = np.power(a + eps, P)

    # maybe make sure that there are no zeros in 'a'?
    #   (there is currently no guarantee that 'a' >= 0)

    a = np.mean(a, axis=axis, dtype=dtype, out=out, keepdims=keepdims)

    a = np.power(a, 1 / P)

    return a
