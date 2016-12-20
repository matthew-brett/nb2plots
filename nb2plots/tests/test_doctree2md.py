# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
""" Test writer conversions

Test running writer over example files and chosen snippets
"""
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

import sys
from os.path import join as pjoin
from glob import glob
from functools import partial
from io import TextIOWrapper, BytesIO

from docutils import nodes
from docutils.utils import new_document
from docutils.core import publish_string

from ..doctree2md import Writer, IndentLevel

from nose.tools import assert_equal

from .convutils import convert_assert, doctree_assert, fcontents, DATA_PATH


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
    assert_equal(len(level), 0)
    level.append('baz')
    assert_equal(len(level), 1)


def test_container():
    # Test container node passed through
    doc = new_document('md-test')
    container = nodes.container()
    doc.append(container)
    container.append(nodes.Text('Boo!'))
    assert_dt_equal(doc, b'Boo!\n')


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
