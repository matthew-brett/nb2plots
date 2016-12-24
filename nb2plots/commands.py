""" Support for command-line scripts
"""

import sys
from argparse import ArgumentParser

from .converters import NbConverter

# Bytes stream for writing to stdout
bin_stdout = sys.stdout.buffer if sys.version_info[0] > 2 else sys.stdout


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
    bin_stdout.write(output.encode('utf-8'))
