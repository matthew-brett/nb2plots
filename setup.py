#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Installation script for nb2plots package '''
import os
from os.path import join as pjoin, split as psplit, splitext
import re

import setuptools
from distutils.core import setup

import versioneer

# Get install requirements from requirements.txt file
with open('requirements.txt', 'rt') as fobj:
    install_requires = [line.strip() for line in fobj
                        if line.strip() and not line[0] in '#-']
# Get any extra test requirements
with open('test-requirements.txt', 'rt') as fobj:
    test_requires = [line.strip() for line in fobj
                     if line.strip() and not line[0] in '#-']

# Requires for distutils (only used in pypi interface?)
break_ver = re.compile(r'(\S+?)(\[\S+\])?([=<>!]+\S+)')
requires = [break_ver.sub(r'\1 (\3)', req) for req in install_requires]

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


cmdclass = versioneer.get_cmdclass()
cmdclass['install_scripts'] = my_install_scripts


setup(name='nb2plots',
      version=versioneer.get_version(),
      cmdclass=cmdclass,
      description='Converting between ipython notebooks and sphinx docs',
      author='Matthew Brett',
      author_email='matthew.brett@gmail.com',
      maintainer='Matthew Brett',
      maintainer_email='matthew.brett@gmail.com',
      url='http://github.com/matthew-brett/nb2plots',
      packages=['nb2plots',
                'nb2plots.tests'],
      package_data = {'nb2plots': [
          'tests/data/*.rst',
          'tests/rst_md_files/*',
          'tests/data/*',
          'tests/proj1/*.rst',
          'tests/proj1/*.py',
          'tests/proj1/_static/*',
          'tests/otherpages/*',
      ]},
      license='BSD license',
      classifiers = [
          'Development Status :: 2 - Pre-Alpha',
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
      scripts = ['scripts/nb2plots',
                 'scripts/sphinx2nb',
                 'scripts/sphinx2py',
                 'scripts/sphinx2md',
                 'scripts/sphinx2pxml',
                 'scripts/rst2md'],
      long_description = open('README.rst', 'rt').read(),
      install_requires = install_requires,
      extras_require = {'test': test_requires}
      )
