#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Installation script for nb2plots package '''
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


setup(name='nb2plots',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Converting between ipython notebooks and sphinx docs',
      author='Matthew Brett',
      author_email='matthew.brett@gmail.com',
      maintainer='Matthew Brett',
      maintainer_email='matthew.brett@gmail.com',
      url='http://github.com/matthew-brett/nb2plots',
      packages=['nb2plots',
                'nb2plots.tests'],
      package_data = {'nb2plots': [
          'tests/data/*.ipynb'
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
