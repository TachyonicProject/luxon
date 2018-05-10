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
import functools

class classproperty(property):
    """Similar to property decorator, but allows class-level properties.

    Using @classproperty as a decorator for a member,
    that member can be called like a class attribute

    Example:
        .. code:: python

            class test():

                _nug = "Default"

                def __init__(self,x):
                    self._nug = x

                @classproperty
                def nug(self):
                    return self._nug

               # or use it like a wrapper
               # although it only takes a getter
               # so as to make a read only property
               # nug = classproperty(nug)


            print(test.nug)
            test._nug = "TEST"
            print(test.nug)

            outputs:

            Default
            TEST


    | Class Method -> test.fnc_1()
    | Property -> test().fnc_2
    | Class Property -> test.fnc_3

    """
    def __new__(cls, fget=None, doc=None):
        if fget is None:
            def wrapper(func):
                return cls(func)

            return wrapper

        return super(classproperty, cls).__new__(cls)

    def __init__(self, fget, doc=None):
        fget = self._fget_wrapper(fget)

        super(classproperty, self).__init__(fget=fget, doc=doc)

        if doc is not None:
            self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if objtype is not None:
            val = self.fget.__wrapped__(objtype)
        else:
            val = super(classproperty, self).__get__(obj, objtype=objtype)
        return val

    def getter(self, fget):
        return super(classproperty, self).getter(self._fget_wrapper(fget))

    def setter(self, fset):
        raise NotImplementedError("classproperty can only be read-only")

    def deleter(self, fdel):
        raise NotImplementedError("classproperty can only be read-only")

    @staticmethod
    def _fget_wrapper(orig_fget):
        if isinstance(orig_fget, classmethod):
            orig_fget = orig_fget.__func__

        @functools.wraps(orig_fget)
        def fget(obj):
            return orig_fget(obj.__class__)

        fget.__wrapped__ = orig_fget

        return fget
