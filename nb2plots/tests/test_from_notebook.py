""" Testing from_notebook module
"""

from os.path import dirname, join as pjoin

from ..ipython_shim import nbformat
from ..from_notebook import (convert_nb, convert_nb_fname, to_doctests,
                             has_mpl_inline, CODE_WITH_OUTPUT)


from nose.tools import (assert_true, assert_false, assert_raises,
                        assert_equal, assert_not_equal)


DATA_PATH = pjoin(dirname(__file__), 'data')

PLT_HDR = "\n.. nbplot::\n\n"


def test_simple_cells():
    v4 = nbformat.v4
    nb = v4.new_notebook()
    # Markdown -> default conversion
    md_cell = v4.new_markdown_cell('# Some text')
    nb['cells'] = [md_cell]
    exp_text = "\nSome text\n=========\n"
    assert_equal(convert_nb(nb), exp_text)
    # Code -> replaced with plot directive / doctest markers
    code_cell = v4.new_code_cell('a = 10')
    nb['cells'] = [code_cell]
    exp_code = PLT_HDR + "    >>> a = 10\n"
    assert_equal(convert_nb(nb), exp_code)
    # Empty code -> no output
    empty_code_cell = v4.new_code_cell('')
    nb['cells'] = [empty_code_cell]
    exp_empty_code = "\n"
    assert_equal(convert_nb(nb), exp_empty_code)
    # magic lines get stripped
    magic_code_cell = v4.new_code_cell('%timeit a = 1')
    nb['cells'] = [magic_code_cell]
    assert_equal(convert_nb(nb), exp_empty_code)
    # Magic lines stripped from within other code lines
    mixed_magic_code_cell = v4.new_code_cell('%timeit a = 1\nb = 2')
    exp_mixed_magic = PLT_HDR + "    >>> b = 2\n"
    nb['cells'] = [mixed_magic_code_cell]
    assert_equal(convert_nb(nb), exp_mixed_magic)


def test_mpl_inline_works():
    # Test we get a mpl-interactive directive for %matplotlib inline
    v4 = nbformat.v4
    nb = v4.new_notebook()
    code_cell = v4.new_code_cell('%matplotlib inline\na = 10')
    nb['cells'] = [code_cell]
    exp_code = "\n.. mpl-interactive::\n{}    >>> a = 10\n".format(PLT_HDR)
    assert_equal(convert_nb(nb), exp_code)


def test_mpl_inline():
    assert_false(has_mpl_inline(''))
    assert_false(has_mpl_inline('%matplotlib inline # foo'))
    assert_true(has_mpl_inline('%matplotlib inline'))
    assert_true(has_mpl_inline('%   matplotlib    inline'))
    assert_true(has_mpl_inline('  %   matplotlib    inline'))
    assert_false(has_mpl_inline('%matplotlib nbagg # foo'))
    assert_true(has_mpl_inline('%matplotlib nbagg'))
    assert_true(has_mpl_inline('% matplotlib nbagg\nb = 2'))
    assert_true(has_mpl_inline('a = 1\n% matplotlib nbagg\nb = 2'))


def test_to_doctests():
    # Test to_doctests filter
    assert_equal(to_doctests(''), '')
    assert_equal(to_doctests('a = 1'), '>>> a = 1')
    assert_equal(to_doctests('a = 1\nb = 2'), '>>> a = 1\n>>> b = 2')
    assert_equal(to_doctests(
"""
a = 1
for i in (1, 2):
    a += i

    for j in (2, 3):
        a += j

print(a)
for i in (1, 2):

    a += i
print(a)
"""),
""">>>
>>> a = 1
>>> for i in (1, 2):
...     a += i
...
...     for j in (2, 3):
...         a += j
...
>>> print(a)
>>> for i in (1, 2):
...
...     a += i
>>> print(a)
""")
    assert_equal(to_doctests(
"""def xyz_trans_vol(vol, x_y_z_trans):
    \"\"\" Make a new copy of `vol` translated by `x_y_z_trans` voxels

    x_y_z_trans is a sequence or array length 3, containing the (x, y, z) translations in voxels.

    Values in `x_y_z_trans` can be positive or negative, and can be floats.
    \"\"\"
    x_y_z_trans = np.array(x_y_z_trans)
"""),
""">>> def xyz_trans_vol(vol, x_y_z_trans):
...     \"\"\" Make a new copy of `vol` translated by `x_y_z_trans` voxels
...
...     x_y_z_trans is a sequence or array length 3, containing the (x, y, z) translations in voxels.
...
...     Values in `x_y_z_trans` can be positive or negative, and can be floats.
...     \"\"\"
...     x_y_z_trans = np.array(x_y_z_trans)
""")


def test_small():
    # Regression tests on small notebook
    nb_fname = pjoin(DATA_PATH, 'small.ipynb')
    rst_fname = pjoin(DATA_PATH, 'small.rst')
    out = convert_nb_fname(nb_fname)
    with open(rst_fname, 'rt') as fobj:
        assert_equal(out + '\n', fobj.read())


code = \
"""##CODE_START##
a = 1
b = 2
##CODE_END##"""

code_value = 'a = 1\nb = 2\n'

stdout = \
"""##STDOUT_START##
one
two
##STDOUT_END##"""

stdout_value = 'one\ntwo\n'

end_out = \
"""##END_OUT_START##
three
4
##END_OUT_END##"""

end_out_value = 'three\n4\n'


def test_code_regex():
    # Test regular expression matching for code, output parts

    def get_dict(s):
        match = CODE_WITH_OUTPUT.search(s)
        if match is None:
            return None
        return match.groupdict()

    # Check that the code part must match
    assert_equal(get_dict(stdout), None)
    assert_equal(get_dict(end_out), None)
    # Check different joins still allows detection of parts
    for combination, output in zip(
        ((code,),
         (code, stdout),
         (code, end_out),
         (code, stdout, end_out)),
        (dict(code=code_value, stdout=None, end_out=None),
         dict(code=code_value, stdout=stdout_value, end_out=None),
         dict(code=code_value, stdout=None, end_out=end_out_value),
         dict(code=code_value, stdout=stdout_value, end_out=end_out_value)
        )):
        for joiner in ('\n', '\n  \n\n'):
            in_str = joiner.join(combination)
            assert_equal(get_dict(in_str), output)
            # Check adding extra carriage returns etc is OK
            in_str += '\n\n'
            assert_equal(get_dict(in_str), output)
