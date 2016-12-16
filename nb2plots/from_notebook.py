#!python
""" Convert from notebook to rst page with plot directives
"""

import re

from jinja2 import DictLoader

from .ipython_shim import nbformat, nbconvert, traitlets, config

MPL_INLINE = re.compile(r"^\s*%\s*matplotlib\s+(inline|nbagg)\s*$",
                        re.MULTILINE)


# Template to label code and output and plot blocks
dl = DictLoader({'rst_plots.tpl': """\
{%- extends 'rst.tpl' -%}

{% block input %}
{%- if cell.source.strip() | has_mpl_inline -%}
.. mpl-interactive::

{% endif -%}
{%- if cell.source.strip() | strip_ipy -%}
##CODE_START##
{{ cell.source | strip_ipy | to_doctests | indent}}
##CODE_END##
{% endif -%}
{% endblock input %}

{%- block execute_result -%}
{%- block data_priority scoped -%}
{{ super() }}
{%- endblock -%}
{%- endblock execute_result -%}

{%- block data_svg -%}
{%- endblock data_svg -%}
{%- block data_png -%}
{%- endblock data_png -%}

{%- block stream -%}
##STDOUT_START##
{{ output.text | ellipse_mpl | indent }}
##STDOUT_END##
{%- endblock stream -%}

{%- block data_text scoped -%}
##END_OUT_START##
{{ output.data['text/plain'] | ellipse_mpl | indent }}
##END_OUT_END##
{%- endblock data_text -%}
"""})


def has_mpl_inline(code):
    return MPL_INLINE.search(code)


def strip_ipy(code):
    """ Strip any ipython magic lines """
    return '\n'.join([line for line in code.split('\n')
                      if not line.strip().startswith('%')])


def to_doctests(code, first='>>> ', cont='... '):
    """Add docstring prompts to code snippets"""
    new_code = []
    code_list = code.split('\n')
    prefix = first
    last_line_no = len(code_list) - 1
    for i, line in enumerate(code_list):
        if line.strip() != '':
            prefix = cont if line.startswith(' ') else first
            new_code.append(prefix + line)
            continue
        # For blank lines, we always strip the whitespace, but we will need a
        # prefix for anything but the last line
        if i == last_line_no:
            prefix = ''
        elif code_list[i + 1].startswith(' '):
            # Use continuation for line following
            prefix = cont.rstrip()
        else:  # Use prefix for previous line
            prefix = prefix.rstrip()
        new_code.append(prefix)

    return '\n'.join(new_code)


MPL_LIST_OUT = re.compile('\[<matplotlib\..*?>\]')
MPL_OBJ_OUT = re.compile('<matplotlib\..*?>')

def ellipse_mpl(text):
    """ Replace outputs of matplotlib objects with ellipses
    """
    text = MPL_LIST_OUT.sub('[...]', text)
    return MPL_OBJ_OUT.sub('<...>', text)


class PlotsExporter(nbconvert.RSTExporter):
    template_file = 'rst_plots.tpl'
    filters = traitlets.Dict(dict(
        has_mpl_inline=has_mpl_inline,
        to_doctests=to_doctests,
        strip_ipy=strip_ipy,
        ellipse_mpl=ellipse_mpl,
    ), config=True)


# Code, with option stdout and optional end-of-block output
CODE_WITH_OUTPUT = re.compile(
    '^##CODE_START##\n'
    '(?P<code>.*?)'
    '^##CODE_END##(\n|$)'
    '([\s\\n]*?'
    '^##STDOUT_START##\n'
    '(?P<stdout>.*?)'
    '^##STDOUT_END##(\n|$))?'
    '([\s\\n]*?'
    '^##END_OUT_START##\n'
    '(?P<end_out>.*?)'
    '^##END_OUT_END##(\n|$))?', re.S | re.M)


PLOT_DIRECTIVE_PREFIX = """\
.. nbplot::

"""

def repl_code_plot(match):
    groups = match.groupdict(default='')
    out = ''.join((PLOT_DIRECTIVE_PREFIX,
                   groups['code'],
                   groups['end_out']))
    if groups['stdout']:
        out += '\n' + groups['stdout']
    return out


def convert_nb_fname(nb_fname):
    with open(nb_fname, 'rt') as nb_fobj:
        notebook = nbformat.read(nb_fobj, as_version=4)
    return convert_nb(notebook)


def convert_nb(notebook):
    # Turn off output preprocessor (we don't want the figures)
    c =  config.Config({
        'ExtractOutputPreprocessor':{'enabled': False}
    })
    plots_exporter = PlotsExporter(extra_loaders=[dl], config=c)
    output, resources = plots_exporter.from_notebook_node(notebook)
    return CODE_WITH_OUTPUT.sub(repl_code_plot, output)
