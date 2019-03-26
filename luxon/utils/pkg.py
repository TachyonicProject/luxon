# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Christiaan Frans Rademan.
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
import importlib.util
from pkg_resources import (resource_stream, resource_listdir,
                           resource_isdir, resource_exists,
                           iter_entry_points)

from luxon.utils.singleton import NamedSingleton
from luxon.utils.imports import import_module
from luxon.utils.files import mkdir, f_exists, is_dir
from luxon.exceptions import NotFoundError


class EntryPoints(metaclass=NamedSingleton):
    def __init__(self, name):
        self.named_objects = {}
        for entry_point in iter_entry_points(group=name):
            self.named_objects.update({entry_point.name: entry_point.load()})

    def __getattr__(self, name):
        try:
            return self.named_objects[name]
        except KeyError:
            raise AttributeError(name) from None

    def __getitem__(self, name):
        try:
            return self.named_objects[name]
        except KeyError:
            raise NotFoundError("Entry Point '%s' not found"
                                % name) from None

    def __iter__(self):
        return iter(self.named_objects)


class Module(object):
    """Imports installed module and performs actions on it

    Args:
        module (str): Module import path definition.
    """
    def __init__(self, module):
        try:
            import_module(module)
            self._module = module
        except ImportError:
            raise ImportError(module) from None

    def exists(self, path, error=False):
        """Does the resource exist

        Args:
            path (str): resource location
        """
        try:
            val = resource_exists(self._module, path)
            if val is False and error is True:
                raise FileNotFoundError('%s/%s' % (self._module,
                                                   path,)) from None
            return val
        except ImportError:
            raise ImportError(self._module) from None

    def read(self, path):
        """Returns resource as a string

        Args:
            path (str): resource location
        """
        try:
            self.exists(path, True)
            with resource_stream(self._module,
                                 path) as res:
                return res.read()
        except ImportError:
            raise ImportError(self._module) from None

    def file(self, path):
        """Returns resource as a string

        Args:
            path (str): resource location
        """
        try:
            self.exists(path, True)
            return resource_stream(self._module,
                                   path)
        except ImportError:
            raise ImportError(self._module) from None

    def list(self, path):
        """List directories in the resource

        Args:
            path (str): resource location
        """
        try:
            self.exists(path, True)
            return resource_listdir(self._module, path)

        except ImportError:
            raise ImportError(self._module) from None

    def is_dir(self, path):
        """Is the resource a directory

        Args:
            path (str): resource location
        """
        try:
            self.exists(path, True)
            return resource_isdir(self._module, path)
        except ImportError:
            raise ImportError(self._module) from None

    def is_file(self, path):
        """Is the resource a file

        Args:
            path (str): resource location
        """
        try:
            self.exists(path, True)
            if resource_isdir(self._module, path):
                return False
        except ImportError:
            raise ImportError(self._module) from None

    def walk(self, path):
        """Walk through the resource

        Args:
            path (str): resource location
        """
        try:
            self.exists(path, True)

            def _walk(real_path, walk_path):
                files = []
                directory = self.list(real_path)
                for f in directory:
                    file_path = real_path.rstrip('/') + '/' + f
                    file_walk_path = walk_path.rstrip('/') + '/' + f
                    if self.is_dir(file_path):
                        files.append(file_walk_path)
                        files += _walk(file_path, file_walk_path)
                    else:
                        files.append(file_walk_path)
                return files

            return _walk(path, '')

        except ImportError:
            raise ImportError(self._module) from None

    def copy(self, src, dst, new_extension=None):
        """Copy the resource

        Args:
            src (str): resource location
            dst (str): destination
        """
        try:
            self.exists(src, True)

            if self.is_dir(src):
                mkdir(dst, recursive=True)

                real_src = src
                walk_files = self.walk(real_src)
                for walk_file in walk_files:
                    real_src = src.rstrip('/') + '/' + walk_file.strip('/')
                    real_dst = dst.rstrip('/') + '/' + walk_file.strip('/')
                    if self.is_dir(real_src):
                        mkdir(real_dst, recursive=True)
                    else:
                        content = self.read(real_src)
                        if new_extension is not None and f_exists(real_dst):
                            real_dst += "." + new_extension.strip('.')

                        with open(real_dst, 'wb') as new_file:
                            new_file.write(content)
            else:
                content = self.read(src)
                src_file = src.strip('/').split('/')[-1]
                if is_dir(dst):
                    dst = dst.rstrip('/') + '/' + src_file

                if new_extension is not None and f_exists(dst):
                    dst += "." + new_extension.strip('.')

                with open(dst, 'wb') as new_file:
                    new_file.write(content)

        except ImportError:
            raise ImportError(self._module) from None


def exists(package):
    if importlib.util.find_spec(package) is None:
        return False
    return True
