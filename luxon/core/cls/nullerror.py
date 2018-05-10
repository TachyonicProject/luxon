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


class NullError(object):
    """This class raises expection when accessing object.

    The purposes of this NullError objects is to raise useful exceptions
    when the required object has not been initialized.

    It basically performs like a placeholder.

    Args:
        exception (class): Exception to raise.
        *args: Any other arguementst to pass to exception.

    Kwargs:
        *kwargs: Any arguements to pass to exception.
    """
    def __init__(self, exception, *args, **kwargs):
        super().__setattr__('_exception', exception)
        super().__setattr__('_args', args)
        super().__setattr__('_kwargs', kwargs)

    def __call__(self, *args, **kwargs):
        raise self._exception(*self._args, **self._kwargs)

    def __getattr__(self, attr):
        raise self._exception(*self._args, **self._kwargs)

    def __setattr__(self, attr, value):
        raise self._exception(*self._args, **self._kwargs)

    def __getitem__(self, item):
        raise self._exception(*self._args, **self._kwargs)

    def __setitem__(self, item, value):
        raise self._exception(*self._args, **self._kwargs)

    def __len__(self):
        raise self._exception(*self._args, **self._kwargs)

    def __contains__(self, key):
        raise self._exception(*self._args, **self._kwargs)

    def __repr__(self):
        raise self._exception(*self._args, **self._kwargs)

    def __str__(self):
        raise self._exception(*self._args, **self._kwargs)

    def __add__(self, other):
        raise self._exception(*self._args, **self._kwargs)

    def __sub__(self, other):
        raise self._exception(*self._args, **self._kwargs)

    def __mul__(self, other):
        raise self._exception(*self._args, **self._kwargs)

    def __matmul__(self, other):
        raise self._exception(*self._args, **self._kwargs)

    def __truediv__(self, other):
        raise self._exception(*self._args, **self._kwargs)

    def __floordiv__(self, other):
        raise self._exception(*self._args, **self._kwargs)

    def __mod__(self, other):
        raise self._exception(*self._args, **self._kwargs)

    def __divmod__(self, other):
        raise self._exception(*self._args, **self._kwargs)

    def __pow__(self, other):
        raise self._exception(*self._args, **self._kwargs)

    def __lshift__(self, other):
        raise self._exception(*self._args, **self._kwargs)

    def __rshift__(self, other):
        raise self._exception(*self._args, **self._kwargs)

    def __and__(self, other):
        raise self._exception(*self._args, **self._kwargs)

    def __xor__(self, other):
        raise self._exception(*self._args, **self._kwargs)

    def __or__(self, other):
        raise self._exception(*self._args, **self._kwargs)
