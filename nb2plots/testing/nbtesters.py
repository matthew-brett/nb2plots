""" Utils for testing notebooks
"""

from copy import deepcopy

from nb2plots.ipython_shim import nbf


def rm_ids(nb):
    nb2 = deepcopy(nb)
    for cell in nb2['cells']:
        if 'id' in cell:
            del cell['id']
    return nb2


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
    # 'execution' in cell metadata from nbconvert 6.0
    for cell in actual_nb['cells']:
        if 'execution' in cell['metadata']:
            cell['metadata'].pop('execution')
    assert rm_ids(actual_nb) == rm_ids(expected_nb)
