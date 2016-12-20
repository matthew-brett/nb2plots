# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
""" Test scripts

Test running scripts
"""
from __future__ import division, print_function, absolute_import

from os.path import (join as pjoin, exists)
from glob import glob
import re

from nose.tools import assert_equal, assert_true

from .scriptrunner import ScriptRunner
from .convutils import fcontents, DATA_PATH
from .test_doctree2nb import assert_nb_equiv


runner = ScriptRunner()
run_command = runner.run_command


def script_test(func):
    # Decorator to label test as a script_test
    func.script_test = True
    return func
script_test.__test__ = False # It's not a nose test


@script_test
def test_rst2md():
    # test rst2md script over all .rst files checking against .md files
    for rst_fname in glob(pjoin(DATA_PATH, '*.rst')):
        md_fname = rst_fname[:-3] + 'md'
        with open(md_fname, 'rb') as fobj:
            expected_md = fobj.read()
        # Skip files containing text "skip".  These are files for which the
        # source ReST is not valid in plain docutils, such as those containing
        # Sphinx directives and roles.
        if expected_md.strip() == b'skip':
            continue
        cmd = ['rst2md', rst_fname]
        code, stdout, stderr = run_command(cmd)
        assert_equal(stdout, expected_md)


@script_test
def test_sphinx2md():
    # test sphinx2md script over all .rst files checking against .smd / .md
    # files
    for rst_fname in glob(pjoin(DATA_PATH, '*.rst')):
        # Try .smd filename first, otherwise ordinary .md
        md_fname = rst_fname[:-3] + 'smd'
        if not exists(md_fname):
            md_fname = rst_fname[:-3] + 'md'
        expected_md = fcontents(md_fname)
        cmd = ['sphinx2md', rst_fname]
        code, stdout, stderr = run_command(cmd)
        assert_equal(stdout, expected_md)


@script_test
def test_sphinx2nb():
    # test sphinx2nb script over all .rst files checking against .ipynb files
    for rst_fname in glob(pjoin(DATA_PATH, '*.rst')):
        nb_fname = rst_fname[:-3] + 'ipynb'
        expected = fcontents(nb_fname, 't')
        cmd = ['sphinx2nb', rst_fname]
        code, stdout, stderr = run_command(cmd)
        assert_nb_equiv(stdout.decode('utf-8'), expected)


@script_test
def test_sphinx2py():
    # test sphinx2py script over all .rst files checking against .ipynb files
    for rst_fname in glob(pjoin(DATA_PATH, '*.rst')):
        py_fname = rst_fname[:-3] + 'py'
        expected = fcontents(py_fname, 'b')
        cmd = ['sphinx2py', rst_fname]
        code, stdout, stderr = run_command(cmd)
        assert_equal(stdout, expected)


@script_test
def test_sphinx2pxml():
    rst_fname = pjoin(DATA_PATH, 'sect_text.rst')
    cmd = ['sphinx2pxml', rst_fname]
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
    assert_true(re.match(pattern, output))
