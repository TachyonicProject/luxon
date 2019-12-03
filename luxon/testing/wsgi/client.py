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
import os

from luxon.core.handlers.wsgi import Wsgi
from luxon.testing.wsgi.request import request


class Client(object):
    __slots__ = ('app',
                 '_default_headers')

    def __init__(self, test_module_file, default_headers=None):
        app_root = (os.path.abspath(os.path.dirname(test_module_file)))
        self.app = Wsgi(__name__, app_root + '/wsgi')
        self._default_headers = default_headers

    def get(self, path='/', **kwargs):
        return request(self.app, 'GET', path, **kwargs)

    def post(self, path='/', **kwargs):
        return request(self.app, 'POST', path, **kwargs)

    def put(self, path='/', **kwargs):
        return request(self.app, 'PUT', path, **kwargs)

    def patch(self, path='/', **kwargs):
        return request(self.app, 'PATCH', path, **kwargs)

    def delete(self, path='/', **kwargs):
        return request(self.app, 'DELETE', path, **kwargs)

    def head(self, path='/', **kwargs):
        return request(self.app, 'HEAD', path, **kwargs)

    def options(self, path='/', **kwargs):
        return request(self.app, 'OPTIONS', path, **kwargs)

    def connect(self, path='/', **kwargs):
        return request(self.app, 'CONNECT', path, **kwargs)
