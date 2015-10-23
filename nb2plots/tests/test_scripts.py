# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
""" Test scripts

Test running scripts
"""
from __future__ import division, print_function, absolute_import

from os.path import (dirname, join as pjoin, abspath)

from nose.tools import (assert_true, assert_false, assert_not_equal,
                        assert_equal)

from .scriptrunner import ScriptRunner


runner = ScriptRunner()
run_command = runner.run_command


def script_test(func):
    # Decorator to label test as a script_test
    func.script_test = True
    return func
script_test.__test__ = False # It's not a test

DATA_PATH = abspath(pjoin(dirname(__file__), 'data'))


@script_test
def test_nb2plots():
    # test nb2plots script
    fname = pjoin(DATA_PATH, 'small.ipynb')
    cmd = ['nb2plots', fname]
    code, stdout, stderr = run_command(cmd)
    with open(pjoin(DATA_PATH, 'small.rst'), 'rb') as fobj:
        expected_rst = fobj.read()
    assert_equal(stdout, expected_rst)
