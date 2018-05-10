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
import traceback

from luxon import g
from luxon.core.logger import GetLogger

log = GetLogger(__name__)


def model(*args, **kwargs):
    def model_wrapper(cls):
        cls._sql = True
        g.models.append(cls)
        return cls

    return model_wrapper


def resources(*args, name=None, **kwargs):
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


def resource(method, route, tag=None, cache=0):
    def resource_wrapper(func):
        g.router.add(method, route, func, tag, cache)
        return func

    return resource_wrapper


def middleware(middleware_class, *args, **kwargs):
    try:
        middleware_obj = middleware_class(*args, **kwargs)

        if hasattr(middleware_obj, 'pre'):
            g.middleware_pre.append(middleware_obj.pre)

        if hasattr(middleware_obj, 'resource'):
            g.middleware_resource.append(middleware_obj.resource)

        if hasattr(middleware_obj, 'post'):
            g.middleware_post.append(middleware_obj.post)
    except Exception:
        trace = str(traceback.format_exc())
        log.critical("%s" % trace)
        raise


def error_template(template):
    g.error_template = template


def ajax_error_template(template):
    g.ajax_error_template = template
