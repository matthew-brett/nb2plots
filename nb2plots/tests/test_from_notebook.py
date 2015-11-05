""" Testing from_notebook module
"""

from os.path import dirname, join as pjoin

from ..ipython_shim import nbformat
from ..from_notebook import convert_nb, convert_nb_fname, to_doctests

from nose.tools import (assert_true, assert_false, assert_raises,
                        assert_equal, assert_not_equal)


DATA_PATH = pjoin(dirname(__file__), 'data')

PLT_HDR = "\n.. nbplot::\n\n"


def test_simple_cells():
    v4 = nbformat.v4
    nb = v4.new_notebook()
    # Markdown -> default conversion
    md_cell = v4.new_markdown_cell('# Some text')
    nb['cells'] = [md_cell]
    exp_text = "\nSome text\n=========\n"
    assert_equal(convert_nb(nb), exp_text)
    # Code -> replaced with plot directive / doctest markers
    code_cell = v4.new_code_cell('a = 10')
    nb['cells'] = [code_cell]
    exp_code = PLT_HDR + "    >>> a = 10\n"
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
    exp_mixed_magic = PLT_HDR + "    >>> b = 2\n"
    nb['cells'] = [mixed_magic_code_cell]
    assert_equal(convert_nb(nb), exp_mixed_magic)


def test_to_doctests():
    # Test to_doctests filter
    assert_equal(to_doctests(''), '>>>')
    assert_equal(to_doctests('a = 1'), '>>> a = 1')
    assert_equal(to_doctests('a = 1\nb = 2'), '>>> a = 1\n>>> b = 2')
    assert_equal(to_doctests(
"""
a = 1
for i in (1, 2):
    a += i

    for j in (2, 3):
        a += j

print(a)
for i in (1, 2):

    a += i
print(a)
"""),
""">>>
>>> a = 1
>>> for i in (1, 2):
...     a += i
...
...     for j in (2, 3):
...         a += j
...
>>> print(a)
>>> for i in (1, 2):
...
...     a += i
>>> print(a)
>>>""")


def test_small():
    # Regression tests on small notebook
    nb_fname = pjoin(DATA_PATH, 'small.ipynb')
    rst_fname = pjoin(DATA_PATH, 'small.rst')
    out = convert_nb_fname(nb_fname)
    with open(rst_fname, 'rt') as fobj:
        assert_equal(out + '\n', fobj.read())
