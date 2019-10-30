""" Tests for runroles module
"""
import re
from os.path import isfile, join as pjoin

from nb2plots import runroles as rr
from nb2plots.runroles import convert_timeout
from nb2plots import doctree2nb
from nb2plots import doctree2py
from nb2plots.converters import to_pxml

from nb2plots.testing import mockapp
from nb2plots.testing import PlotsBuilder

import pytest


def test_runroles_setup(*args):
    # Test extension setup works as expected
    app = mockapp.get_app()
    rr.setup(app)
    connects = [('doctree-resolved', rr.collect_runfiles),
                ('build-finished', rr.write_runfiles)]
    roles = list(rr.NAME2ROLE.items())
    translators = [('ipynb', doctree2nb.Translator),
                   ('pyfile', doctree2py.Translator)]
    for method_name, args, kwargs in app.method_calls:
        if (method_name == 'connect' and args[0:2] in connects):
            connects.remove(args[0:2])
        if (method_name == 'add_role' and args[0:2] in roles):
            roles.remove(args[0:2])
        if (method_name == 'set_translator' and args[0:2] in translators):
            translators.remove(args[0:2])

    assert len(connects) == 0, 'Connections failed'
    assert len(roles) == 0, 'Roles failed'
    assert len(translators) == 0, 'Translators failed'


def test_convert_timeout():
    assert convert_timeout('4') == 4
    assert convert_timeout('30') == 30
    assert convert_timeout('-1') == -1
    assert convert_timeout('None') == None
    assert convert_timeout('none') == None
    assert convert_timeout('noNe') == None
    with pytest.raises(ValueError):
        convert_timeout('-2')


def test_runrole_doctrees():
    # Test that run roles generate expected doctrees
    expected_re_fmt = """\
<document source=".*?">
    <paragraph>
        Text then 
        <runrole_reference filename="{filebase}.{ext}" refdoc="contents" reftarget="{base}.{ext}" reftype="{role_type}">
            {descr}
         then text."""

    def assert_rst_pxml(pxml_params, rst_source):
        code_type = pxml_params['code_type']
        pxml = to_pxml.from_rst(rst_source)
        if not 'ext' in pxml_params:
            pxml_params['ext'] = 'py' if code_type == 'pyfile' else 'ipynb'
        pxml_regex = expected_re_fmt.format(
            role_type=code_type,
            **pxml_params)
        assert re.match(pxml_regex, pxml)

    assert_rst_pxml(
        dict(code_type='clearnotebook',
             filebase='contents',
             base='/contents',
             descr=r'Download this page as a Jupyter notebook \(no outputs\)'),
        "Text then :clearnotebook:`.` then text.")
    assert_rst_pxml(
        dict(code_type='fullnotebook',
             filebase='contents',
             base='/contents',
             descr=('Download this page as a Jupyter notebook '
                    r'\(with outputs\)')),
        "Text then :fullnotebook:`.` then text.")
    assert_rst_pxml(
        dict(code_type='pyfile',
             filebase='contents',
             base='/contents',
             descr='Download this page as a Python code file'),
        "Text then :pyfile:`.` then text.")
    for code_type in ('clearnotebook', 'fullnotebook', 'pyfile'):
        assert_rst_pxml(
            dict(code_type=code_type,
                 filebase='contents',
                 base='/contents',
                 descr='message to taste'),
            "Text then :{}:`message to taste` then text.".format(code_type))
        assert_rst_pxml(
            dict(code_type=code_type,
                 filebase='foo',
                 base='foo',
                 ext='ipynb',
                 descr='message to taste'),
            "Text then :{}:`message to taste <foo.ipynb>` then text."
            .format(code_type))
        # It is annoying, but there must be a first text description for the
        # angle brackets part to refer to the output file name.  This is how
        # ReST role processing usually works.
        assert_rst_pxml(
            dict(code_type=code_type,
                 filebase='contents',
                 base='/contents',
                 descr='<foo.ipynb>'),
            "Text then :{}:`<foo.ipynb>` then text.".format(code_type))


class TestSubdirBuild(PlotsBuilder):
    """ Test that output files from subdirectories have correct location
    """

    rst_sources = {'foo/a_page': """\
A section
#########

Some text.

:clearnotebook:`notebook here`

Text is endless.

:pyfile:`code here`

Bare path is relative to containing directory:

:pyfile:`code here <my_code.py>`

Can have relative parts too:

:clearnotebook:`notebook here <../my_nb.ipynb>`

Prepended / refers to root of project:

:pyfile:`code here </more_code.py>`
"""}

    def test_output(self):
        for suffix in ('.py', '.ipynb'):
            assert isfile(pjoin(self.out_dir, 'foo', 'a_page' + suffix))
        assert isfile(pjoin(self.out_dir, 'foo', 'my_code.py'))
        assert isfile(pjoin(self.out_dir, 'my_nb.ipynb'))
        assert isfile(pjoin(self.out_dir, 'more_code.py'))


class TestPyfileAlias(PlotsBuilder):
    """ Test that 'codefile' alias works for pyfile
    """

    rst_sources = {'a_page': """\
A section
#########

:codefile:`code here`

>>> True
True
"""}

    def test_output(self):
        assert isfile(pjoin(self.out_dir, 'a_page.py'))


class TestDuplicatesOK(PlotsBuilder):
    """ Test that same and different filename for same code type works.
    """

    rst_sources = {'a_page': """\
Title
#####

:fullnotebook:`name <foo.ipynb>`

:fullnotebook:`name <foo.ipynb>`

:fullnotebook:`name <bar.ipynb>`

"""}

    def test_output(self):
        assert isfile(pjoin(self.out_dir, 'foo.ipynb'))
        assert isfile(pjoin(self.out_dir, 'bar.ipynb'))


class TestDuplicatesNotOK(PlotsBuilder):
    """ Test that same filename for different code type fails.
    """

    rst_sources = {'a_page': """\
Title
#####

:fullnotebook:`name <foo.ipynb>`

:clearnotebook:`name <foo.ipynb>`

"""}

    should_error = True
