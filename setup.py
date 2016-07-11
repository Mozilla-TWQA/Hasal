#!/usr/bin/env python
# -*- coding:utf-8 -*-

# from distutils.sysconfig import get_python_lib
import os
import platform
from setuptools import setup, find_packages

DEFAULT_REQUIREMENT_DOC = "requirements.txt"
DEFAULT_REQUIREMENT_DOC_FOR_WIN = "requirements_windows.txt"
DEFAULT_REQUIREMENT_DOC_FOR_MAC = "requirements_mac.txt"



# dependencies
with open(DEFAULT_REQUIREMENT_DOC) as f:
    deps = f.read().splitlines()

if platform.system().lower() == "windows":
    if os.path.exists(DEFAULT_REQUIREMENT_DOC_FOR_WIN):
        with open(DEFAULT_REQUIREMENT_DOC_FOR_WIN) as fh_win:
            deps.extend(fh_win.read().splitlines())
elif platform.system().lower() == "darwin":
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
