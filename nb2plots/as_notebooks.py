""" Directive to insert links to current document as notebooks

As a bare directive, with no options, inserts links to the current document as
a clear notebook (no outputs) and a full notebook (outputs inserted by
executing the built notebook)::

    .. as-notebooks:

You can select one or both of the clear or full notebooks with the ``type``
option::

    .. as-notebooks:
        :type: clear

    .. as-notebooks:
        :type: full

    .. as-notebooks:
        :type: both

``both`` is the default.
"""

from docutils.statemachine import StringList
from docutils.parsers.rst import directives
from docutils import nodes

from sphinx.util.compat import Directive


def setup_module(module):
    # Prevent nosetests trying to run setup function
    pass


class AsNotebooks(Directive):
    """ Add links to built notebook(s) to output page.
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    option_spec = {'type': directives.unchanged}

    nb_text_fmt = ('* :{0}notebook:`Download this page as a Jupyter '
                   'notebook ({1} outputs) <{2}_{0}.ipynb>`')

    def _role_lines(self):
        """ Text lines for notebook roles of types requested in options.
        """
        env = self.state.document.settings.env
        nb_spec = self.options.get('type', 'both')
        nb_types = ('clear', 'full') if nb_spec == 'both' else (nb_spec,)
        lines = []
        for nb_type in nb_types:
            lines.append(self.nb_text_fmt.format(
                nb_type,
                'with' if nb_type == 'full' else 'no',
                env.docname))
        return lines

    def run(self):
        lines = ['.. only:: html', '']
        lines += ['   ' + line for line in self._role_lines()]
        node = nodes.container('\n'.join(lines))
        self.state.nested_parse(StringList(lines),
                                       self.content_offset,
                                node)
        return [node]


def setup(app):
    setup.app = app
    setup.config = app.config
    setup.confdir = app.confdir

    app.add_directive('as-notebooks', AsNotebooks)
