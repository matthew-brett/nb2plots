# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
""" Test scripts

Test running scripts
"""
from __future__ import division, print_function, absolute_import

from os.path import (dirname, join as pjoin, abspath)
from glob import glob

from nose.tools import (assert_true, assert_false, assert_not_equal,
                        assert_equal)

from .scriptrunner import ScriptRunner


runner = ScriptRunner()
run_command = runner.run_command


def script_test(func):
    # Decorator to label test as a script_test
    func.script_test = True
    return func
script_test.__test__ = False # It's not a nose test

DATA_PATH = abspath(pjoin(dirname(__file__), 'rst_md_files'))


@script_test
def test_rst2md():
    # test rst2md script over all .rst files checking against .md files
    for rst_fname in glob(pjoin(DATA_PATH, '*.rst')):
        md_fname = rst_fname[:-3] + 'md'
        cmd = ['rst2md', rst_fname]
        code, stdout, stderr = run_command(cmd)
        with open(md_fname, 'rb') as fobj:
            expected_md = fobj.read()
        assert_equal(stdout, expected_md)
