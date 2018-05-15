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

from luxon.core.cls.nullerror import NullError
from luxon.exceptions import NoContextError
from luxon.structs.threaddict import ThreadDict


_thread_globals = ThreadDict()
_thread_items = ('current_request', 'client',)

_context_items = ('client',
                  'current_request',
                  'app_root',
                  'app_name',
                  )

_globals = {}

_models = []
_middleware_pre = []
_middleware_resource = []
_middleware_post = []

_cached_global_router = None
_cached_global_config = None

APIClient = None


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

    @property
    def config(self):
        global _cached_global_config

        if _cached_global_config is not None:
            return _cached_global_config
        else:
            from luxon.core.config import Config
            _cached_global_config = Config()
            return _cached_global_config

    @property
    def router(self):
        global _cached_global_router

        if _cached_global_router is not None:
            return _cached_global_router
        else:
            from luxon.core.router import Router
            _cached_global_router = Router()
            return _cached_global_router

    @property
    def debug(self):
        global _debug

        try:
            return _debug
        except NameError:
            try:
                _debug = self.config.getboolean('application', 'debug')
            except Exception:
                _debug = True
        return _debug

    @debug.setter
    def debug(self, value):
        global _debug

        _debug = value

    @property
    def models(self):
        """Returns list of models"""
        return _models

    @property
    def middleware_pre(self):
        return _middleware_pre

    @property
    def middleware_resource(self):
        return _middleware_resource

    @property
    def middleware_post(self):
        return _middleware_post

    def __setattr__(self, attr, value):
        if attr in _thread_items:
            _thread_globals[attr] = value
        else:
            super().__setattr__(attr, value)

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
                try:
                    return super().__getattr__(attr)
                except AttributeError:
                    pass
                if attr in _context_items:
                    # Place holder for context - Provides nice error.
                    return NullError(NoContextError,
                                     "Working outside of '%s'" % attr +
                                     " context")
                raise AttributeError("'" + self.__class__.__name__ +
                                     "' object has no attribute '" +
                                     attr + "'") from None

    def __contains__(self, attr):
        return attr in _thread_globals or attr in _globals or hasattr(self,
                                                                      attr)


# All globals.... luxon.g = Application wide context.
luxon_globals = Globals()
