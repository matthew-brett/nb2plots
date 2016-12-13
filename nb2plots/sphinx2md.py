""" Conversion from Sphinx ReST to Markdown
"""

import sys

from .sphinxutils import build_rst
from .doctree2md import Writer, UnicodeOutput


def sphinx2md(rst_text, conf_txt=None, status=sys.stdout, warningiserror=True):
    """ Build Sphinx formatted ReST text `rst_text` into Markdown

    Parameters
    ----------
    rst_text : str
        string containing ReST to build.
    conf_txt : None or str, optional
        text for configuration ``conf.py`` file.  None gives a default conf
        file.
    status : file-like object or None
        File-like object to which to write build status messages, or None for
        no build status messages.
    warningiserror : {True, False}, optional
        if True, raise an error for warning during the Sphinx build.

    Returns
    -------
    mdown : str
        Text in Markdown format
    """
    doctree = build_rst(rst_text, conf_txt, status=status,
                        warningiserror=warningiserror)
    return Writer().write(doctree, UnicodeOutput())
