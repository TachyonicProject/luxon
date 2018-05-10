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

import threading

from luxon.utils.objects import object_name

class ThreadList(object):
    """List for Threads

    Allows thread safe and mutable iterations and unique sequence set of values
    per thread. Context for sequence of values being the thread id.

    Define globally for process and not within thread to take advantage of unique
    content functionality.
    """
    def __init__(self):
        self._thread_local = threading.local()

    def _contains(self):
        if not hasattr(self._thread_local, '_contains'):
            self._thread_local._contains = []

        return self._thread_local._contains

    def __call__(self):
        return self._contains()

    def clear(self):
        """Clear sequence for thread.
        """
        if not hasattr(self._thread_local, '_contains'):
            self._thread_local._contains = []
            return self

        self._thread_local._contains.clear()
        return self


    def append(self, value):
        """Appends object obj to list

        Args:
            Object/Value to be appended.
        """
        self._contains().append(value)

    def remove(self, value):
        self._contains().remove(value)


    def __setitem__(self, item, value):
        """Update value of item
        """
        self._contains()[item] = value

    def __getitem__(self, item):
        """Get value of item.
        """
        try:
            return self._contains()[item]
        except IndexError:
            raise IndexError('list index out of range')

    def __delitem__(self, item):
        """Delete item in sequence.
        """
        try:
            del self._contains()[item]
        except IndexError:
            raise IndexError('list index out of range')

    def __contains__(self, item):
        """True if has a item, else False.
        """
        try:
            return item in self._contains()
        except IndexError:
            raise IndexError('list index out of range')

    def __iter__(self):
        """Return iterable of thread list.
        """
        return iter(self._contains())

    def __len__(self):
        """Return int length of thread list.
        """
        return len(self._contains())

    def __repr__(self):
        """Return representation of thread list.
        """
        return repr(object_name(self) + str(self()))

    def __str__(self):
        """Return string of thread list.
        """
        return str(object_name(self) + str(self()))
