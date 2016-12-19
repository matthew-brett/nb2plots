""" Convert doctree to Jupyter notebook
"""
from __future__ import unicode_literals

from docutils import nodes

from .ipython_shim import nbf
from . import doctree2py as d2py


class Translator(d2py.Translator):

    def _init_output(self):
        self._notebook = nbf.new_notebook()

    def reset(self):
        d2py.Translator.reset(self)
        self._in_nbplot = False

    def _add_text_block(self, txt):
        self._notebook['cells'].append(nbf.new_markdown_cell(txt))

    def astext(self):
        """ Return the document as a string """
        self.flush_text()
        return nbf.writes(self._notebook)

    def add_code_block(self, txt):
        self.flush_text()
        self._notebook['cells'].append(nbf.new_code_cell(txt))

    def visit_mpl_hint(self, node):
        self.add_code_block('%matplotlib inline')
        raise nodes.SkipNode


class Writer(d2py.Writer):
    supported = ('jupyter',)
    """Formats this writer supports."""

    def __init__(self):
        d2py.Writer.__init__(self)
        self.translator_class = Translator
