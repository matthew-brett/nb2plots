""" Support for command-line scripts
"""

import sys
from argparse import ArgumentParser

from .converters import NbConverter


def nb2plots_main():
    """Entry point for the ``nb2plots`` command."""
    from .from_notebook import convert_nb_fname

    parser = ArgumentParser(
        description="Convert notebook to ReST format with plot directives")
    parser.add_argument('notebook', help='notebook file to convert')
    args = parser.parse_args()
    rst_text = convert_nb_fname(args.notebook) + '\n'
    sys.stdout.buffer.write(rst_text.encode('utf-8'))


def rst2md_main():
    """Entry point for the ``rst2md`` command."""
    import locale

    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        pass

    from docutils.core import publish_cmdline, default_description

    from .doctree2md import Writer

    description = ('Generates Markdown formatted text from standalone '
                   'reStructuredText sources.  ' + default_description)
    publish_cmdline(writer=Writer(), description=description)


def sphinx2md_main():
    """Entry point for the ``sphinx2md`` command."""
    do_main("Convert Sphinx ReST file to Markdown", 'markdown')


def sphinx2nb_main():
    """Entry point for the ``sphinx2nb`` command."""
    do_main("Convert Sphinx ReST file to Notebook JSON", 'jupyter')


def sphinx2py_main():
    """Entry point for the ``sphinx2py`` command."""
    do_main("Convert Sphinx ReST file to Python code", 'python')


def sphinx2pxml_main():
    """Entry point for the ``sphinx2pxml`` command."""
    do_main("Convert Sphinx ReST file to Pseudo XML", 'pseudoxml')


def get_parser(description):
    """ Get parser for sphinx2something utilities
    """
    parser = ArgumentParser(description=description)
    parser.add_argument('rst_file', help = 'ReST file to convert')
    parser.add_argument('-W', '--warn-is-error', action='store_true',
                        help = 'turn warnings into errors')
    return parser


def do_main(description, buildername):
    """ Get main clause for sphinx2something utilities
    """
    parser = get_parser(description)
    args = parser.parse_args()
    with open(args.rst_file, 'rt') as fobj:
        contents = fobj.read()
    converter = NbConverter(buildername,
                            status=sys.stderr,
                            warningiserror=args.warn_is_error)
    output = converter.from_rst(contents)
    sys.stdout.buffer.write(output.encode('utf-8'))
