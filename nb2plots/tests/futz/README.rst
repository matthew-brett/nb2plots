#################
Futzing directory
#################

The tests are all well and good in their temporary directory, but sometimes I
need to do an actual sphinx build and check what the output is, for debugging
and so on.

I do that in this directory.  Something like::

    make init
    make html

Then I might copy some stuff into the ``proj1`` subdirectory that ``make
init`` made for me, before retrying the build.
