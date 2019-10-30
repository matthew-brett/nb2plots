""" Test code-links directive """

from os.path import isfile, join as pjoin

import re

from nb2plots.converters import to_pxml

from nb2plots.testing import PlotsBuilder


def test_codelinks():

    def as_pxml(rst_text):
        return to_pxml.from_rst(rst_text, resolve=False)

    page = """\
Text here

.. code-links::

More text here."""
    both_re = re.compile(r"""<document source=".*?">
    <paragraph>
        Text here
    <code_links>
        <bullet_list bullet="\*">
            <list_item>
                <paragraph>
                    <runrole_reference refdoc="contents" reftarget="/contents.py" reftype="pyfile">
                        Download this page as a Python code file
                    ;
            <list_item>
                <paragraph>
                    <runrole_reference refdoc="contents" reftarget="/contents.ipynb" reftype="clearnotebook">
                        Download this page as a Jupyter notebook \(no outputs\)
                    ;
            <list_item>
                <paragraph>
                    <runrole_reference refdoc="contents" reftarget="/contents_full.ipynb" reftype="fullnotebook">
                        Download this page as a Jupyter notebook \(with outputs\)
                    .
    <paragraph>
        More text here.""")
    pxml = as_pxml(page)
    assert both_re.match(pxml)
    # Default is 'both'
    page = """\
Text here

.. code-links:: python clear full

More text here."""
    pxml = as_pxml(page)
    assert both_re.match(pxml)
    page = """\
Text here

.. code-links:: clear

More text here."""
    pxml = as_pxml(page)
    assert re.match(r"""<document source=".*?">
    <paragraph>
        Text here
    <code_links>
        <bullet_list bullet="\*">
            <list_item>
                <paragraph>
                    <runrole_reference refdoc="contents" reftarget="/contents.ipynb" reftype="clearnotebook">
                        Download this page as a Jupyter notebook \(no outputs\)
                    .
    <paragraph>
        More text here.""" , pxml)
    page = """\
Text here

.. code-links:: full

More text here."""
    pxml = as_pxml(page)
    assert re.match(r"""<document source=".*?">
    <paragraph>
        Text here
    <code_links>
        <bullet_list bullet="\*">
            <list_item>
                <paragraph>
                    <runrole_reference refdoc="contents" reftarget="/contents_full.ipynb" reftype="fullnotebook">
                        Download this page as a Jupyter notebook \(with outputs\)
                    .
    <paragraph>
        More text here.""", pxml)
    page = """\
Text here

.. code-links:: full python

More text here."""
    pxml = as_pxml(page)
    assert re.match(r"""<document source=".*?">
    <paragraph>
        Text here
    <code_links>
        <bullet_list bullet="\*">
            <list_item>
                <paragraph>
                    <runrole_reference refdoc="contents" reftarget="/contents_full.ipynb" reftype="fullnotebook">
                        Download this page as a Jupyter notebook \(with outputs\)
                    ;
            <list_item>
                <paragraph>
                    <runrole_reference refdoc="contents" reftarget="/contents.py" reftype="pyfile">
                        Download this page as a Python code file
                    .
    <paragraph>
        More text here.""", pxml)


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
            assert isfile(pjoin(self.out_dir, 'foo', 'a_page' + suffix))
