""" Utils for testing notebooks
"""

from nb2plots.ipython_shim import nbf


def assert_nb_equiv(ipynb, expected):
    actual_nb = nbf.reads(ipynb)
    expected_nb = nbf.reads(expected)
    # Ignore different minor versions of Notebook format
    # It does not appear to be possible to request specific minor versions of
    # the Notebook format.
    expected_nb['nbformat_minor'] = actual_nb['nbformat_minor']
    # 'language_info' key seems to have arrived in metadata as a result of
    # nbconvert 5.3.1 -> 5.4.0 (5.4.0 released September 7 2018).  Previously
    # it was empty.
    actual_nb['metadata'].pop('language_info', None)
    assert actual_nb == expected_nb
