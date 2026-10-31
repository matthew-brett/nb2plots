""" Test conversion of Sphinx format ReST to Markdown

Test running writer over example files and chosen snippets.
"""

from os.path import join as pjoin, exists
from glob import glob

from nb2plots.converters import NbConverter, to_markdown

from nb2plots.testing import DATA_PATH
from nb2plots.testing.convutils import (convert_assert, fcontents,
                                        unsmart_converter)


to_md_safe = unsmart_converter(to_markdown.from_rst)

SIX_HEADERS_RST = """\
Header 1
========

Header 2
--------

Header 3
~~~~~~~~

Header 4
^^^^^^^^

Header 5
''''''''

Header 6
++++++++
"""


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


def test_default_infer_heading_levels():
    # Default 'infer' gives heading levels matching the source when there is
    # a single top-level section.
    assert_conv_equal(SIX_HEADERS_RST, """\
# Header 1

## Header 2

### Header 3

#### Header 4

##### Header 5

###### Header 6
""")


def test_demote_heading_levels():
    # 'demote' adds one level to every heading; this was the behavior before
    # version 0.8.
    converter = NbConverter('markdown',
                            conf_txt=NbConverter.default_conf +
                            "\nnbplot_heading_levels = 'demote'\n",
                            status=None)
    convert_assert(SIX_HEADERS_RST, converter.from_rst, """\
## Header 1

### Header 2

#### Header 3

##### Header 4

###### Header 5

####### Header 6
""", encoding=None)


def test_infer_heading_levels():
    # 'infer' gives heading levels matching the source when there is a single
    # top-level section.  See
    # https://github.com/matthew-brett/nb2plots/issues/9
    converter = NbConverter('markdown',
                            conf_txt=NbConverter.default_conf +
                            "\nnbplot_heading_levels = 'infer'\n",
                            status=None)
    convert_assert(SIX_HEADERS_RST, converter.from_rst, """\
# Header 1

## Header 2

### Header 3

#### Header 4

##### Header 5

###### Header 6
""", encoding=None)


def test_infer_multiple_top_sections():
    # No document title and multiple top-level sections: 'infer' uses the
    # docutils title-promotion rule, which cannot promote a title here, so
    # the 'demote' behavior applies without promoting the first section.
    converter = NbConverter('markdown',
                            conf_txt=NbConverter.default_conf +
                            "\nnbplot_heading_levels = 'infer'\n",
                            status=None)
    convert_assert("""\
First
=====

Text.

Second
======

More.
""", converter.from_rst, """\
## First

Text.

## Second

More.
""", encoding=None)


def test_infer_body_text_before_title():
    # Body text before the first section prevents docutils title promotion,
    # so 'infer' demotes headings for this Sphinx doctree.
    converter = NbConverter('markdown',
                            conf_txt=NbConverter.default_conf +
                            "\nnbplot_heading_levels = 'infer'\n",
                            status=None)
    convert_assert("""\
Intro paragraph.

Title
=====

Body.
""", converter.from_rst, """\
Intro paragraph.

## Title

Body.
""", encoding=None)


def test_source_heading_levels():
    # 'source' uses the levels implied by the Sphinx doctree: the first
    # top-level section is level 1.
    converter = NbConverter('markdown',
                            conf_txt=NbConverter.default_conf +
                            "\nnbplot_heading_levels = 'source'\n",
                            status=None)
    convert_assert(SIX_HEADERS_RST, converter.from_rst, """\
# Header 1

## Header 2

### Header 3

#### Header 4

##### Header 5

###### Header 6
""", encoding=None)


def test_source_multiple_top_sections():
    # 'source' leaves multiple top-level sections at level 1.
    converter = NbConverter('markdown',
                            conf_txt=NbConverter.default_conf +
                            "\nnbplot_heading_levels = 'source'\n",
                            status=None)
    convert_assert("""\
First
=====

Text.

Second
======

More.
""", converter.from_rst, """\
# First

Text.

# Second

More.
""", encoding=None)
