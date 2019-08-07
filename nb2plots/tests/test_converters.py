""" Test bare Converter class
"""

import re

from nb2plots.converters import Converter


NEW_PAGE = u"""
More fancy title
++++++++++++++++

More compelling text
"""

def test_converter():
    # Default converter
    conv = Converter()
    text = conv.from_rst(NEW_PAGE)
    assert text.strip() == """\
More fancy title
****************

More compelling text"""
    # pseudoxml converter
    conv = Converter('pseudoxml')
    pxml = conv.from_rst(NEW_PAGE)
    assert re.search(r"""<document source=".*/(contents|index)\.rst">
    <section ids="more-fancy-title" names="more\\ fancy\\ title">
        <title>
            More fancy title
        <paragraph>
            More compelling text
""", pxml) is not None
