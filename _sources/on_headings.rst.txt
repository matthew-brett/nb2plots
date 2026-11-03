.. _nbplot-heading-levels:

#############################
On heading levels in Markdown
#############################

``nb2plots`` writes Markdown documents from ReST documents.  In order to do
this, it has to work out the intended heading levels of the various sections
in the ReST.

Because there are various ways of doing this, ``nb2plots`` has a configuration
option ``nbplot_heading_levels``, and a command line flag
``--nbplot-heading-levels``, for you to choose your preferred solution.

**********
Background
**********

Heading levels in ReST source
=============================

ReST, by design, defines section headings relative to the other section
headings in the document.  The top-level heading is, by definition, the first,
and ReST identifies other heading levels relative to previous ones.  Below is
a ReST document with the heading levels noted by ``<- markers``::

    Heading  <- level 1
    +++++++

    Text.

    Section 1 <- level 2
    =========

    Text

    Subsection A <- level 3
    ------------

    More text.

    Subsection B <- level 3
    ------------

    More text.

    Section 2 <- level 2 (same heading style as Section 1)
    =========

    Final text.

In this first case, we have a single top-level heading (STLH), but we could
also have multiple headings at the top-level::

    Section 1  <- level 1
    =========

    Text

    Subsection A  <- level 2
    ------------

    More text.

    Subsection B <- level 2
    ------------

    More text.

    Section 2 <- level 1
    =========

    Final text.

This document has multiple top-level headings (MTLH).

The heading levels we've identified here are those according to the *source*;
that is, in terms of the ReST standard, and before any further processing
takes place.

Call the levels marked above — *source-levels*.

Heading levels in ReST and Markdown
===================================

We have seen that ReST heading levels are *relative* to the other headings in
the document.  In contrast, Markdown heading levels are absolute: ``#
Heading`` means top-level heading, wherever it is in the document, and ``##
Section`` is a second level heading, wherever it is in the document.

Heading levels in Doctrees
==========================

Docutils and Sphinx (via Docutils) parse ReST documents into `Doctrees
<https://docutils.sourceforge.io/docs/ref/doctree.html>`_, abstract
representations of the document contents.

This parsing, via Docutils internals, and via Docutils and Sphinx extensions,
can modify heading levels.

In fact, Docutils, by default, does one such modification, called the
`DocTitle transform
<https://docutils.sourceforge.io/docs/api/transforms.html#doctitle>`_. This
transform occurs when the Docutils setting `doctitle_xform
<https://docutils.sourceforge.io/docs/user/config.html#doctitle-xform>`_ is
True, which is the default for standard Docutils parsing.

The transform uses an algorithm to determine whether a top-level heading could
be a title.  The algorithm has various criteria for this decision, but the
most important for our purposes is that a heading can only be a title when
it is the only heading at the top-level. Thus Docutils does detect a title for
the STLH document above, and does not for the MTLH document.

In general, call this the Docutils Title (DT) test — we'll say DT:True for a
document where this algorithm would detect a title, and DT:False otherwise.

In standard Docutils parsing --- as used, for example, by our ``rst2md``
command --- for a DT:True document, Docutils modifies the Doctree to:

1. Label the top-level heading as the Title and
2. Promote all the other headings by one level.

We'll use DT:True to mean that the DocTitle algorithm *would detect a title*,
if run.  Of course, by default, in Sphinx, we do not run the algorithm, but we
could label a ReST document DT:True even if it was parsed by Sphinx, meaning
that it would pass the DocTitle test.

Thus the STLH document above is DT:True (it would pass the DocTitle test,
meaning, there is a plausible heading for a title).  The MTLH document is
DT:False.

1. The STLH document above gives DT:True.
2. The MTLH document above gives DT:False.

(The algorithm uses additional criteria besides single / multiple top-level
headings.  As a first-pass summary: a single top-level heading, with no body
text before it, gives DT:True; multiple top-level headings give DT:False).

Thus, for the STLH (DT:True) document above, with standard Docutils parsing,
``Heading`` becomes a Title, not a section level, and ``Section 1`` becomes a
level 1 section rather than a level 2 section, and so on.  Call this
Title-Section-Level-Promotion (TSLP).

Note, though, that Sphinx specifically sets ``doctitle_xform`` to ``False``,
so does not run the DocTitle transform and so (unless some other extension
intervenes) does not detect a title, and does not apply TSLP.  So although the
document, such as STLH, is DT:True, because the algorithm is not run, the
title is not detected, and the resulting Doctree does not undergo TSLP.

