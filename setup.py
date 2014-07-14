#!/usr/bin/env python
# -*- coding: utf-8 -*-

import versioneer
versioneer.VCS = 'git'
versioneer.versionfile_source = 'py_sonicvisualiser/_version.py'
versioneer.versionfile_build = versioneer.versionfile_source
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = 'py_sonicvisualiser-'

from setuptools import setup, find_packages

CLASSIFIERS = [
    'Intended Audience :: Science/Research',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'Programming Language :: Python',
    'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
    'Operating System :: OS Independent',
    'Topic :: Multimedia :: Sound/Audio',
    'Topic :: Multimedia :: Sound/Audio :: Analysis',
    'Topic :: Multimedia :: Sound/Audio :: Editors',
    'Topic :: Multimedia :: Sound/Audio :: Speech',
    'Topic :: Multimedia :: Sound/Audio :: Conversion',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Scientific/Engineering :: Visualization',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Text Processing :: Markup',
    ]

KEYWORDS = 'audio analysis features visualization plot annotation sonicvisualiser conversion format'

setup(
  name = "py_sonicvisualiser",
  url='https://github.com/DavidDoukhan/py_sonicvisualiser',
  description = "manipulating sonic-visualiser environment files",
  long_description = open('README.md').read(),
  author = "David Doukhan",
  author_email = "david.doukhan@gmail.com",
#  version = '0.0.1',

   # versioneer
  version=versioneer.get_version(),
  cmdclass=versioneer.get_cmdclass(),

  install_requires = [
        'setuptools',
#        'xml',
#        'bz2',
#        'wave',
        'numpy',
        'scipy'
        ],
  platforms=['OS Independent'],
  license='Gnu Public License V2',
  classifiers = CLASSIFIERS,
  keywords = KEYWORDS.split(' '),
  packages = find_packages(),
  include_package_data = True,
  # zip_safe = False,
  # scripts=['scripts/timeside-waveforms', 'scripts/timeside-launch'],
)
