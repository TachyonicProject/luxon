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
import json
from http.cookies import SimpleCookie

from luxon.structs.cidict import CiDict
from luxon.utils.http import content_type_encoding
from luxon.testing.wsgi.cookie import Cookie


class Result(object):
    """Result of a WSGI request.

    The args provided are the values returned by the WSGI Application. This
    'class' provides a simple interface to access the encapsulated data.

    Args:
        iterable (iterable): Payload returned by WSGI Application.
        status (str): HTTP status string returned by WSGI Application.
        headers (list): List of (name, value) tuples.

    Attributes:
        status (str): HTTP status string.
        status_code (int): HTTP status code.
        headers (CiDict): Case-insensitive dictionary
        cookies (dict): Dictionary of Cookies.
        encoding (str): Encoding type. e.g. UTF-8
        text (str): Decoded response body.
        json (dict): Deserialized JSON body.
        content (bytes): Raw response body
    """
    def __init__(self, iterable, status, headers):
        self._text = None

        self._content = b''.join(iterable)
        if hasattr(iterable, 'close'):
            iterable.close()

        self._status = status
        self._status_code = int(status[:3])
        self._headers = CiDict(headers)

        cookies = SimpleCookie()
        for name, value in headers.items():
            if name.lower() == 'set-cookie':
                cookies.load(value)

        self._cookies = dict(
            (morsel.key, Cookie(morsel))
            for morsel in cookies.values()
        )

        self._encoding = content_type_encoding(
            self._headers.get('content-type'))

    @property
    def status(self):
        return self._status

    @property
    def status_code(self):
        return self._status_code

    @property
    def headers(self):
        return self._headers

    @property
    def cookies(self):
        return self._cookies

    @property
    def encoding(self):
        return self._encoding

    @property
    def content(self):
        return self._content

    @property
    def text(self):
        if self._text is None:
            if not self.content:
                self._text = u''
            else:
                if self.encoding is None:
                    encoding = 'UTF-8'
                else:
                    encoding = self.encoding

                self._text = self.content.decode(encoding)

        return self._text

    @property
    def json(self):
        if not self.text:
            return None

        return json.loads(self.text)
