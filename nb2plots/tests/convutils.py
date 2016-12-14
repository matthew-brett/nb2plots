""" Utilities for testing conversion between formats
"""
from os.path import (dirname, join as pjoin, abspath)
import difflib

from docutils.core import publish_string
from docutils.writers.pseudoxml import Writer as PXMLWriter
from docutils.io import StringOutput

from nose.tools import assert_equal

DATA_PATH = abspath(pjoin(dirname(__file__), 'rst_md_files'))


def fcontents(fname, mode='b'):
    with open(fname, 'r' + mode) as fobj:
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


def convert_assert(rst_str, converter, expected, encoding='utf8'):
    actual = converter(rst_str)
    if (actual == expected):
        assert_equal(actual, expected)
        return
    # Make some useful debugging output
    if encoding is not None:
        actual = actual.decode(encoding)
        expected = expected.decode(encoding)
    msg = ('actual, expected not equal:\n' +
           _diff_strs(actual, expected))
    pxml = publish_string(rst_str, writer=PXMLWriter())
    msg += '\nwith doctree\n' + pxml.decode(
        'utf8' if encoding is None else encoding)
    assert_equal(actual, expected, msg=msg)


def doctree_assert(doctree, writer, expected):
    destination = StringOutput(encoding='utf8')
    assert_equal(writer.write(doctree, destination), expected)

