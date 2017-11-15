#!/usr/bin/env python
# -*- coding:utf-8 -*-

# from distutils.sysconfig import get_python_lib
from __future__ import print_function

import os
import sys
import shutil
from setuptools import setup, find_packages


def validate_pywin32():
    try:
        import win32gui  # NOQA
        import win32con  # NOQA
    except ImportError as e:
        print(e)
        sys.exit("Please make sure you already install the pywin32 properly. You can download the latest version from here https://sourceforge.net/projects/pywin32/")

#
# Clean up some critical files which will crash the program
#
clean_file_list = [
    os.path.join('ejenti', 'ejenti.pyc'),
]

for clean_file in clean_file_list:
    print('Checking {} ... '.format(clean_file), end='')
    if os.path.exists(clean_file):
        print('found')
        print('Removing {} ... '.format(clean_file), end='')
        if os.path.isfile(clean_file):
            os.remove(clean_file)
        elif os.path.isdir(clean_file):
            shutil.rmtree(clean_file)
        print('done')
    else:
        print('not found')

#
# Requirement files
#
DEFAULT_REQUIREMENT_DOC = "requirements.txt"
DEFAULT_REQUIREMENT_EJENTI_DOC = os.path.join("ejenti", "requirements.txt")
DEFAULT_REQUIREMENT_DOC_FOR_WIN = "requirements_windows.txt"
DEFAULT_REQUIREMENT_DOC_FOR_MAC = "requirements_mac.txt"

# platform dependencies
# System                platform value
# Linux (2.x and 3.x)   'linux2'
# Windows               'win32'
# Windows/Cygwin        'cygwin'
# Mac OS X              'darwin'
# OS/2                  'os2'
# OS/2 EMX              'os2emx'
# RiscOS                'riscos'
# AtheOS                'atheos'

# dependencies
with open(DEFAULT_REQUIREMENT_DOC) as f:
    deps = f.read().splitlines()

with open(DEFAULT_REQUIREMENT_EJENTI_DOC) as f_ejenti:
    deps.extend(f_ejenti.read().splitlines())

if sys.platform == 'win32':
    if os.path.exists(DEFAULT_REQUIREMENT_DOC_FOR_WIN):
        with open(DEFAULT_REQUIREMENT_DOC_FOR_WIN) as fh_win:
            deps.extend(fh_win.read().splitlines())
    validate_pywin32()


elif sys.platform == 'darwin':
    if os.path.exists(DEFAULT_REQUIREMENT_DOC_FOR_MAC):
        with open(DEFAULT_REQUIREMENT_DOC_FOR_MAC) as fh_mac:
            deps.extend(fh_mac.read().splitlines())

version = "0.1.0"


# main setup script
setup(
    name="Hasal",
    version=version,
    description="Performance test on google doc",
    author="Mozilla Taiwan",
    author_email="tw-qa@mozilla.com",
    license="MPL",
    install_requires=deps,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False
)
