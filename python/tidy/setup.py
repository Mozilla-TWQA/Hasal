# Copyright 2013 The Servo Project Developers. See the COPYRIGHT
# file at the top-level directory of this distribution.
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

import os
from setuptools import setup, find_packages


VERSION = '0.0.3'

install_requires = [
    "flake8==2.4.1",
    "toml==0.9.1",
]

here = os.path.dirname(os.path.abspath(__file__))
# get documentation from the README and HISTORY
try:
    with open(os.path.join(here, 'README.rst')) as doc:
        readme = doc.read()
except:
    readme = ''

try:
    with open(os.path.join(here, 'HISTORY.rst')) as doc:
        history = doc.read()
except:
    history = ''

long_description = readme + '\n\n' + history

if __name__ == '__main__':
    setup(
        name='tidy',
        version=VERSION,
        description='The tidy is used to check source of Hasal.',
        long_description=long_description,
        keywords='mozilla hasal tidy ',
        author='The Hasal Project Developers',
        author_email='tw-qa@mozilla.com',
        url='https://github.com/Mozilla-TWQA/Hasal',
        packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
        package_data={},
        install_requires=install_requires,
        zip_safe=False,
        entry_points={
            'console_scripts': [
                'tidy=tidy.tidy:scan'
            ],
        },
    )
