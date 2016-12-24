""" Sphinx builders for output formats
"""

from sphinx.builders.text import TextBuilder

from . import doctree2md, doctree2py, doctree2nb


class MarkdownBuilder(TextBuilder):
    name = 'markdown'
    format = 'markdown'
    out_suffix = '.md'
    writer_class = doctree2md.Writer

    def prepare_writing(self, docnames):
        self.writer = self.writer_class(self)


class PythonBuilder(MarkdownBuilder):
    name = 'python'
    out_suffix = '.py'
    writer_class = doctree2py.Writer


class NotebookBuilder(PythonBuilder):
    name = 'jupyter'
    out_suffix = '.ipynb'
    writer_class = doctree2nb.Writer


def setup(app):
    app.add_builder(MarkdownBuilder)
    app.add_builder(PythonBuilder)
    app.add_builder(NotebookBuilder)
