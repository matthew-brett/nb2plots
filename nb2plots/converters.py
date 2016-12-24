""" Convert ReST and doctrees to various formats using nb2plots defaults
"""

from importlib import import_module

from .sphinxutils import Converter


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
to_pxml = NbConverter('pseudoxml')
to_markdown = NbConverter('markdown')
to_py = NbConverter('python')
to_notebook = NbConverter('jupyter')
