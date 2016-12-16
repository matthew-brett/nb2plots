""" Test as-notebooks directive """

import re

from nb2plots.sphinxutils import build_rst, doctree2pxml

from nose.tools import assert_true


def test_as_notebooks():
    page = """\
Text here

.. as-notebooks::

More text here."""
    doctree = build_rst(page)
    both_re = re.compile("""\
<document source=".*?">
    <paragraph>
        Text here
    <container>
        <only expr="html">
            <bullet_list bullet="\*">
                <list_item>
                    <paragraph>
                        <notebook_reference evaluate="False" refdoc="contents" reftarget="contents_clear.ipynb" reftype="clearnotebook">
                            Download this page as a Jupyter notebook \(no outputs\)
                <list_item>
                    <paragraph>
                        <notebook_reference evaluate="True" refdoc="contents" reftarget="contents_full.ipynb" reftype="fullnotebook">
                            Download this page as a Jupyter notebook \(with outputs\)
    <paragraph>
        More text here.""")
    pxml = doctree2pxml(doctree)
    assert_true(both_re.match(pxml))
    # Default is 'both'
    page = """\
Text here

.. as-notebooks::
    :type: both

More text here."""
    doctree_both = build_rst(page)
    assert_true(both_re.match(doctree2pxml(doctree_both)))
    page = """\
Text here

.. as-notebooks::
    :type: clear

More text here."""
    doctree = build_rst(page)
    assert_true(re.match("""\
<document source=".*?">
    <paragraph>
        Text here
    <container>
        <only expr="html">
            <bullet_list bullet="\*">
                <list_item>
                    <paragraph>
                        <notebook_reference evaluate="False" refdoc="contents" reftarget="contents_clear.ipynb" reftype="clearnotebook">
                            Download this page as a Jupyter notebook \(no outputs\)
    <paragraph>
        More text here.""" , doctree2pxml(doctree)))
    page = """\
Text here

.. as-notebooks::
    :type: full

More text here."""
    doctree = build_rst(page)
    assert_true(re.match("""\
<document source=".*?">
    <paragraph>
        Text here
    <container>
        <only expr="html">
            <bullet_list bullet="\*">
                <list_item>
                    <paragraph>
                        <notebook_reference evaluate="True" refdoc="contents" reftarget="contents_full.ipynb" reftype="fullnotebook">
                            Download this page as a Jupyter notebook \(with outputs\)
    <paragraph>
        More text here.""" , doctree2pxml(doctree)))
