# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
""" Test writer conversions

Test running writer over example files and chosen snippets
"""
from __future__ import (division, print_function, absolute_import,
                        unicode_literals)

from os.path import (dirname, join as pjoin, abspath)
from glob import glob
import difflib

from docutils import nodes
from docutils.io import StringOutput
from docutils.utils import new_document
from docutils.core import publish_string
from docutils.writers.pseudoxml import Writer as PXMLWriter

from ..doctree2md import Writer, IndentLevel

from nose.tools import (assert_true, assert_false, assert_not_equal,
                        assert_equal)

DATA_PATH = abspath(pjoin(dirname(__file__), 'rst_md_files'))

def _fcontents(fname):
    with open(fname, 'rb') as fobj:
        contents = fobj.read()
    return contents


def _diff_strs(first, second):
    # Replicate some of the standard string comparison error message.
    # This is from unittest.TestCase.assertMultiLineEqual
    firstlines = first.splitlines(True)
    secondlines = second.splitlines(True)
    if len(firstlines) == 1 and first.strip('\r\n') == first:
        firstlines = [first + '\n']
        secondlines = [second + '\n']
    return ''.join(difflib.ndiff(firstlines, secondlines))


def assert_conv_equal(rst_str, md_expected):
    md_actual = publish_string(rst_str, writer=Writer())
    if (md_actual == md_expected):
        assert_equal(md_actual, md_expected)
        return
    # Make some useful debugging output
    msg = 'actual, expected not equal:\n' + _diff_strs(md_actual, md_expected)
    pxml = publish_string(rst_str, writer=PXMLWriter())
    msg += '\nwith doctree\n' + pxml
    assert_equal(md_actual, md_expected, msg=msg)


def assert_dt_equal(doctree, md_expected):
    destination = StringOutput(encoding='utf8')
    assert_equal(Writer().write(doctree, destination), md_expected)


def test_example_files():
    # test rst2md script over all .rst files checking against .md files
    for rst_fname in glob(pjoin(DATA_PATH, '*.rst')):
        rst_contents = _fcontents(rst_fname)
        md_fname = rst_fname[:-3] + 'md'
        md_contents = _fcontents(md_fname)
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
    assert_dt_equal(doc, b'Boo!')


def test_snippets():
    assert_conv_equal("Some text", b"Some text\n")
    assert_conv_equal("With *emphasis*", b"With *emphasis*\n")
    assert_conv_equal("That's **strong**", b"That's **strong**\n")
    assert_conv_equal("As ``literal``", b"As `literal`\n")
    assert_conv_equal("To ``defrole``", b"To `defrole`\n")
    assert_conv_equal("Now :math:`a = 1`", b"Now $a = 1$\n")
