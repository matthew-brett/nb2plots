# -*- coding: utf-8 -*-
"""Simple Markdown writer for reStructuredText.

"""

from __future__ import unicode_literals

__docformat__ = 'reStructuredText'

from docutils import frontend, nodes, writers, languages


class Writer(writers.Writer):

    supported = ('markdown',)
    """Formats this writer supports."""

    output = None
    """Final translated form of `document`."""

    # Add configuration settings for additional Markdown flavours here.
    settings_spec = (
        'Markdown-Specific Options',
        None,
        (('Extended Markdown syntax.',
          ['--extended-markdown'],
          {'default': 0, 'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ('Strict Markdown syntax. Default: true',
          ['--strict-markdown'],
          {'default': 1, 'action': 'store_true',
           'validator': frontend.validate_boolean}),))

    def __init__(self):
        writers.Writer.__init__(self)
        self.translator_class = Translator

    def translate(self):
        visitor = self.translator_class(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.astext()


class IndentLevel(object):
    """ Class to hold text being written for a certain indentation level

    For example, all text in list_elements need to be indented.  A list_element
    creates one of these indentation levels, and all text contained in the
    list_element gets written to this IndentLevel.  When we leave the
    list_element, we ``write`` the text with suitable prefixes to the next
    level down, which might be the base of the document (document body) or
    another indentation level, if this is - for example - a nested list.

    In most respects, IndentLevel behaves like a list.
    """
    def __init__(self, base, prefix, first_prefix=None):
        self.base = base  # The list to which we eventually write
        self.prefix = prefix  # Text prepended to lines
        # Text prepended to first list
        self.first_prefix = prefix if first_prefix is None else first_prefix
        # Our own list to which we append before doing a ``write``
        self.content = []

    def append(self, new):
        self.content.append(new)

    def __getitem__(self, index):
        return self.content[index]

    def __len__(self):
        return len(self.content)

    def __bool__(self):
        return len(self) != 0

    def write(self):
        """ Add ``self.contents`` with current ``prefix`` and ``first_prefix``

        Add processed ``self.contents`` to ``self.base``.  The first line has
        ``first_prefix`` prepended, further lines have ``prefix`` prepended.

        Empty (all whitepsace) lines get written as bare carriage returns, to
        avoid ugly extra whitespace.
        """
        string = ''.join(self.content)
        lines = string.splitlines(True)
        if len(lines) == 0:
            return
        texts = [self.first_prefix + lines[0]]
        for line in lines[1:]:
            if line.strip() == '':  # avoid prefix for empty lines
                texts.append('\n')
            else:
                texts.append(self.prefix + line)
        self.base.append(''.join(texts))


class Translator(nodes.NodeVisitor):

    std_indent = '    '

    # Customise Markdown syntax here. Still need to add term,
    # indent, problematic etc...
    syntax_defs = {
        'emphasis': ('*', '*'),   # Could also use ('_', '_')
        'problematic' : ('\n\n', '\n\n'),
        'strong' : ('**', '**'),  # Could also use ('__', '__')
        'literal' : ('`', '`'),
        'math' : ('$', '$'),
        'subscript' : ('<sub>', '</sub>'),
        'superscript' : ('<sup>', '</sup>'),
    }

    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        self.settings = settings = document.settings
        lcode = settings.language_code
        self.language = languages.get_language(lcode, document.reporter)
        self.head, self.body, self.foot = [], [], []
        # Reset attributes modified by reading
        self.reset()
        # Lookup table to get section list from name
        self._lists = dict(head=self.head,
                           body=self.body,
                           foot=self.foot)

    def reset(self):
        """ Initialize object for fresh read """
        self.head[:] = []
        self.body[:] = []
        self.foot[:] = []

        # Current section heading level during writing
        self.section_level = 0

        # FIFO list of list prefixes, while writing nested lists.  Each element
        # corresponds to one level of nesting.  Thus ['1. ', '1. ', '* '] would
        # occur when writing items of an unordered list, that is nested within
        # an ordered list, that in turn is nested in another ordered list.
        self.list_prefixes = []

        # FIFO list of indentation levels.  When we are writing a block of text
        # that should be indented, we create a new indentation level.  We only
        # write the text when we leave the indentation level, so we can insert
        # the correct prefix for every line.
        self.indent_levels = []

        ##TODO docinfo items can go in a footer HTML element (store in self.foot).
        self._docinfo = {
            'title' : '',
            'subtitle' : '',
            'author' : [],
            'date' : '',
            'copyright' : '',
            'version' : '',
            }

    # Utility methods

    def astext(self):
        """Return the final formatted document as a string."""
        self.drop_trailing_eols()
        return ''.join(self.head + self.body + self.foot)

    def drop_trailing_eols(self):
        # Drop trailing carriage return from ends of lists
        for L in self._lists.values():
            if L and L[-1] == '\n':
                L.pop()

    def deunicode(self, text):
        text = text.replace(u'\xa0', '\\ ')
        text = text.replace(u'\u2020', '\\(dg')
        return text

    def ensure_eol(self):
        """Ensure the last line in current base is terminated by new line."""
        out = self.get_current_output()
        if out and out[-1] and out[-1][-1] != '\n':
            out.append('\n')

    def get_current_output(self, section='body'):
        """ Get list or IndentLevel to which we are currently writing """
        return (self.indent_levels[-1] if self.indent_levels
                else self._lists[section])

    def add(self, string, section='body'):
        """ Add `string` to `section` or current output

        Parameters
        ----------
        string : str
            String to add to output document
        section : {'body', 'head', 'foot'}, optional
            Section of document that generated text should be appended to, if
            not already appending to an indent level.
        """
        self.get_current_output(section).append(string)

    def add_section(self, string, section='body'):
        """ Add `string` to `section` regardless of current output

        Can be useful when forcing write to header or footer.

        Parameters
        ----------
        string : str
            String to add to output document
        section : {'body', 'head', 'foot'}, optional
            Section of document that generated text should be appended to.
        """
        self._lists[section].append(string)

    def start_level(self, prefix, first_prefix=None, section='body'):
        """ Create a new IndentLevel with `prefix` and `first_prefix`
        """
        base = (self.indent_levels[-1].content if self.indent_levels else
                self._lists[section])
        level = IndentLevel(base, prefix, first_prefix)
        self.indent_levels.append(level)

    def finish_level(self):
        """ Remove most recent IndentLevel and write contents
        """
        level = self.indent_levels.pop()
        level.write()

    # Node visitor methods

    def visit_Text(self, node):
        text = node.astext()
        self.add(text)

    def depart_Text(self, node):
        pass

    def visit_comment(self, node):
        self.add('<!-- ' + node.astext() + ' -->\n')
        raise nodes.SkipNode

    def visit_docinfo_item(self, node, name):
        if name == 'author':
            self._docinfo[name].append(node.astext())
        else:
            self._docinfo[name] = node.astext()
        raise nodes.SkipNode

    def visit_document(self, node):
        pass

    def depart_document(self, node):
        pass

    def visit_emphasis(self, node):
        self.add(self.syntax_defs['emphasis'][0])

    def depart_emphasis(self, node):
        self.add(self.syntax_defs['emphasis'][1])

    def visit_paragraph(self, node):
        pass

    def depart_paragraph(self, node):
        self.ensure_eol()
        self.add('\n')

    def visit_math_block(self, node):
        self.add('$$\n')

    def depart_math_block(self, node):
        self.ensure_eol()
        self.add('$$\n\n')

    def visit_literal_block(self, node):
        code_type = node['classes'][1] if 'code' in node['classes'] else ''
        self.add('```' + code_type + '\n')

    def depart_literal_block(self, node):
        self.ensure_eol()
        self.add('```\n\n')

    def visit_block_quote(self, node):
        self.start_level('> ')

    def depart_block_quote(self, node):
        self.finish_level()

    def visit_problematic(self, node):
        self.add(self.syntax_defs['problematic'][0])

    def depart_problematic(self, node):
        self.add(self.syntax_defs['problematic'][1])

    def visit_section(self, node):
        self.section_level += 1

    def depart_section(self, node):
        self.section_level -= 1

    def visit_strong(self, node):
        self.add(self.syntax_defs['strong'][0])

    def depart_strong(self, node):
        self.add(self.syntax_defs['strong'][1])

    def visit_literal(self, node):
        self.add(self.syntax_defs['literal'][0])

    def depart_literal(self, node):
        self.add(self.syntax_defs['literal'][1])

    def visit_math(self, node):
        self.add(self.syntax_defs['math'][0])

    def depart_math(self, node):
        self.add(self.syntax_defs['math'][1])

    def visit_enumerated_list(self, node):
        self.list_prefixes.append('1. ')

    def depart_enumerated_list(self, node):
        self.list_prefixes.pop()

    def visit_bullet_list(self, node):
        self.list_prefixes.append('* ')

    depart_bullet_list = depart_enumerated_list

    def visit_list_item(self, node):
        first_prefix = self.list_prefixes[-1]
        prefix = ' ' * len(first_prefix)
        self.start_level(prefix, first_prefix)

    def depart_list_item(self, node):
        self.finish_level()

    def visit_subscript(self, node):
        self.add(self.syntax_defs['subscript'][0])

    def depart_subscript(self, node):
        self.add(self.syntax_defs['subscript'][1])

    def visit_subtitle(self, node):
        if isinstance(node.parent, nodes.document):
            self.visit_docinfo_item(node, 'subtitle')
            raise nodes.SkipNode

    def visit_superscript(self, node):
        self.add(self.syntax_defs['superscript'][0])

    def depart_superscript(self, node):
        self.add(self.syntax_defs['superscript'][1])

    def visit_system_message(self, node):
        # TODO add report_level
        #if node['level'] < self.document.reporter['writer'].report_level:
        #    Level is too low to display:
        #    raise nodes.SkipNode
        attr = {}
        if node.hasattr('id'):
            attr['name'] = node['id']
        if node.hasattr('line'):
            line = ', line %s' % node['line']
        else:
            line = ''
        self.add('"System Message: %s/%s (%s:%s)"\n'
            % (node['type'], node['level'], node['source'], line))

    def depart_system_message(self, node):
        pass

    def visit_title(self, node):
        if self.section_level == 0:
            self.add_section('# ', section='head')
            self._docinfo['title'] = node.astext()
        else:
            self.add((self.section_level + 1) * '#' + ' ')

    def depart_title(self, node):
        self.ensure_eol()
        self.add('\n')

    def visit_transition(self, node):
        # Simply replace a transition by a horizontal rule.
        # Could use three or more '*', '_' or '-'.
        self.add('\n---\n\n')
        raise nodes.SkipNode

    def visit_reference(self, node):
        if 'refuri' not in node:
            return
        self.add('[{0}]({1})'.format(node.astext(), node['refuri']))
        raise nodes.SkipNode

    def depart_reference(self, node):
        pass

    def visit_target(self, node):
        pass

    def depart_target(self, node):
        pass

    def visit_inline(self, node):
        pass

    def depart_inline(self, node):
        pass

# The following code adds visit/depart methods for any reStructuredText element
# which we have not explicitly implemented above.

# All reStructuredText elements:
rst_elements = ('abbreviation', 'acronym', 'address', 'admonition',
    'attention', 'attribution', 'author', 'authors', 'block_quote', 
    'bullet_list', 'caption', 'caution', 'citation', 'citation_reference', 
    'classifier', 'colspec', 'comment', 'compound', 'contact', 'container', 
    'copyright', 'danger', 'date', 'decoration', 'definition',
    'definition_list', 'definition_list_item', 'description', 'docinfo', 
    'doctest_block', 'document', 'emphasis', 'entry', 'enumerated_list', 
    'error', 'field', 'field_body', 'field_list', 'field_name', 'figure', 
    'footer', 'footnote', 'footnote_reference', 'generated', 'header', 
    'hint', 'image', 'important', 'inline', 'label', 'legend', 'line', 
    'line_block', 'list_item', 'literal', 'literal_block', 'math', 
    'math_block', 'note', 'option' ,'option_argument', 'option_group', 
    'option_list', 'option_list_item', 'option_string', 'organization', 
    'paragraph', 'pending', 'problematic', 'raw', 'reference', 'revision', 
    'row', 'rubric', 'section', 'sidebar', 'status', 'strong', 'subscript', 
    'substitution_definition', 'substitution_reference', 'subtitle', 
    'superscript', 'system_message', 'table', 'target', 'tbody,' 'term', 
    'tgroup', 'thead', 'tip', 'title', 'title_reference', 'topic', 
    'transition','version','warning',)

##TODO Eventually we should silently ignore unsupported reStructuredText 
##     constructs and document somewhere that they are not supported.
##     In the meantime raise a warning *once* for each unsupported element.
_warned = set()

def visit_unsupported(self, node):
    node_type = node.__class__.__name__
    if node_type not in _warned:
        self.document.reporter.warning('The ' + node_type + \
            ' element is not supported.')
        _warned.add(node_type)
    raise nodes.SkipNode

for element in rst_elements:
    if not hasattr(Translator, 'visit_' + element):
        setattr(Translator, 'visit_' + element , visit_unsupported)

