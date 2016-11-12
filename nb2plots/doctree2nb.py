""" Convert doctree to Jupyter notebook
"""
from __future__ import unicode_literals

import re
from textwrap import dedent

from docutils import nodes

from .to_notebook import nbf
from . import doctree2md as d2m

# The following regular expression comes from Python source file "doctest.py".
# License for that file recorded as:
#
# Released to the public domain 16-Jan-2001, by Tim Peters (tim@python.org).
#
# This regular expression is used to find doctest examples in a
# string.  It defines three groups: `source` is the source code
# (including leading indentation and prompts); `indent` is the
# indentation of the first (PS1) line of the source code; and
# `want` is the expected output (including leading indentation).
_EXAMPLE_RE = re.compile(r'''
    # Source consists of a PS1 line followed by zero or more PS2 lines.
    (?P<source>
        (?:^(?P<indent> [ ]*) >>>    .*)    # PS1 line
        (?:\n           [ ]*  \.\.\. .*)*)  # PS2 lines
    \n?
    # Want consists of any non-blank lines that do not start with PS1.
    (?P<want> (?:(?![ ]*$)    # Not a blank line
                 (?![ ]*>>>)  # Not a line starting with PS1
                 .+$\n?       # But any other line
              )*)
    ''', re.MULTILINE | re.VERBOSE)


def parse_doctest(doctest_txt):
    txt = dedent(doctest_txt.expandtabs())
    parts = []
    for m in _EXAMPLE_RE.finditer(txt):
        indent = len(m.group('indent'))
        source_lines = m.group('source').splitlines()
        source = '\n'.join([L[indent + 4:] for L in source_lines])
        parts.append(source)
    return '\n'.join(parts)


class Translator(d2m.Translator):

    def __init__(self, document):
        d2m.Translator.__init__(self, document)
        self._notebook = nbf.new_notebook()

    def flush_md(self):
        md_txt = d2m.Translator.astext(self).strip()
        if md_txt:
            self._notebook['cells'].append(nbf.new_markdown_cell(md_txt))
        self.reset()

    def astext(self):
        """ Return the document as a string """
        self.flush_md()
        return nbf.writes(self._notebook)

    def visit_doctest_block(self, node):
        self.flush_md()
        doctest_txt = node.astext().strip()
        if doctest_txt:
            parsed = parse_doctest(doctest_txt)
            self._notebook['cells'].append(nbf.new_code_cell(parsed))
        raise nodes.SkipNode


class Writer(d2m.Writer):
    supported = ('jupyter',)
    """Formats this writer supports."""

    output = None
    """Final translated form of `document`."""

    def __init__(self):
        d2m.Writer.__init__(self)
        self.translator_class = Translator
