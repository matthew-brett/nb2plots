# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
""" Test scripts

Test running scripts
"""

from pathlib import Path
import re
import shutil
import sys

import pytest

from nb2plots.testing.convutils import unsmart, unsmart_nb
from nb2plots.testing.nbtesters import assert_nb_equiv


TESTS_PATH = Path(__file__).parent
RST_MD_PATH = TESTS_PATH / 'rst_md_files'
# Scripts live in the top-level ``scripts`` directory of the source tree.
SCRIPTS_PATH = TESTS_PATH.parents[1] / 'scripts'

# The scripts write UTF-8 bytes to ``sys.stdout.buffer``, which the in-process
# launcher of pytest-console-scripts cannot capture.  Run them as real
# subprocesses instead.
pytestmark = pytest.mark.script_launch_mode('subprocess')


def _script_command(name, *args):
    """ Return command to run script `name` with arguments `args`.

    In a development tree the scripts are not installed, so run them through
    the current Python interpreter.  This also avoids relying on the shebang
    line in the script.  For an installed package, fall back to the script on
    the PATH.
    """
    script_path = SCRIPTS_PATH / name
    if script_path.is_file():
        cmd = [sys.executable, str(script_path)]
    else:
        if shutil.which(name) is None:
            pytest.skip(f'Cannot find script {name!r} on the PATH')
        cmd = [name]
    return cmd + [str(arg) for arg in args]


def run_script(script_runner, name, *args):
    """ Run script `name` with `args`, checking that it succeeded. """
    return script_runner.run(
        _script_command(name, *args), check=True, encoding='utf-8')


def test_rst2md(script_runner):
    # test rst2md script over all .rst files checking against .md files
    for rst_path in RST_MD_PATH.glob('*.rst'):
        md_path = rst_path.with_suffix('.md')
        expected_md = md_path.read_bytes()
        # Skip files containing text "skip".  These are files for which the
        # source ReST is not valid in plain docutils, such as those containing
        # Sphinx directives and roles.
        if expected_md.strip() == b'skip':
            continue
        result = run_script(script_runner, 'rst2md', rst_path)
        assert result.stdout == expected_md.decode('utf-8')


def test_sphinx2md(script_runner):
    # test sphinx2md script over all .rst files checking against .smd / .md
    # files
    for rst_path in RST_MD_PATH.glob('*.rst'):
        # Try .smd filename first, otherwise ordinary .md
        md_path = rst_path.with_suffix('.smd')
        if not md_path.is_file():
            md_path = rst_path.with_suffix('.md')
        expected_md = md_path.read_bytes()
        result = run_script(script_runner, 'sphinx2md', rst_path)
        assert (unsmart(result.stdout) == expected_md.decode('utf-8'))


def test_sphinx2nb(script_runner):
    # test sphinx2nb script over all .rst files checking against .ipynb files
    for rst_path in RST_MD_PATH.glob('*.rst'):
        nb_path = rst_path.with_suffix('.ipynb')
        expected = nb_path.read_text()
        result = run_script(script_runner, 'sphinx2nb', rst_path)
        assert_nb_equiv(unsmart_nb(result.stdout), expected)


def test_sphinx2py(script_runner):
    # test sphinx2py script over all .rst files checking against .ipynb files
    for rst_path in RST_MD_PATH.glob('*.rst'):
        py_path = rst_path.with_suffix('.py')
        expected = py_path.read_bytes()
        result = run_script(script_runner, 'sphinx2py', rst_path)
        assert (unsmart(result.stdout) == expected.decode('utf-8'))


def test_sphinx2pxml(script_runner):
    rst_path = RST_MD_PATH / 'sect_text.rst'
    result = run_script(script_runner, 'sphinx2pxml', rst_path)
    pattern = r"""<document source=".*?">
    <section ids="a-section" names="a\\ section">
        <title>
            A section
        <paragraph>
            Some 
            <emphasis>
                text
            ."""
    assert re.match(pattern, result.stdout)


def test_nb2plots(script_runner):
    fname = 'example_notebook'
    data_path = TESTS_PATH / 'data'
    nb_path = data_path / (fname + '.ipynb')
    rst_path = data_path / 'converted_example.rst'
    expected = rst_path.read_text()
    result = run_script(script_runner, 'nb2plots', nb_path)
    assert result.stdout.strip() == expected.strip()
