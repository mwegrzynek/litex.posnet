
# -*- coding: UTF-8 -*-
from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

version = '1.0.0'

setup(
    name='litex.posnet',
    version=version,
    description='A simple driver for Polish fiscal printers implementing POSNET protocol',
    long_description=long_description,
    url='https://litexservice.pl',
    author=u'Michał Węgrzynek',
    author_email='mwegrzynek@litexservice.pl',
    license='GPL',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: System :: Hardware',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='posnet serial fiscal',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    namespace_packages=['litex'],
    install_requires=['pyserial', 'construct>=2.8,<3', 'pycrc'],
    dependency_links=['https://github.com/construct/construct/archive/master.zip#egg=construct-2.8.1'],
    extras_require={
        'test': ['coverage', 'nose'],
    },
    package_data={
        #'sample': ['package_data.dat'],
    }
)
