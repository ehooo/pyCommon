from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

import sys

setup(name              = 'pyCommon',
      version           = '0.0.1',
      author            = 'Victor Torre',
      author_email      = 'web.ehooo@gmail.com',
      description       = 'Collection of usefull class, functions and tools',
      license           = 'GPLv2',
      url               = 'https://github.com/ehooo/pyCommon',
      install_requires  = [],
      packages          = find_packages(),
      classifiers = [
          'Development Status :: 1 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          ],
    )
