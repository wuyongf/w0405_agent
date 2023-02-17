#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys
from shutil import rmtree
from setuptools import find_packages, setup

# from rm.integration.mir200 import __version__

# Package meta-data.
NAME = 'rm.integration.mir200'
DESCRIPTION = 'Robotmanager and MiR200 Robot Integration'
URL = ''
EMAIL = 'yongfeng@willsonic.com'
AUTHOR = 'WU, Yongfeng'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.1.0'

# Required packages
REQUIRED = ['requests', 'paho-mqtt']

setup(
    name=NAME,
    # version=__version__,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    # packages=find_packages('rm.integration.mir200'),
    install_requires=REQUIRED,
    include_package_data=True,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ]
)
