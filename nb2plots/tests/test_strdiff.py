""" Test strdiff module
"""

from nb2plots.strdiff import get_diff


def test_get_diff():
    assert get_diff('foo', 'foo') == "L0, OK: foo"
    assert get_diff('foo', 'baz') == "L0, S1: foo\nL0, S2: baz"
    assert (get_diff('foo\nfoo', 'bar\nfoo\nbaz') == """\
L0, S1: foo
L0, S2: bar
L1, OK: foo
Remaining line in second string is:
        baz""")
    assert (get_diff('bar\nfoo\nbaz', 'foo\nfoo') == """\
L0, S1: bar
L0, S2: foo
L1, OK: foo
Remaining line in first string is:
        baz""")
    assert (get_diff('bar\nfoo\nbaz\nbof', 'foo\nfoo') == """\
L0, S1: bar
L0, S2: foo
L1, OK: foo
Remaining lines in first string are:
        baz
        bof""")
