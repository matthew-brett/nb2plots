""" Package providing utilities for testing
"""

from os.path import abspath, dirname, join as pjoin

import numpy as np

from sphinxtesters import SourcesBuilder

DATA_PATH = abspath(pjoin(
    dirname(__file__),
    '..',
    'tests',
    'rst_md_files'))


def setup_test():
    """ Set numpy print options to "legacy" for new versions of numpy
    """
    from distutils.version import LooseVersion

    if LooseVersion(np.__version__) >= LooseVersion('1.14'):
        np.set_printoptions(legacy="1.13")


class PlotsBuilder(SourcesBuilder):
    """ Class to build pages with nbplots default extensions

    Used by several test functions.
    """

    conf_source = """\
master_doc = "contents"  # Compatibility with Sphinx 2
extensions = ["nb2plots", "sphinx.ext.doctest"]
"""

def stripeq(actual, expected):
    """ True if LR stripped `actual` equal to LR stripped `expected`
    """
    return actual.strip() == expected.strip()
