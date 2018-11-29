# -*- coding: utf-8 -*-
# Copyright (c) 2018 Christiaan Frans Rademan.
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
import imp
import glob
import shutil
from distutils import cmd

if not sys.version_info >= (3, 5):
    print('Requires python version 3.5 or higher')
    exit()
try:
    from setuptools import setup, Extension, find_packages
    from setuptools.command.test import test as TestCommand
except ImportError:
    print('Requires `setuptools` to be installed')
    print('`pip install setuptools`')
    exit()

# DEFINE ROOT PACKAGE NAME
PACKAGE = 'luxon'


###############################################################################
# DO NOT EDIT CODE BELOW THIS POINT ###########################################
###############################################################################

cmdclass = {}
MYDIR = os.path.abspath(os.path.dirname(__file__))
CODE_DIRECTORY = os.path.join(MYDIR, PACKAGE)
DOCS_DIRECTORY = os.path.join(MYDIR, 'docs')
TESTS_DIRECTORY = os.path.join(MYDIR, 'tests')
PYTEST_FLAGS = ['--doctest-modules']
# Add the source directory to the module search path.
sys.path.insert(0, MYDIR)

# Load Metadata from PACKAGE
metadata = imp.load_source(
    'metadata', os.path.join(MYDIR, CODE_DIRECTORY, 'metadata.py'))


# Miscellaneous helper functions
def requirements(path):
    dependency = []
    if os.path.exists(os.path.join(os.path.dirname(__file__), path)):
        with open(os.path.join(os.path.dirname(__file__), path)) as req:
            dependency = req.read().splitlines()

    return dependency


def list_modules(path, ext='py'):
    filenames = glob.glob(os.path.join(path, '*.%s' % ext))

    module_names = []
    for name in filenames:
        module, ext = os.path.splitext(os.path.basename(name))
        if module != '__init__':
            module_names.append(module)

    return module_names


def list_packages(package):
    path = os.path.join(MYDIR, package)
    packages = []

    scan_dir = os.path.join(path)
    top_dir = "/" + "/".join(scan_dir.strip('/').split('/')[:-1])

    for directory, directories, files in os.walk(scan_dir):
        if '__init__.py' in files:
            packages.append((os.path.relpath(directory,
                                             top_dir).replace('/', '.')))

    return packages


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


class CleanCommand(cmd.Command):
    """A custom command to run Pylint on all Python source files."""

    description = 'run source clean-up'
    user_options = []

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass

    def run(self):
        """Run command."""
        if os.path.exists(os.path.join(MYDIR, 'build')):
            print("Removing Build")
            shutil.rmtree(os.path.join(MYDIR, 'build'))

        if os.path.exists(os.path.join(MYDIR, '.eggs')):
            print("Removing .eggs")
            shutil.rmtree(os.path.join(MYDIR, '.eggs'))

        def clean(diretory, files):
            # __pyc__
            filenames = glob.glob(os.path.join(directory, '%s' %
                                               (files,)))
            for filename in filenames:
                print("Removing %s" % filename)
                if os.path.isdir(filename):
                    shutil.rmtree(filename)
                else:
                    os.remove(filename)

        for directory, directories, files in os.walk(os.path.join(MYDIR,
                                                                  PACKAGE)):
            clean(directory, '__pycache__')
            clean(directory, '*.pyc')
            clean(directory, '*.so')


# Add Clean command
cmdclass['clean'] = CleanCommand


class CythonizeCommand(cmd.Command):
    """A custom command to run Pylint on all Python source files."""

    description = 'build cython source c files'
    user_options = []

    def initialize_options(self):
        """Set default values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass

    def run(self):
        """Run command."""
        try:
            from Cython.Build import cythonize
            files = []
            for package in list_packages(PACKAGE):
                for module in list_modules(os.path.join(MYDIR,
                                                        *package.split('.'))):
                    files.append(os.path.join(*(package.split('.') +
                                                [module + '.py'])))

            cythonize(files)

        except ImportError:
            print('No Cython installed')


# Add Clean command
cmdclass['cythonize'] = CythonizeCommand

# CYTHON / C sources compile
try:
    from Cython.Distutils import build_ext

    ext_modules = [
        Extension(
            package + '.' + module,
            [os.path.join(*(package.split('.') + [module + '.py']))]
        )
        for package in list_packages(PACKAGE)
        for module in list_modules(os.path.join(MYDIR, *package.split('.')))
    ]

    cmdclass['build_ext'] = build_ext
except ImportError:
    ext_modules = []
    print('\nNOTE: Cython not installed. '
          'Luxon will still work fine, but may run '
          'slower.\n')

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
    ext_modules=ext_modules,
    zip_safe=False,  # don't use eggs
    entry_points={
        'console_scripts': [
            'luxon = luxon.main:entry_point'
        ],
    },
    python_requires='>=3.6'
)


def main():
    setup(**setup_dict)


if __name__ == '__main__':
    main()
