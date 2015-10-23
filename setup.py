#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Installation script for nb2plots package '''
import os
from os.path import join as pjoin, split as psplit, splitext
import sys

# For some commands, use setuptools.
if len(set(('develop', 'bdist_egg', 'bdist_rpm', 'bdist', 'bdist_dumb',
            'install_egg_info', 'egg_info', 'easy_install', 'bdist_wheel',
            'bdist_mpkg')).intersection(sys.argv)) > 0:
    import setuptools

from distutils.core import setup

import versioneer

extra_setup_kwargs = ({} if 'setuptools' not in sys.modules else
                      dict(install_requires=['six', 'sphinx>=1.1.3']))


# See: https://github.com/matthew-brett/myscripter
from distutils.command.install_scripts import install_scripts
from distutils import log

BAT_TEMPLATE = \
r"""@echo off
REM wrapper to use shebang first line of {FNAME}
set mypath=%~dp0
set pyscript="%mypath%{FNAME}"
set /p line1=<%pyscript%
if "%line1:~0,2%" == "#!" (goto :goodstart)
echo First line of %pyscript% does not start with "#!"
exit /b 1
:goodstart
set py_exe=%line1:~2%
call "%py_exe%" %pyscript% %*
"""

class my_install_scripts(install_scripts):
    """ Install .bat wrapper for scripts on Windows """
    def run(self):
        install_scripts.run(self)
        if not os.name == "nt":
            return
        for filepath in self.get_outputs():
            # If we can find an executable name in the #! top line of the
            # script file, make .bat wrapper for script.
            with open(filepath, 'rt') as fobj:
                first_line = fobj.readline()
            if not (first_line.startswith('#!') and
                    'python' in first_line.lower()):
                log.info("No #!python executable found, skipping .bat "
                            "wrapper")
                continue
            pth, fname = psplit(filepath)
            froot, ext = splitext(fname)
            bat_file = pjoin(pth, froot + '.bat')
            bat_contents = BAT_TEMPLATE.replace('{FNAME}', fname)
            log.info("Making %s wrapper for %s" % (bat_file, filepath))
            if self.dry_run:
                continue
            with open(bat_file, 'wt') as fobj:
                fobj.write(bat_contents)


CMDCLASS = versioneer.get_cmdclass()
CMDCLASS['install_scripts'] = my_install_scripts


setup(name='nb2plots',
      version=versioneer.get_version(),
      cmdclass=CMDCLASS,
      description='Converting between ipython notebooks and sphinx docs',
      author='Matthew Brett',
      author_email='matthew.brett@gmail.com',
      maintainer='Matthew Brett',
      maintainer_email='matthew.brett@gmail.com',
      url='http://github.com/matthew-brett/nb2plots',
      packages=['nb2plots',
                'nb2plots.tests'],
      package_data = {'nb2plots': [
          'tests/data/*.ipynb',
          'tests/data/*.rst',
      ]},
      license='BSD license',
      classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Topic :: Scientific/Engineering',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Operating System :: Unix',
            'Operating System :: MacOS',
        ],
      scripts = ['scripts/nb2plots'],
      long_description = open('README.rst', 'rt').read(),
      **extra_setup_kwargs
      )
