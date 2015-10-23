#!python
""" Convert from notebook to rst page with plot directives
"""

import re

from jinja2 import DictLoader

from .ipython_shim import nbformat, nbconvert, traitlets, config


# Template to label code and output and plot blocks
dl = DictLoader({'rst_plots': """\
{%- extends 'rst.tpl' -%}

{% block input %}
{%- if cell.source.strip() | strip_ipy -%}
##CODE_START##
{{ cell.source | strip_ipy | to_doctests | indent}}
##CODE_END##
{% endif -%}
{% endblock input %}

{% block data_svg %}
##PLOT##
{% endblock data_svg %}

{% block data_png %}
##PLOT##
{% endblock data_png %}

{% block stream %}
##OUTPUT_START##
{{ output.text | ellipse_mpl | indent }}
##OUTPUT_END##
{% endblock stream %}

{% block data_text scoped %}
##OUTPUT_START##
{{ output.data['text/plain'] | ellipse_mpl | indent }}
##OUTPUT_END##
{% endblock data_text %}
"""})


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
        if line.strip() == '':
            # Blank line - which prefix should we use?
            if i < last_line_no and code_list[i + 1].startswith(' '):
                # Use continuation for line following
                prefix = cont.rstrip()
            else:  # Use prefix for previous line
                prefix = prefix.rstrip()
        elif line.startswith(' '):
            prefix = cont
        else:
            prefix = first
        new_code.append(prefix + line)

    return '\n'.join(new_code)


MPL_OBJ_OUT = re.compile('<matplotlib\..*?>')

def ellipse_mpl(text):
    """ Replace outputs of matplotlib objects with ellipses
    """
    return MPL_OBJ_OUT.sub('...', text)


class PlotsExporter(nbconvert.RSTExporter):
    template_file = 'rst_plots'
    filters = traitlets.Dict(dict(
        to_doctests=to_doctests,
        strip_ipy=strip_ipy,
        ellipse_mpl=ellipse_mpl,
    ), config=True)



# Put code output into code block
CODE_WITH_OUTPUT = re.compile(
    '(^##CODE_END##\n)'
    '[\S\\n]*?'
    '^##OUTPUT_START##\n'
    '(.*?)'
    '^##OUTPUT_END##$', re.S | re.M)

# put nofigs into blocks not apparently returning figures
CODE_WITH_OPTIONAL_PLOT = re.compile(
    '^##CODE_START##\n'
    '(.*?)'
    '^##CODE_END##\n'
    '([\S\\n]*^##PLOT##)?', re.S | re.M)

PLOT_DIRECTIVE_FMT = """\
.. plot::
    :context:{0}

"""

def repl_code_plot(match):
    groups = match.groups()
    if groups[1] is None:
        return PLOT_DIRECTIVE_FMT.format('\n    :nofigs:') + groups[0]
    return PLOT_DIRECTIVE_FMT.format('') + groups[0]


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

    out1 = CODE_WITH_OUTPUT.sub(r'\2\1', output)
    out2 = CODE_WITH_OPTIONAL_PLOT.sub(repl_code_plot, out1)
    return out2
