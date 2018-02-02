""" Test conversion of Sphinx format ReST to Markdown

Test running writer over example files and chosen snippets.
"""
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

from os.path import join as pjoin, exists
from glob import glob

from nb2plots.converters import to_markdown

from nb2plots.testing import DATA_PATH
from nb2plots.testing.convutils import (convert_assert, fcontents,
                                        unsmart_converter)


to_md_safe = unsmart_converter(to_markdown.from_rst)


def assert_conv_equal(rst_str, md_expected):
    convert_assert(rst_str, to_md_safe, md_expected, None)


def test_example_files():
    # test sphinx2md script over all .rst files checking against .smd / .md
    # files
    for rst_fname in glob(pjoin(DATA_PATH, '*.rst')):
        rst_contents = fcontents(rst_fname, 't')
        # Try .smd filename first, otherwise ordinary .md
        md_fname = rst_fname[:-3] + 'smd'
        if not exists(md_fname):
            md_fname = rst_fname[:-3] + 'md'
        md_contents = fcontents(md_fname, 't')
        assert_conv_equal(rst_contents, md_contents)


def test_default_mathdollar():
    # Test mathdollar extension present by default.
    md = to_markdown.from_rst(r'Some text with $a = 1$ math.')
    expected = "Some text with $a = 1$ math.\n"
    assert md == expected
