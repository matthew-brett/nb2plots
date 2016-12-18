""" Convert ReST and doctrees to various formats using nb2plots defaults
"""

from importlib import import_module

from docutils.writers import pseudoxml

from .sphinxutils import Converter
from . import doctree2md, doctree2nb, doctree2py


def can_import(module_str):
    try:
        import_module(module_str)
    except ImportError:
        return False
    return True


DEFAULT_EXTENSIONS = [ext_name for ext_name in
                      ["nb2plots",
                       'sphinx.ext.autodoc',  # to silence math_dollar warning
                       'sphinx.ext.mathjax',  # to enable math output
                       'texext.math_dollar']  # to enable inline dollar syntax
                      if can_import(ext_name)]


DEFAULT_CONF =  """\
extensions = [{}]
""".format(',\n'.join('"{}"'.format(ext_name)
                      for ext_name in DEFAULT_EXTENSIONS))


class NbConverter(Converter):
    default_conf = DEFAULT_CONF


# Some standard converters
to_pxml = NbConverter(pseudoxml.Writer)
to_markdown = NbConverter(doctree2md.Writer)
to_notebook = NbConverter(doctree2nb.Writer)
to_py = NbConverter(doctree2py.Writer)
