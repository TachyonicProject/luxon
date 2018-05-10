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

from luxon.structs.threaddict import ThreadDict

class ThreadSingleton(type):
    """Singleton MetaClass

    Ensure class is not duplicated per thread and always references initial
    instantiated object.
    """
    _instances = ThreadDict()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(ThreadSingleton, cls).__call__(*args, **kwargs)

        if hasattr(cls._instances[cls], '_singleton_init'):
            cls._instances[cls]._singleton_init

        return cls._instances[cls]

class NamedSingleton(type):
    """Singleton MetaClass

    Ensures class is singleton based on first arg name.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if len(args) > 0:
            name = args[0]
        else:
            name = None

        if name not in cls._instances:
            cls._instances[name] = {}

        if cls not in cls._instances[name]:
            cls._instances[name][cls] = super(NamedSingleton, cls).__call__(*args, **kwargs)

        if hasattr(cls._instances[name][cls], '_singleton_init'):
            cls._instances[name][cls]._singleton_init

        return cls._instances[name][cls]

class Singleton(type):
    """Singleton MetaClass

    Ensure class is not duplicated and always references initial instantiated object.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        if hasattr(cls._instances[cls], '_singleton_init'):
            cls._instances[cls]._singleton_init

        return cls._instances[cls]
