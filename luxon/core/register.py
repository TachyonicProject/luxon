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
import traceback
from luxon import g

from luxon import router
from luxon.core.logger import GetLogger

log = GetLogger(__name__)

_models = []
_sa_models = []
_middleware_pre = []
_middleware_resource = []
_middleware_post = []
_error_template = None
_ajax_error_template = None
g.javascripts = []
g.stylesheets = []
g.dashboards = []


class Register(object):
    __slots__ = ()

    def resource(self, method, route, tag=None, cache=0):
        def resource_wrapper(func):
            router.add(method, route, func, tag, cache)
            return func

        return resource_wrapper

    def resources(self, *args, name=None, **kwargs):
        def resource_wrapper(cls):
            if name is not None:
                cls._resources_name = name

            try:
                obj = cls(*args, **kwargs)
            except Exception:
                trace = str(traceback.format_exc())
                log.critical("%s" % trace)
                raise

            return obj

        return resource_wrapper

    def model(self, *args, **kwargs):
        def model_wrapper(cls):
            if hasattr(cls, '__table__'):
                # SQLAlchmey Models.
                _sa_models.append(cls)
                return cls
            else:
                # Old Models.
                cls._sql = True
                _models.append(cls)
                return cls

        return model_wrapper

    def middleware(self, middleware_class, *args, **kwargs):
        try:
            middleware_obj = middleware_class(*args, **kwargs)

            if hasattr(middleware_obj, 'pre'):
                _middleware_pre.append(middleware_obj.pre)

            if hasattr(middleware_obj, 'resource'):
                _middleware_resource.append(middleware_obj.resource)

            if hasattr(middleware_obj, 'post'):
                _middleware_post.append(middleware_obj.post)
        except Exception:
            trace = str(traceback.format_exc())
            log.critical("%s" % trace)
            raise

    def error_template(self, template):
        global _error_template

        _error_template = template

    def ajax_error_template(self, template):
        global _ajax_error_template

        _ajax_error_template = template

    def javascript(self, javascript):
        g.javascripts.append(javascript.strip('/'))

    def stylesheet(self, stylesheet):
        g.stylesheets.append(stylesheet.strip('/'))

    def dashboard(self, heading, dashboard):
        g.dashboards.append((heading, dashboard))
