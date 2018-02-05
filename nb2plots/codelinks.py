""" Directive to insert links to current document as runnable code.

As a bare directive, with no options, inserts links to the current document as
a Python code file; a clear notebook (no outputs) and a full notebook (outputs
inserted by executing the built notebook)::

    .. code-links:

You can select one or more of these links with a list as an argument to the
directive, where "python", "clear" and "full" refer to a Python code file,
clear notebook file and a full notebook file, respectively. For example::

    .. code-links: python

    .. code-links: python full

    .. code-links: clear full

``python clear full`` is the default.

Kernel timeout
--------------

When you build the full notebook, Jupyter will execute the code in each cell.
By default, Jupyter will time out for any cell that takes longer than 30
seconds to execute.  You can change this default for the whole project with the
``fill_notebook_timeout`` setting in the ``conf.py`` file (see below).  If you
just want to change the setting for a single page, you can add the ``timeout``
option to the ``code-links`` directive.  For example::

    .. code-links:
        :timeout: 120

Set the ``timeout`` value to -1 or ``none`` to disable timeout entirely for
this directive / page.

Configuration options
---------------------

The code-links directive has the following configuration options, that can be
set in the ``conf.py`` file.

    fill_notebook_timeout
        Default value for Jupyter kernel timeout when executing notebooks
        during page build.  If not set, default is 30 seconds. Set to -1 or
        None to disable timeout.
"""

from docutils.statemachine import StringList
from docutils import nodes
from docutils.parsers.rst import Directive

from .runroles import NAME2ROLE, convert_timeout, runrole_reference


class code_links(nodes.container):
    """ Node to contain code links """


class CodeLinks(Directive):
    """ Add links to built runnable code from contained page.
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 3
    option_spec = {'timeout': convert_timeout}

    _type2params = dict(python=dict(role_name='pyfile', suffix=''),
                        clear=dict(role_name='clearnotebook', suffix=''),
                        full=dict(role_name='fullnotebook', suffix='_full'))

    code_links_node = code_links

    def _role_lines(self):
        """ Text lines for notebook roles of types requested in options.
        """
        code_types = (self.arguments if len(self.arguments)
                      else ['python', 'clear', 'full'])
        env = self.state.document.settings.env
        lines = []
        for code_type in code_types:
            params = self._type2params[code_type]
            suffix = params['suffix']
            role_name = params['role_name']
            role = NAME2ROLE[role_name]
            lines.append(
                '* :{role_name}:`{descr} </{docname}{suffix}{ext}>`'.format(
                    role_name=role_name,
                    descr=role.default_text,
                    docname=env.docname,
                    suffix=suffix,
                    ext=role.default_extension))
        return lines

    def run(self):
        lines = []
        body_lines = self._role_lines()
        for i, line in enumerate(body_lines):
            suffix = '.' if i == len(body_lines) - 1 else ';'
            lines.append('{}{}'.format(line, suffix))
        node = self.code_links_node('\n'.join(lines))
        self.state.nested_parse(StringList(lines),
                                self.content_offset,
                                node)
        if 'timeout' in self.options:
            for node in node.traverse(runrole_reference):
                if node['reftype'] == 'fullnotebook':
                    node['timeout'] = self.options['timeout']
        return [node]


def setup(app):
    app.add_directive('code-links', CodeLinks)

    # Pass through containers used as markers for code links
    null = lambda self, node : None
    app.add_node(CodeLinks.code_links_node,
                 **{builder: (null, null)
                    for builder in ('html', 'latex', 'text', 'texinfo')})
    app.add_config_value('fill_notebook_timeout', 30, True)
