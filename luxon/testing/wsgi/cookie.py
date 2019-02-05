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
from luxon.utils.timezone import parse_http_date


class Cookie(object):
    """Represents a cookie returned by a simulated request.

    Args:
        morsel: Object from which to derive the cookie data.

    Attributes:
        name (str): Cookie name.
        value (str): Value of the cookie.
        expires(datetime.datetime): Cookie Expiration timestamp or 'None'.
        max_age (int): Cookie lifetime in seconds or 'None'.
        domain (str): Domain which this cookie is restricted for or 'None'.
        path (str): Path prefix of which this cookie is restricted or 'None'.
        http_only (bool): If cookie may only be sent in unscripted requests.
        secure (bool): If the cookie may only only be transmitted over HTTPS.
    """

    def __init__(self, morsel):
        self._name = morsel.key
        self._value = morsel.value

        for name in (
            'expires',
            'path',
            'domain',
            'max_age',
            'secure',
            'httponly',
        ):
            value = morsel[name.replace('_', '-')] or None
            setattr(self, '_' + name, value)

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def max_age(self):
        return int(self._max_age) if self._max_age else None

    @property
    def expires(self):
        if self._expires:
            return parse_http_date(self._expires, obs_date=True)

        return None

    @property
    def path(self):
        return self._path

    @property
    def domain(self):
        return self._domain

    @property
    def http_only(self):
        return bool(self._httponly)

    @property
    def secure(self):
        return bool(self._secure)
