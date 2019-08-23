import ast
import re

import setuptools

from kpar import __version__

setuptools.setup(
    name = "kpar",
    version = __version__,
    url = 'https://github.com/mdipierro/kpar',
    license = 'BSD',
    author = 'Massimo Di Pierro',
    author_email = 'massimo.dipierro@gmail.com',
    maintainer = 'Massimo Di Pierro',
    maintainer_email = 'massimo.dipierro@gmail.com',
    description = 'K(onfiguration) Parameters',
    long_description = "A possible solution for describing large and complex hiararchical parameters using Python",
    long_description_content_type = "text/markdown",
    packages = ['kpar'],
    include_package_data = True,
    zip_safe = False,
    platforms = 'any',
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
