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

import os
import logging
import pickle
import time
import datetime
import base64

from luxon import g
from luxon.helpers.rd import Redis
from luxon.utils.encoding import (if_bytes_to_unicode,
                                  if_unicode_to_bytes)
from luxon.utils import js
from luxon.utils.files import Open

log = logging.getLogger(__name__)


class Session(object):
    """ Session Base Class.

    Luxon provides full support for anonymous sessions. The session framework
    lets you store and retrieve arbitrary data on a per-site-visitor basis. It
    stores data on the server side and abstracts the sending and receiving of
    cookies. Cookies contain a session ID – not the data itself (unless you’re
    using the cookie based backend).

    SessionBase A dictionary like object containing session data.

    """
    def __init__(self, session_id, backend=None, expire=86400):
        self._session_id = session_id(expire)
        self._session = {}

        self._backend = backend(int(expire),
                                self._session_id,
                                self._session)

        self.load()

    @property
    def id(self):
        return self._session_id

    def save(self):
        self._session_id.save()
        self._backend.save()

    def load(self):
        self._backend.load()

    def clear(self):
        self._session_id.clear()
        self._backend.clear()

    def get(self, k, d=None):
        return self._session.get(k, d)

    def __setitem__(self, key, value):
        self._session[key] = value

    def __getitem__(self, key):
        return self._session[key]

    def __delitem__(self, key):
        try:
            del self._session[key]
        except KeyError:
            pass

    def __contains__(self, key):
        return key in self._session

    def __iter__(self):
        return iter(self._session)

    def __len__(self):
        return len(self._session)


class SessionRedis(object):
    """Session Redis Interface.

    Used for storing session data in Redis. Helpful when running multiple
    instances of luxon which requires a shared session state.

    Please refer to Session.
    """
    def __init__(self, expire, session_id, session):
        self._redis = Redis(expire=expire)
        self._session = session
        self._name = "session:%s" % str(session_id)

    def load(self):
        if self._name in self._redis:
            self._session.update(self._redis[self._name])

    def save(self):
        if len(self._session) > 0:
            self._redis[self._name] = self._session

    def clear(self):
        self._session.clear()
        try:
            del self._redis[self._name]
        except Exception:
            pass


class SessionFile(object):
    """ Session File Interface.

    Used for storing session data in flat files.

    Please refer to Session.
    """
    def __init__(self, expire, session_id, session):
        self._expire = expire
        self._session_id = str(session_id)
        self._session = session
        path = "%s/tmp" % g.app_root
        self._file = "%s/session_%s.pickle" % (path, self._session_id,)

    def load(self):
        try:
            with Open(self._file, 'rb', 0) as sf:
                ts = int(time.mktime(datetime.datetime.now().timetuple()))
                stat = os.stat(self._file)
                lm = int(stat.st_mtime)
                if ts - lm > self._expire:
                    self._session.clear()
                    try:
                        os.unlink(self._file)
                    except FileNotFoundError:
                        pass
                else:
                    try:
                        self._session.update(pickle.load(sf))
                    except EOFError:
                        self._session.clear()
                        pass
        except FileNotFoundError:
            self._session.clear()

    def save(self):
        if len(self._session) > 0:
            with Open(self._file, 'wb', 0) as fd:
                pickle.dump(self._session, fd)

    def clear(self):
        with Open(self._file, 'rb', 0):
            self._session.clear()
            try:
                os.unlink(self._file)
            except FileNotFoundError:
                pass


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
        if len(content) > 1920:
            raise ValueError('SessionCookie size exceeded 15KB')

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

        if self._cookie_name in self._req.cookies:
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


class TrackToken(object):
    def __init__(self, expire):
        self._session_id = g.current_request.user_token

    def clear(self):
        pass

    def save(self):
        pass

    def __str__(self):
        return if_bytes_to_unicode(str(self._session_id),
                                   'ISO-8859-1')
