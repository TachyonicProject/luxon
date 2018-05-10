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
import sys
from io import BytesIO
import wsgiref.validate

from luxon.utils.encoding import if_unicode_to_bytes

from luxon.testing.wsgi.mock import StartResponseMock
from luxon.testing.wsgi.result import Result

def request(app, method='GET', path='/', query_string='',
            headers={}, body=None, file_wrapper=None,
            wsgierrors=sys.stdout, protocol='http'):

        if not path.startswith('/'):
            raise ValueError("path must start with '/'")

        if query_string and query_string.startswith('?'):
            raise ValueError("query_string should not start with '?'")

        if '?' in path:
            raise ValueError(
                'path may not contain a query string. Please use the '
                'query_string parameter instead.'
            )

        env = {}
        env['REQUEST_METHOD'] = method.upper()
        env['HTTP_HOST'] = 'tachyonic.org'
        env['SCRIPT_NAME'] = '/wsgi'
        env['PATH_INFO'] = path
        env['SERVER_NAME'] = 'tachyonic.org'
        env['SERVER_PORT'] = '80'
        env['SRRVER_PROTOCOL'] = 'HTTP/1/1'
        env['QUERY_STRING'] = query_string
        env['wsgi.errors'] = wsgierrors
        env['wsgi.input'] = BytesIO()
        if body is not None:
            env['wsgi.input'].write(if_unicode_to_bytes(body))
            env['wsgi.input'].seek(0)
        env['wsgi.multiprocess'] = True
        env['wsgi.multithread'] = True
        env['wsgi.run_once'] = False
        env['wsgi.url_scheme'] = protocol
        env['wsgi.version'] = (1, 0)

        for header in headers:
            if header.lower() == 'content-type':
                env['CONTENT_TYPE'] = headers[header]
            elif header.lower() == 'content-length':
                env['CONTENT_LENGTH'] = headers[header]
            else:
                wsgi_name = 'HTTP_' + header.upper().replace('-', '_')
                env[wsgi_name] = headers[header]

        srmock = StartResponseMock()

        validator = wsgiref.validate.validator(app)
        iterable = validator(env, srmock)

        result = Result(iterable, srmock.status, srmock.headers)

        if not srmock._called:
            raise Exception('Start Response not called')

        return result
