""" Test code-links directive """

import re

from nb2plots.converters import to_pxml

from nose.tools import assert_true


def test_codelinks():
    page = """\
Text here

.. code-links::

More text here."""
    both_re = re.compile("""\
<document source=".*?">
    <paragraph>
        Text here
    <container>
        <only expr="html">
            <bullet_list bullet="\*">
                <list_item>
                    <paragraph>
                        <runrole_reference code_type="python" refdoc="contents" reftarget="contents.py" reftype="codefile">
                            Download this page as a Python code file
                        ;
                <list_item>
                    <paragraph>
                        <runrole_reference code_type="clear notebook" refdoc="contents" reftarget="contents.ipynb" reftype="clearnotebook">
                            Download this page as a Jupyter notebook \(no outputs\)
                        ;
                <list_item>
                    <paragraph>
                        <runrole_reference code_type="full notebook" refdoc="contents" reftarget="contents_full.ipynb" reftype="fullnotebook">
                            Download this page as a Jupyter notebook \(with outputs\)
                        .
    <paragraph>
        More text here.""")
    pxml = to_pxml.from_rst(page)
    assert_true(both_re.match(pxml))
    # Default is 'both'
    page = """\
Text here

.. code-links:: python clear full

More text here."""
    pxml = to_pxml.from_rst(page)
    assert_true(both_re.match(pxml))
    page = """\
Text here

.. code-links:: clear

More text here."""
    pxml = to_pxml.from_rst(page)
    assert_true(re.match("""\
<document source=".*?">
    <paragraph>
        Text here
    <container>
        <only expr="html">
            <bullet_list bullet="\*">
                <list_item>
                    <paragraph>
                        <runrole_reference code_type="clear notebook" refdoc="contents" reftarget="contents.ipynb" reftype="clearnotebook">
                            Download this page as a Jupyter notebook \(no outputs\)
                        .
    <paragraph>
        More text here.""" , pxml))
    page = """\
Text here

.. code-links:: full

More text here."""
    pxml = to_pxml.from_rst(page)
    assert_true(re.match("""\
<document source=".*?">
    <paragraph>
        Text here
    <container>
        <only expr="html">
            <bullet_list bullet="\*">
                <list_item>
                    <paragraph>
                        <runrole_reference code_type="full notebook" refdoc="contents" reftarget="contents_full.ipynb" reftype="fullnotebook">
                            Download this page as a Jupyter notebook \(with outputs\)
                        .
    <paragraph>
        More text here.""", pxml))
    page = """\
Text here

.. code-links:: full python

More text here."""
    pxml = to_pxml.from_rst(page)
    assert_true(re.match("""\
<document source=".*?">
    <paragraph>
        Text here
    <container>
        <only expr="html">
            <bullet_list bullet="\*">
                <list_item>
                    <paragraph>
                        <runrole_reference code_type="full notebook" refdoc="contents" reftarget="contents_full.ipynb" reftype="fullnotebook">
                            Download this page as a Jupyter notebook \(with outputs\)
                        ;
                <list_item>
                    <paragraph>
                        <runrole_reference code_type="python" refdoc="contents" reftarget="contents.py" reftype="codefile">
                            Download this page as a Python code file
                        .
    <paragraph>
        More text here.""", pxml))
