# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020 Christiaan Frans Rademan <chris@fwiw.co.za>.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

import os
import sys
from importlib.machinery import SourceFileLoader

try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test as TestCommand
except ImportError:
    print('Requires `setuptools` to be installed')
    print('`pip install setuptools`')
    exit()

# DEFINE ROOT PACKAGE NAME
PACKAGE = 'luxon'

##############################################################################
# DO NOT EDIT CODE BELOW THIS POINT ##########################################
##############################################################################

cmdclass = {}
MYDIR = os.path.abspath(os.path.dirname(__file__))
CODE_DIRECTORY = os.path.join(MYDIR, PACKAGE)
DOCS_DIRECTORY = os.path.join(MYDIR, 'docs')
TESTS_DIRECTORY = os.path.join(MYDIR, 'tests')
PYTEST_FLAGS = ['--doctest-modules']
# Add the source directory to the module search path.
sys.path.insert(0, MYDIR)

# Load Metadata from PACKAGE
metadata = SourceFileLoader(
    'metadata', os.path.join(MYDIR, CODE_DIRECTORY,
                             'metadata.py')).load_module()


# Miscellaneous helper functions
def requirements(path):
    dependency = []
    if os.path.exists(os.path.join(os.path.dirname(__file__), path)):
        with open(os.path.join(os.path.dirname(__file__), path)) as req:
            dependency = req.read().splitlines()

    return dependency


def read(filename):
    """Return the contents of a file.

    :param filename: file path
    :type filename: :class:`str`
    :return: the file's content
    :rtype: :class:`str`
    """
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


class PyTestCommand(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(PYTEST_FLAGS + [TESTS_DIRECTORY])
        sys.exit(errno)


cmdclass['test'] = PyTestCommand

# define install_requires for specific Python versions
python_version_specific_requires = []

# As of Python >= 2.7 and >= 3.2, the argparse module is maintained within
# the Python standard library, we install it as a separate package
python_version_specific_requires.append('argparse')

# install-requires.txt as install_requires
# minimal dependencies to run.
install_requires = requirements('install-requires.txt')

# docs-requires.txt as docs_requires
# minimal dependencies to run.
docs_requires = requirements('docs-requires.txt')

# tests-requires.txt as tests_requires
# minimal dependencies to run.
tests_requires = requirements('tests-requires.txt')

# dependency-links.txt as dependency_links
# locations of where to find dependencies within
# install-requires.txt ie github.
# setuptools does work with url format for pip.
dependency_links = requirements('dependency-links.txt')

# See here for more options:
# <http://pythonhosted.org/setuptools/setuptools.html>
setup_dict = dict(
    name=metadata.package,
    version=metadata.version,
    author=metadata.author,
    author_email=metadata.email,
    maintainer=metadata.author,
    maintainer_email=metadata.email,
    license=metadata.license,
    url=metadata.url,
    description=metadata.description,
    long_description=read('README.rst'),
    include_package_data=True,
    classifiers=metadata.classifiers,
    packages=find_packages(exclude=(TESTS_DIRECTORY,)),
    install_requires=[] + python_version_specific_requires + install_requires,
    dependency_links=dependency_links,
    # Allow tests to be run with `python setup.py test'.
    tests_require=install_requires + tests_requires,
    cmdclass=cmdclass,
    zip_safe=False,  # don't use eggs
    entry_points={
        'console_scripts': [
            'luxon = luxon.main:entry_point'
        ],
    },
    python_requires='>=3.6',
)


def main():
    setup(**setup_dict)


if __name__ == '__main__':
    main()
