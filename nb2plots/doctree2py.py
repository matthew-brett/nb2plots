""" Writer to convert doctree to Python .py file
"""
from __future__ import unicode_literals

from . import doctree2nb as d2nb


class Translator(d2nb.Translator):

    def _init_output(self):
        self._out_lines = []

    def _add_text_block(self, txt):
        self._out_lines += ['# ' + line for line in txt.splitlines()]
        self._out_lines.append('')

    def add_code_block(self, txt):
        self.flush_text()
        self._out_lines += txt.splitlines() + ['']

    def astext(self):
        """ Return the document as a string """
        self.flush_text()
        return '\n'.join(self._out_lines)


class Writer(d2nb.Writer):
    supported = ('python',)
    """Formats this writer supports."""

    def __init__(self):
        d2nb.Writer.__init__(self)
        self.translator_class = Translator
