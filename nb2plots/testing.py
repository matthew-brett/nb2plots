""" Utilities for testing
"""

import numpy as np


def setup_test():
    """ Set numpy print options to "legacy" for new versions of numpy
    """
    from distutils.version import LooseVersion

    if LooseVersion(np.__version__) >= LooseVersion('1.14'):
        np.set_printoptions(legacy="1.13")
