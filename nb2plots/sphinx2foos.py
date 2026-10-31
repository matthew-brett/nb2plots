""" Sphinx builders for output formats
"""

from pathlib import Path

import sphinx
from docutils.io import StringOutput
from sphinx.builders.text import TextBuilder

from . import doctree2md, doctree2py, doctree2nb


SPHINX_GE_6 = sphinx.version_info[0] >= 6


class MarkdownBuilder(TextBuilder):
    name = 'markdown'
    format = 'markdown'
    out_suffix = '.md'
    writer_class = doctree2md.Writer
    default_translator_class = doctree2md.Translator

    def __init__(self, app, env=None):
        """ Initialize Markdown (and friends) builder
        """
        args = (app, env) if SPHINX_GE_6 else (app,)
        super(MarkdownBuilder, self).__init__(*args)
        # If None or empty string, do not resolve internal links.  Otherwise,
        # use as base for HTML-style links.  Applies to internal references and
        # download references.
        self.markdown_http_base = (self.config.markdown_http_base
                                   if self.config.markdown_http_base
                                   else None)

    def prepare_writing(self, docnames):
        self.writer = self.writer_class(self)

    def write_doc(self, docname, doctree):
        """ Write `doctree` as `docname` using our docutils writer.

        Sphinx 9 changed ``TextBuilder.write_doc`` to use a translator rather
        than the builder's docutils writer, which loses our custom output.
        """
        self.current_docname = docname
        self.secnumbers = self.env.toc_secnumbers.get(docname, {})
        self.writer.write(doctree, StringOutput(encoding='utf-8'))
        out_file_name = Path(self.outdir) / (docname + self.out_suffix)
        out_file_name.parent.mkdir(parents=True, exist_ok=True)
        out_file_name.write_text(self.writer.output, encoding='utf-8')

    def get_target_uri(self, docname, typ=None):
        if self.markdown_http_base:
            return docname + '.html'
        return super(MarkdownBuilder, self).get_target_uri(docname, typ)


class PythonBuilder(MarkdownBuilder):
    name = 'python'
    out_suffix = '.py'
    writer_class = doctree2py.Writer
    default_translator_class = doctree2py.Translator


class NotebookBuilder(PythonBuilder):
    name = 'jupyter'
    out_suffix = '.ipynb'
    writer_class = doctree2nb.Writer
    default_translator_class = doctree2nb.Translator


def setup(app):
    app.add_builder(MarkdownBuilder)
    app.add_builder(PythonBuilder)
    app.add_builder(NotebookBuilder)
    # Base URL for Markdown link conversion
    app.add_config_value('markdown_http_base', None, True)
