""" Testing from_notebook module
"""

from os.path import dirname, join as pjoin

from ..from_notebook import convert_nb, convert_nb_fname

from IPython.nbformat import v4

from nose.tools import (assert_true, assert_false, assert_raises,
                        assert_equal, assert_not_equal)


DATA_PATH = pjoin(dirname(__file__), 'data')

PLT_HDR = "\n.. plot::\n    :context:\n"
PLT_NO_FIGS = PLT_HDR + "    :nofigs:\n\n"
PLT_FIGS = PLT_HDR + "\n"


def test_simple_cells():
    nb = v4.new_notebook()
    # Markdown -> default conversion
    md_cell = v4.new_markdown_cell('# Some text')
    nb['cells'] = [md_cell]
    exp_text = "\nSome text\n=========\n"
    assert_equal(convert_nb(nb), exp_text)
    # Code -> replaced with plot directive / doctest markers
    code_cell = v4.new_code_cell('a = 10')
    nb['cells'] = [code_cell]
    exp_code = PLT_NO_FIGS + "    >>> a = 10\n"
    assert_equal(convert_nb(nb), exp_code)
    # Empty code -> no output
    empty_code_cell = v4.new_code_cell('')
    nb['cells'] = [empty_code_cell]
    exp_empty_code = "\n"
    assert_equal(convert_nb(nb), exp_empty_code)
    # magic lines get stripped
    magic_code_cell = v4.new_code_cell('%timeit a = 1')
    nb['cells'] = [magic_code_cell]
    assert_equal(convert_nb(nb), exp_empty_code)
    # Magic lines stripped from within other code lines
    mixed_magic_code_cell = v4.new_code_cell('%timeit a = 1\nb = 2')
    exp_mixed_magic = PLT_NO_FIGS + "    >>> b = 2\n"
    nb['cells'] = [mixed_magic_code_cell]
    assert_equal(convert_nb(nb), exp_mixed_magic)


def test_small():
    # Regression tests on small notebook
    nb_fname = pjoin(DATA_PATH, 'small.ipynb')
    rst_fname = pjoin(DATA_PATH, 'small.rst')
    out = convert_nb_fname(nb_fname)
    with open(rst_fname, 'rt') as fobj:
        assert_equal(out + '\n', fobj.read())
