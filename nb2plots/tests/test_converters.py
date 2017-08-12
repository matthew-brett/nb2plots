""" Test bare Converter class
"""

from ..converters import Converter

from nose.tools import assert_equal, assert_regexp_matches


NEW_PAGE = u"""
More fancy title
++++++++++++++++

More compelling text
"""

def test_converter():
    # Default converter
    conv = Converter()
    text = conv.from_rst(NEW_PAGE)
    assert_equal(text.strip(), """\
More fancy title
****************

More compelling text""")
    # pseudoxml converter
    conv = Converter('pseudoxml')
    pxml = conv.from_rst(NEW_PAGE)
    assert_regexp_matches(pxml, r"""<document source=".*/contents.rst">
    <section ids="more-fancy-title" names="more\\ fancy\\ title">
        <title>
            More fancy title
        <paragraph>
            More compelling text
""")
