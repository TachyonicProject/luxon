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
import sys
import inspect
from luxon.utils.imports import import_module


def profile_objects(root=None, include_obj=True):
    usage = []
    modules = sys.modules.keys()
    for module in modules:
        module = module.split('.')
        if ((root is not None and module[0] == root) or
                root is None):
            module = ".".join(module)
            py_mod = import_module(module)
            try:
                for obj, py_obj in inspect.getmembers(py_mod):
                    if not inspect.ismodule(py_obj):
                        if include_obj is True:
                            usage.append((module + '.' + obj,
                                          sys.getsizeof(py_obj),
                                          str(type(py_obj)),
                                          py_obj))
                        else:
                            usage.append((module + '.' + obj,
                                          sys.getsizeof(py_obj),
                                          str(type(py_obj))))
            except:
                pass
    return usage


def profile_mem(root=None):
    objs = profile_objects(root)
    types = {}
    found = []
    for obj in objs:
        name, size, typ, obj = obj
        if id(obj) not in found:
            found.append(id(obj))
            if typ not in types:
                types[typ] = size
            else:
                types[typ] += size
    return types
