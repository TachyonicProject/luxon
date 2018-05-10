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

class Reproduce(type):
    """Reproduce MetaClass.

    A convienance method to reproduce new object from object class.

    This cleaner than using copy/deepcopy.

    New object will be initilized with same args and kwargs as parent.
    """
    def __call__(_cls, *args, **kwargs):
        instance = super(Reproduce, _cls).__call__(*args, **kwargs)

        instance._args = args
        instance._kwargs = kwargs

        return instance

    def __new__(mcs, name, bases, attrs, **kwargs):
        def reproduce(self):
            """Reproduce object class.

            Returns new object.
            """
            # If has __init__ args stored private property
            if hasattr(self, '_args'):
                args = self._args
            else:
                args = []

            # If has __init__ kwargs stored private property
            if hasattr(self, '_kwargs'):
                kwargs = self._kwargs
            else:
                kwargs = {}

            return self.__class__(*args, **kwargs)

        attrs['reproduce'] = reproduce
        return super().__new__(mcs, name, bases, attrs)

    def __init__(cls, name, bases, attrs, **kwargs):
        return super().__init__(name, bases, attrs)
