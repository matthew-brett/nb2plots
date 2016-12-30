""" Sphinx builders for output formats
"""

from sphinx.builders.text import TextBuilder

from . import doctree2md, doctree2py, doctree2nb


class MarkdownBuilder(TextBuilder):
    name = 'markdown'
    format = 'markdown'
    out_suffix = '.md'
    writer_class = doctree2md.Writer

    def init(self):
        """ Custom initialization of builder, called at end of __init__
        """
        # If None or empty string, do not resolve internal links.  Otherwise,
        # use as base for HTML-style links.  Applies to internal references and
        # download references.
        self.markdown_http_base = (self.config.markdown_http_base
                                   if self.config.markdown_http_base
                                   else None)

    def prepare_writing(self, docnames):
        self.writer = self.writer_class(self)

    def get_target_uri(self, docname, typ=None):
        if self.markdown_http_base:
            return docname + '.html'
        return super(MarkdownBuilder, self).get_target_uri(docname, typ)


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
    # Base URL for Markdown link conversion
    app.add_config_value('markdown_http_base', None, True)
