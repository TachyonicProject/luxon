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

from luxon.exceptions import NoContextError
from luxon.structs.threaddict import ThreadDict


_thread_globals = ThreadDict()
_thread_items = ('current_request', )

_context_items = ('current_request',
                  'app', )

_globals = {}


class Globals(object):
    """Global object

    Providing process level and unique thread object references to.

    Purpose:
        * Placeholder for context related references.
        * Ensures relevant references to objects are based on thread.
        * Provides globals such as configuration on demand.
    """
    __slots__ = ('__dict__',)

    def __init__(self):
        self.__dict__ = _globals

    def __delattr__(self, attr):
        try:
            del _thread_globals[attr]
        except KeyError:
            try:
                del _globals[attr]
            except KeyError:
                pass

    def __getattr__(self, attr):
        try:
            return _thread_globals[attr]
        except KeyError:
            try:
                return _globals[attr]
            except KeyError:
                if attr in _context_items:
                    # Place holder for context - Provides nice error.
                    raise NoContextError(
                                     "Working outside of '%s'" % attr +
                                     " context") from None
                raise AttributeError("'" + self.__class__.__name__ +
                                     "' object has no attribute '" +
                                     attr + "'") from None

    def __contains__(self, attr):
        return attr in _thread_globals or attr in _globals or hasattr(self,
                                                                      attr)


# All globals.... luxon.g = Application wide context.
luxon_globals = Globals()
