""" Utility to show differences between strings

Used for debugging test output
"""

def get_diff(str1, str2, fmt_indent=None):
    """ Return line-by-line difference between multiline strings """
    output = []
    str_lists = [str1.splitlines(), str2.splitlines()]
    lens = [len(L) for L in str_lists]
    min_len = min(lens)
    fmt_str = 'L{:d}, {:2s}: {}'
    if fmt_indent is None:
        fmt_indent = len(fmt_str.format(0, '', '')) * ' '
    for i in range(min(lens)):
        L1 = str_lists[0][i]
        L2 = str_lists[1][i]
        if L1 == L2:
            output.append(fmt_str.format(i, 'OK', L1))
        else:
            output.append(fmt_str.format(i, 'S1', L1))
            output.append(fmt_str.format(i, 'S2', L2))
    diff = lens[1] - lens[0]
    if diff != 0:
        longer = diff > 0
        abs_diff = diff if diff > 0 else -diff
        output.append('Remaining line{} in {} string {}:'.format(
            's' if abs_diff > 1 else '',
            'second' if longer else 'first',
            'are' if abs_diff > 1 else 'is',
        ))
        output += [fmt_indent + L for L in str_lists[longer][min_len:]]
    return '\n'.join(output)
