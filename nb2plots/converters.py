""" Convert ReST and doctrees to various formats using nb2plots defaults
"""

import sys
from os.path import join as pjoin
from importlib import import_module

from docutils.io import Output

from sphinxtesters import TempApp


class UnicodeOutput(Output):
    """ Don't do anything to the string; just return it.
    """

    default_destination_path = '<string>'

    def write(self, data):
        """ Store `data` in `self.destination`, and return it."""
        self.destination = data
        return data


class Converter(object):
    """ Class to convert from ReST or doctree to output format
    """

    default_conf = ''

    def __init__(self, buildername='text', conf_txt=None,
                 status=sys.stdout, warningiserror=True):
        """ Build ReST text in string `rst_text` into doctree.

        Parameters
        ----------
        buildername : str, optional
            Builder name.
        conf_txt : None or str
            Text for ``conf.py`` file controlling Sphinx build.
        status : file-like object or None, optional
            File-like object to which to write build status messages, or None
            for no build status messages.
        warningiserror : {True, False}, optional
            if True, raise an error for warning during the Sphinx build.
        """
        self.buildername = buildername
        self.conf_txt = conf_txt if not conf_txt is None else self.default_conf
        self.status = status
        self.warningiserror = warningiserror

    def _make_app(self, rst_text):
        """ Make, return Sphinx application instance for input ReST text.
        """
        return TempApp(rst_text,
                       self.conf_txt, status=self.status,
                       warningiserror=self.warningiserror,
                       buildername=self.buildername)

    def _build_rst(self, rst_text, resolve=True):
        """ Build ReST text in string `rst_text` into doctree.

        Parameters
        ----------
        rst_text : str
            string containing ReST to build.
        resolve : {True, False}, optional
            Whether to resolve references before returning doctree.

        Returns
        -------
        doctree : node
            document node.
        app : object
            Sphinx application object.  This will need to be cleaned up
            (``app.cleanup()``) after use.
        """
        app = self._make_app(rst_text)
        master_doc = app.config.master_doc
        out_fname = pjoin(app.tmp_dir, master_doc + '.rst')
        with open(out_fname, 'wt') as fobj:
            fobj.write(rst_text)
        # Force build of everything
        app.build(True, [])
        if resolve:
            dt = app.env.get_and_resolve_doctree(master_doc, app.builder)
        else:
            dt = app.env.get_doctree(master_doc)
        return dt, app

    def from_doctree(self, doctree, builder):
        """ Convert doctree `doctree` to output format

        Parameters
        ----------
        doctree : node
            Document node.
        builder : object
            Sphinx builder object.

        Returns
        ------
        output : str
            Representation in output format
        """
        builder.prepare_writing([builder.config.master_doc])
        return builder.writer.write(doctree, UnicodeOutput())

    def from_rst(self, rst_text, resolve=True):
        """ Build Sphinx formatted ReST text `rst_text` into output format

        Parameters
        ----------
        rst_text : str
            string containing ReST to build.
        resolve : {True, False}, optional
            Whether to resolve references before returning doctree.

        Returns
        -------
        output : str
            Text in output format
        """
        doctree, app = self._build_rst(rst_text, resolve)
        res = self.from_doctree(doctree, app.builder)
        app.cleanup()
        return res


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
master_doc = 'contents'   # For compatibility with Sphinx 2
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
