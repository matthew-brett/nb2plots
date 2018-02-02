""" Utilities for testing conversion between formats
"""
import difflib

from docutils.core import publish_string
from docutils.writers.pseudoxml import Writer as PXMLWriter
from docutils.io import StringOutput

# Translate inserted smartquote characters back to their original form
_UNSMART_IN = u'\u2019\u201c\u201d\u2026'
_UNSMART_OUT = (u"'", u'"', u'"', u"...")
UNSMART_TABLE = {ord(x): y for x, y in zip(_UNSMART_IN, _UNSMART_OUT)}
_UNSMART_OUT_NB = (u"'", u'\\"', u'\\"', u"...")
UNSMART_TABLE_NB = {ord(x): y for x, y in zip(_UNSMART_IN, _UNSMART_OUT_NB)}


def fcontents(fname, mode='b'):
    with open(fname, 'r' + mode) as fobj:
        contents = fobj.read()
    return contents


def unsmart(in_str):
    # Remove effect of smart quotes
    # See: https://github.com/sphinx-doc/sphinx/issues/3967
    return in_str.translate(UNSMART_TABLE)


def unsmart_nb(in_str):
    # Remove effect of smart quotes in notebook cells
    return in_str.translate(UNSMART_TABLE_NB)


def unsmart_converter(converter, table=None):
    # Decorate function to remove effect of smart quotes.

    def unsmarted(rst_str):
        return unsmart(converter(rst_str))

    return unsmarted


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
        assert actual == expected
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
    assert actual == expected, msg


def doctree_assert(doctree, writer, expected):
    destination = StringOutput(encoding='utf8')
    assert writer.write(doctree, destination) == expected
