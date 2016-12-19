""" Test conversion of Sphinx format ReST to Python .py files

Test running writer over example files and chosen snippets.
"""
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

from os.path import join as pjoin
from glob import glob

from nb2plots.doctree2py import parse_doctest

from ..converters import to_py

from .convutils import convert_assert, fcontents, DATA_PATH

from nose.tools import assert_equal


def test_doctest_parser():
    assert_equal(parse_doctest('>>> # comment'), '# comment')
    assert_equal(parse_doctest('>>> a = 10'), 'a = 10')
    assert_equal(parse_doctest('   >>> a = 10'), 'a = 10')
    assert_equal(parse_doctest('   >>> a = 10\n   >>> b = 20'),
                 'a = 10\nb = 20')
    assert_equal(parse_doctest(
        '   >>> for i in (1, 2):\n   ...     print(i)'),
        'for i in (1, 2):\n    print(i)')


def assert_conv_equal(rst_str, md_expected):
    convert_assert(rst_str, to_py.from_rst, md_expected, None)


def test_example_files():
    # test conversion code over all .rst files checking against .py files
    for rst_fname in glob(pjoin(DATA_PATH, '*.rst')):
        rst_contents = fcontents(rst_fname, 't')
        py_fname = rst_fname[:-3] + 'py'
        contents = fcontents(py_fname, 't')
        assert_conv_equal(rst_contents, contents)
