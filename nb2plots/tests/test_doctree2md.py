# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
""" Test writer conversions

Test running writer over example files and chosen snippets
"""

import sys
from os.path import join as pjoin
from glob import glob
from functools import partial
from io import TextIOWrapper, BytesIO

import pytest

from docutils import nodes
from docutils.utils import new_document
from docutils.core import publish_string

from nb2plots.doctree2md import (Writer, IndentLevel, validate_heading_levels)

from nb2plots.testing import DATA_PATH
from nb2plots.testing.convutils import (convert_assert, doctree_assert,
                                        fcontents)


def assert_conv_equal(rst_str, md_expected, encoding='utf8'):
    converter = partial(publish_string, writer=Writer())
    convert_assert(rst_str, converter, md_expected, encoding)


def assert_dt_equal(doctree, md_expected):
    doctree_assert(doctree, Writer(), md_expected)


def test_example_files():
    # test rst2md script over all .rst files checking against .md files
    for rst_fname in glob(pjoin(DATA_PATH, '*.rst')):
        rst_contents = fcontents(rst_fname)
        md_fname = rst_fname[:-3] + 'md'
        md_contents = fcontents(md_fname)
        # Skip files containing text "skip".  These are files for which the
        # source ReST is not valid in plain docutils, such as those containing
        # Sphinx directives and roles.
        if md_contents.strip() != b'skip':
            assert_conv_equal(rst_contents, md_contents)


def test_indent_level():
    # Test IndentLevel object
    level = IndentLevel(['foo', 'bar'], 'prefix')
    assert len(level) == 0
    level.append('baz')
    assert len(level) == 1


def test_container():
    # Test container node passed through
    doc = new_document('md-test')
    container = nodes.container()
    doc.append(container)
    container.append(nodes.Text('Boo!'))
    assert_dt_equal(doc, b'Boo!\n')


def test_title_and_section_levels():
    # Docutils promotes the top-level section to a document title, so sections
    # below the title start at level 2.
    assert_conv_equal("""\
Doc Title
=========

Doc Subtitle
------------

Section One
-----------

Subsection
~~~~~~~~~~

Text.
""", b"""\
# Doc Title

## Doc Subtitle

## Section One

### Subsection

Text.
""")


def make_nested_sections(n_levels=6):
    # Make document with nested sections, as Sphinx does (no document title)
    doc = new_document('md-test')
    parent = doc
    for level in range(1, n_levels + 1):
        section = nodes.section()
        section += nodes.title(text='Header {}'.format(level))
        parent += section
        parent = section
    return doc


def test_default_heading_levels():
    # Default 'infer' behaves as 'demote' for doctrees without a document
    # title (and without a Sphinx builder or environment).
    doc = make_nested_sections()
    assert_dt_equal(doc, b"""\
## Header 1

### Header 2

#### Header 3

##### Header 4

###### Header 5

####### Header 6
""")


def test_infer_leaves_non_sphinx_output_unchanged():
    # 'infer' only applies to Sphinx doctrees.  A docutils-style doctree (no
    # Sphinx builder or environment) keeps the 'demote' behavior.
    doc = make_nested_sections()
    doc.settings.nbplot_heading_levels = 'infer'
    assert_dt_equal(doc, b"""\
## Header 1

### Header 2

#### Header 3

##### Header 4

###### Header 5

####### Header 6
""")


def test_infer_multiple_top_sections():
    # 'infer' only applies to Sphinx doctrees.  For docutils output, the
    # DocTitle transform has already run, and headings are unchanged from
    # 'demote'.
    converter = partial(publish_string, writer=Writer(),
                        settings_overrides={
                            'nbplot_heading_levels': 'infer'})
    convert_assert("""\
First
=====

Text.

Second
======

More.
""", converter, b"""\
## First

Text.

## Second

More.
""")


def test_source_heading_levels():
    # 'source' uses the levels implied by the doctree, with a document title
    # at level 1.
    converter = partial(publish_string, writer=Writer(),
                        settings_overrides={'nbplot_heading_levels': 'source'})
    convert_assert("""\
Doc Title
=========

Section One
-----------

Text.
""", converter, b"""\
# Doc Title

## Section One

Text.
""")


def test_source_without_document_title():
    # Without a document title, top-level sections are level 1.
    converter = partial(publish_string, writer=Writer(),
                        settings_overrides={'nbplot_heading_levels': 'source'})
    convert_assert("""\
First
=====

Text.

Second
======

More.
""", converter, b"""\
# First

Text.

# Second

More.
""")


def test_demote_heading_levels():
    # 'demote' adds one level to every heading; this was the behavior before
    # version 0.8.
    converter = partial(publish_string, writer=Writer(),
                        settings_overrides={'nbplot_heading_levels': 'demote'})
    convert_assert("""\
First
=====

Text.

Second
======

More.
""", converter, b"""\
## First

Text.

## Second

More.
""")


def test_validate_heading_levels():
    # Only the three named policies are allowed; integers are rejected.
    for value in ('demote', 'infer', 'source', 'SOURCE'):
        assert validate_heading_levels(None, value, None) == value.lower()
    for value in (1, 'bogus'):
        with pytest.raises(ValueError):
            validate_heading_levels(None, value, None)


def test_snippets():
    assert_conv_equal("Some text", b"Some text\n")
    assert_conv_equal("With *emphasis*", b"With *emphasis*\n")
    assert_conv_equal("That's **strong**", b"That's **strong**\n")
    assert_conv_equal("As ``literal``", b"As `literal`\n")
    assert_conv_equal("To ``defrole``", b"To `defrole`\n")
    assert_conv_equal("Now :math:`a = 1`", b"Now $a = 1$\n")


def test_system_message():
    # This output could surely be improved.
    old_stderr = sys.stderr
    sys.stderr = TextIOWrapper(BytesIO())
    try:
        assert_conv_equal('Text. :bad-role:`.`.  More text.', b"""\
Text. 

```
:bad-role:`.`
```

.  More text.

```
System Message: <string>:, line 1

<string>:1: (ERROR/3) Unknown interpreted text role "bad-role".
```
""")
    finally:
        sys.stderr = old_stderr
