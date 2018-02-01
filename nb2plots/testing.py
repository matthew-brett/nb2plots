""" Utilities for testing
"""

from unittest import TestCase

import numpy as np

from nose.tools import assert_true, assert_equal


def setup_test():
    """ Set numpy print options to "legacy" for new versions of numpy

    If imported into a file, nosetest will run this before any doctests.

    This func
    """
    from distutils.version import LooseVersion

    if LooseVersion(np.__version__) >= LooseVersion('1.14'):
        np.set_printoptions(legacy="1.13")


# Replacement for nose.tools.assert_raises
assert_raises = TestCase().assertRaises
