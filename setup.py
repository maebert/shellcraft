#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import re


with open("src/shellcraft/__init__.py") as f:
    VERSION = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M).group(1)

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = ['Click>=6.0', 'protobuf>=3.3.0', 'future>=0.16.0', 'PyYAML>=3.12']

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='shellcraft',
    version=VERSION,
    description="ShellCraft is a command line based crafting game.",
    long_description=readme,
    author="Manuel Ebert",
    author_email='manuel@1450.me',
    url='https://github.com/maebert/shellcraft',
    packages=find_packages("src"),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'shellcraft=shellcraft.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='shellcraft',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 3',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Simulation'
    ],
    test_suite='tests',
    tests_require=test_requirements
)