The problem for Nb2plots is that we use both standard Docutils parsing (via
e.g. the ``rst2md`` command line utility), and Sphinx-configured Docutils
parsing (via Sphinx builds).  Call these Docutils-parsed (DP) documents vs
Sphinx-parsed (SP) documents.  The DP documents will undergo the level
promotion above (TSLP) when the DT:True criteria are met, but TSLP cannot
happen through Sphinx-parsing (SP) --- and so the resulting doctrees will
differ, in DT:True cases, depending whether we applied DP or SP.

These considerations put Nb2plots in a bind, because it has to deal with both
DP and SP, in the DT:True and DT:False cases, in order to generate matching
Markdown (absolute) heading levels.  Because there are various ways of dealing
with these differences, we give you the choice with a configuration setting
(for Sphinx) and a matching command-line setting (for utilities such as
``rst2md``).

***********
The options
***********

The options for this setting are:

* ``source``
* ``infer`` (the default).
* ``demote``

In what follows --- for DP / DT:True Doctrees, we *always* reverse the TSLP
(section promotion), by *demoting* the detected title to heading level 1,
level 1 to level 2 and so on.

Call this DP / DT:True demotion.  It merely returns the parsed Doctree to the
heading levels implied by the source, as noted above.  You can't turn DP /
DT:True demotion off in any option, as we could see little sense in doing so.
The options therefore differ in their treatment of the other results, which
are:

* Docutils-parsed (DP) / title not detected (DT:False) = DP / DT:False
* Sphinx-parsed (SP) / title detectable = SP / DT:True
* SP / DT:False

``source``
==========

This option follows the heading levels, as implied by the ReST source.  As we
always apply DP / DT:True demotion, this means that documents with a single
top-level heading have a single ``#`` heading in Markdown, and sections at the
next level down get ``##`` Markdown headings.  It does mean that documents
with multiple headings at the top level, via Docutils (DP) or Sphinx (SP),
have multiple top-level (``#``) Markdown headings.

In the table below, TLH means top-level heading(s), 2LH is second-level
heading(s).

.. list-table::
   :header-rows: 1

   * - Parser
     - DT:True, TLH
     - DT:True, 2LH
     - DT:False, TLH
     - DT:False, 2LH
   * - **Docutils (DP)**
     - ``#``
     - ``##``
     - ``#``
     - ``##``
   * - **Sphinx (SP)**
     - ``#``
     - ``##``
     - ``#``
     - ``##``

``infer``
=========

The idea of this option is to work out (infer) whether this is a document with
a title or not.  If there is no title, it demotes the top-level headings to the
second Markdown level (``##``) in order to avoid having multiple top-level
(``#``) headings.

In order to do this, we run the title detection algorithm on the Sphinx-parsed
(SP) documents, to detect DT:True or DT:False for the SP documents.

For both DP / DT:False and SP / DT:False documents, we demote the heading
levels by 1 level.

As for all the options, we reverse the DP / DT:True heading promotion, to make
DP documents equivalent to SP documents.

.. list-table::
   :header-rows: 1

   * - Parser
     - DT:True, TLH
     - DT:True, 2LH
     - DT:False, TLH
     - DT:False, 2LH
   * - **DP**
     - ``#``
     - ``##``
     - ``##``
     - ``###``
   * - **SP**
     - ``#``
     - ``##``
     - ``##``
     - ``###``

``demote``
==========

Finally, for back-compatibility, we have an option that always demotes
headings by one level.  This was the behavior in Nb2plots versions < 0.8.

The demotion undoes the DP / DT:True promotion in the usual way, and means
that documents with multiple top-level headings (DT:False) always start at
Markdown heading level ``##``.

The problem with this option is that a standard DT:True document, in Sphinx,
has a top-level heading at ``##`` level instead of ``#``; its second level
headings are ``###`` instead of ``##`` and so on.

.. list-table::
   :header-rows: 1

   * - Parser
     - DT:True, TLH
     - DT:True, 2LH
     - DT:False, TLH
     - DT:False, 2LH
   * - **DP**
     - ``#``
     - ``##``
     - ``##``
     - ``###``
   * - **SP**
     - ``##``
     - ``###``
     - ``##``
     - ``###``

We guess you will only want the ``demote`` option if you need
back-compatibility with previous Nb2plots versions.
