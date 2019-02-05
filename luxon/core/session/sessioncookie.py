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
import base64

from luxon import g
from luxon.utils.encoding import (if_bytes_to_unicode,
                                  if_unicode_to_bytes)
from luxon.utils import js


class SessionCookie(object):
    """ Session Cookie Interface.

    Used for storing session data in cookies.

    Please refer to Session.
    """
    def __init__(self, expire, session_id, session):
        self._expire = expire
        self._session = session
        self._session_id = str(session_id)

    def load(self):
        req = g.current_request
        cookie = self._session_id
        session = req.cookies.get(cookie)
        if session:
            self._session.update(js.loads(base64.b64decode(session)))

    def save(self):
        req = g.current_request
        content = if_unicode_to_bytes(js.dumps(self._session))
        content = base64.b64encode(content)
        content = if_bytes_to_unicode(content)
        if len(content) > 4000:
            raise ValueError('SessionCookie size exceeded 4KB')

        cookie = self._session_id
        path = '/' + req.app.lstrip('/')
        req.response.set_cookie(cookie,
                                content,
                                path=path,
                                domain=req.host,
                                max_age=self._expire)

    def clear(self):
        req = g.current_request
        cookie = self._session_id
        path = '/' + req.app.lstrip('/')
        req.response.unset_cookie(cookie,
                                  path=path,
                                  domain=req.host)


class TrackCookie(object):
    def __init__(self, expire=86400):
        self._req = g.current_request
        self._cookie_name = self._req.host
        self._path = '/' + self._req.app.lstrip('/')
        self._expire = expire

        if (self._cookie_name in self._req.cookies and
                self._req.cookies[self._cookie_name].strip() != ''):
            self._session_id = if_bytes_to_unicode(
                self._req.cookies[self._cookie_name],
                'ISO-8859-1'
            )
        else:
            self._session_id = self._req.id

    def clear(self):
        self._req.response.unset_cookie(
            self._cookie_name,
            domain=self._req.host,
            path=self._path
        )

    def save(self):
        self._req.response.set_cookie(
            self._cookie_name,
            self._session_id,
            domain=self._req.host,
            path=self._path,
            max_age=self._expire)

    def __str__(self):
        return if_bytes_to_unicode(str(self._session_id),
                                   'ISO-8859-1')
