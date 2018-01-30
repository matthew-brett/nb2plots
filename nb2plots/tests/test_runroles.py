""" Tests for runroles module
"""
import re
from os.path import isfile, join as pjoin

from .test_nbplots import PlotsBuilder


class TestSubdirCodeLinks(PlotsBuilder):
    """ Test output file locations for code-links directive.
    """

    rst_sources = {'foo/a_page': """\
A section
#########

.. code-links::

More text.
"""}

    def test_output(self):
        for suffix in ('.py', '.ipynb', '_full.ipynb'):
            assert_true(isfile(pjoin(self.out_dir, 'foo', 'a_page' + suffix)))

from nb2plots import runroles as rr
from nb2plots import doctree2nb
from nb2plots import doctree2py
from nb2plots.converters import to_pxml

from nose.tools import assert_equal, assert_true

from nb2plots.tests import mockapp

from .test_nbplots import PlotsBuilder


def test_runroles_setup(*args):
    # Test extension setup works as expected
    app = mockapp.get_app()
    rr.setup(app)
    connects = [('doctree-resolved', rr.collect_runfiles),
                ('build-finished', rr.write_runfiles)]
    roles = list(rr.NAME2ROLE.items())
    translators = [('ipynb', doctree2nb.Translator),
                   ('python', doctree2py.Translator)]
    for method_name, args, kwargs in app.method_calls:
        if (method_name == 'connect' and args[0:2] in connects):
            connects.remove(args[0:2])
        if (method_name == 'add_role' and args[0:2] in roles):
            roles.remove(args[0:2])
        if (method_name == 'set_translator' and args[0:2] in translators):
            translators.remove(args[0:2])

    assert_equal(len(connects), 0, 'Connections failed')
    assert_equal(len(roles), 0, 'Roles failed')
    assert_equal(len(translators), 0, 'Translators failed')


def test_runrole_doctrees():
    # Test that run roles generate expected doctrees
    expected_re_fmt = """\
<document source=".*?">
    <paragraph>
        Text then 
        <runrole_reference code_type="{code_type}" filename="{filebase}.{ext}" refdoc="contents" reftarget="{base}.{ext}" reftype="{role_type}">
            {descr}
         then text."""

    type2role = {'clear notebook': 'clearnotebook',
                 'full notebook': 'fullnotebook',
                 'python': 'codefile'}

    def assert_rst_pxml(pxml_params, rst_source):
        code_type = pxml_params['code_type']
        pxml = to_pxml.from_rst(rst_source)
        if not 'ext' in pxml_params:
            pxml_params['ext'] = 'py' if code_type == 'python' else 'ipynb'
        pxml_regex = expected_re_fmt.format(
            role_type=type2role[code_type],
            **pxml_params)
        assert_true(re.match(pxml_regex, pxml))

    assert_rst_pxml(
        dict(code_type='clear notebook',
             filebase='contents',
             base='/contents',
             descr='Download this page as a Jupyter notebook \(no outputs\)'),
        "Text then :clearnotebook:`.` then text.")
    assert_rst_pxml(
        dict(code_type='full notebook',
             filebase='contents',
             base='/contents',
             descr=('Download this page as a Jupyter notebook '
                    '\(with outputs\)')),
        "Text then :fullnotebook:`.` then text.")
    assert_rst_pxml(
        dict(code_type='python',
             filebase='contents',
             base='/contents',
             descr='Download this page as a Python code file'),
        "Text then :codefile:`.` then text.")
    for code_type in ('clear notebook', 'full notebook', 'python'):
        role_type = type2role[code_type]
        assert_rst_pxml(
            dict(code_type=code_type,
                 filebase='contents',
                 base='/contents',
                 descr='message to taste'),
            "Text then :{}:`message to taste` then text.".format(role_type))
        assert_rst_pxml(
            dict(code_type=code_type,
                 filebase='foo',
                 base='foo',
                 ext='ipynb',
                 descr='message to taste'),
            "Text then :{}:`message to taste <foo.ipynb>` then text."
            .format(role_type))
        # It is annoying, but there must be a first text description for the
        # angle brackets part to refer to the output file name.  This is how
        # ReST role processing usually works.
        assert_rst_pxml(
            dict(code_type=code_type,
                 filebase='contents',
                 base='/contents',
                 descr='<foo.ipynb>'),
            "Text then :{}:`<foo.ipynb>` then text.".format(role_type))


class TestSubdirBuild(PlotsBuilder):
    """ Test that output files from subdirectories have correct location
    """

    rst_sources = {'foo/a_page': """\
A section
#########

Some text.

:clearnotebook:`notebook here`

Text is endless.

:codefile:`code here`

Bare path is relative to containing directory:

:codefile:`code here <my_code.py>`

Can have relative parts too:

:clearnotebook:`notebook here <../my_nb.ipynb>`

Prepended / refers to root of project:

:codefile:`code here </more_code.py>`
"""}

    def test_output(self):
        for suffix in ('.py', '.ipynb'):
            assert_true(isfile(pjoin(self.out_dir, 'foo', 'a_page' + suffix)))
        assert_true(isfile(pjoin(self.out_dir, 'foo', 'my_code.py')))
        assert_true(isfile(pjoin(self.out_dir, 'my_nb.ipynb')))
        assert_true(isfile(pjoin(self.out_dir, 'more_code.py')))
