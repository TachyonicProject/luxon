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


class Session(object):
    """Session Base Class.

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
