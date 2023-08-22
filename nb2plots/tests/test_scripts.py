# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
""" Test scripts

Test running scripts
"""

from pathlib import Path
import re

from scripttester import ScriptTester

from nb2plots.testing.convutils import unsmart, unsmart_nb
from nb2plots.testing.nbtesters import assert_nb_equiv


runner = ScriptTester('nb2plots', win_bin_ext='.bat')
run_command = runner.run_command

TESTS_PATH = Path(__file__).parent
RST_MD_PATH = TESTS_PATH / 'rst_md_files'


def script_test(func):
    # Decorator to label test as a script_test
    func.script_test = True
    return func


@script_test
def test_rst2md():
    # test rst2md script over all .rst files checking against .md files
    for rst_path in RST_MD_PATH.glob('*.rst'):
        md_path = rst_path.with_suffix('.md')
        expected_md = md_path.read_bytes()
        # Skip files containing text "skip".  These are files for which the
        # source ReST is not valid in plain docutils, such as those containing
        # Sphinx directives and roles.
        if expected_md.strip() == b'skip':
            continue
        cmd = ['rst2md', str(rst_path)]
        code, stdout, stderr = run_command(cmd)
        assert stdout == expected_md


@script_test
def test_sphinx2md():
    # test sphinx2md script over all .rst files checking against .smd / .md
    # files
    for rst_path in RST_MD_PATH.glob('*.rst'):
        # Try .smd filename first, otherwise ordinary .md
        md_path = rst_path.with_suffix('.smd')
        if not md_path.is_file():
            md_path = rst_path.with_suffix('.md')
        expected_md = md_path.read_bytes()
        cmd = ['sphinx2md', str(rst_path)]
        code, stdout, stderr = run_command(cmd)
        assert (unsmart(stdout.decode('utf-8')) ==
                expected_md.decode('utf-8'))


@script_test
def test_sphinx2nb():
    # test sphinx2nb script over all .rst files checking against .ipynb files
    for rst_path in RST_MD_PATH.glob('*.rst'):
        nb_path = rst_path.with_suffix('.ipynb')
        expected = nb_path.read_text()
        cmd = ['sphinx2nb', str(rst_path)]
        code, stdout, stderr = run_command(cmd)
        assert_nb_equiv(unsmart_nb(stdout.decode('utf-8')),
                        expected)


@script_test
def test_sphinx2py():
    # test sphinx2py script over all .rst files checking against .ipynb files
    for rst_path in RST_MD_PATH.glob('*.rst'):
        py_path = rst_path.with_suffix('.py')
        expected = py_path.read_bytes()
        cmd = ['sphinx2py', str(rst_path)]
        code, stdout, stderr = run_command(cmd)
        assert (unsmart(stdout.decode('utf-8')) ==
                expected.decode('utf-8'))


@script_test
def test_sphinx2pxml():
    rst_path = RST_MD_PATH / 'sect_text.rst'
    cmd = ['sphinx2pxml', str(rst_path)]
    code, stdout, stderr = run_command(cmd)
    pattern = r"""<document source=".*?">
    <section ids="a-section" names="a\\ section">
        <title>
            A section
        <paragraph>
            Some 
            <emphasis>
                text
            ."""
    output = stdout.decode('utf-8')
    assert re.match(pattern, output)


@script_test
def test_nb2plots():
    fname = 'example_notebook'
    data_path = TESTS_PATH / 'data'
    nb_path = data_path / (fname + '.ipynb')
    rst_path = data_path / 'converted_example.rst'
    expected = rst_path.read_text()
    cmd = ['nb2plots', str(nb_path)]
    code, stdout, stderr = run_command(cmd)
    output = stdout.decode('utf-8')
    assert output.strip() == expected.strip()
