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
from datetime import timedelta

from luxon import g
from luxon.utils.encoding import (if_unicode_to_bytes,
                                  if_bytes_to_unicode,)
from luxon.utils import rsa
from luxon.core.logger import GetLogger
from luxon.exceptions import (AccessDeniedError,
                              TokenExpiredError,
                              TokenMissingError)
from luxon.utils import js
from luxon.utils.timezone import utc, now
from luxon.utils import files

log = GetLogger(__name__)


class Auth(object):
    """Authentication class.

    Luxon token / authentication provider. Uses RSA private keys to sign
    tokens. Endpoints will require the public key to validate token
    authenticity.

    The keys should be stored in the application root. Usually where the
    wsgi file is located.

    Generate RSA Private/Public Key pairs:
        luxon -r

    Args:
        expire (int): Token life-span in seconds. (default 60 seconds)

    Attributes:
        authenticated (bool): Wether authenticated.
        token (str): Token.
        json (str): Token in JSON.
        roles (tuple): Roles applied.
        user_id (str): User ID.
        user_domain (str): Login domain.
        tenant_id (str): Scope tenant context.
        domain (str): Scope domain context.
    """
    __slots__ = ('_token_expire',
                 '_credentials',
                 '_rsakey',
                 )

    def __init__(self, expire=60):
        # Create initial token dict.
        self.clear()

        self._token_expire = expire

        self._rsakey = rsa.RSAKey()

        if files.exists(g.app.path.rstrip('/') + '/private.pem'):
            password = g.app.config.get('tokens',
                                        'key_password',
                                        fallback=None)
            self._rsakey.load_pem_key_file(g.app.path.rstrip('/') +
                                           '/private.pem',
                                           password=password)
        if files.exists(g.app.path.rstrip('/') + '/public.pem'):
            self._rsakey.load_pem_key_file(g.app.path.rstrip('/') +
                                           '/public.pem')

    def clear(self):
        """Clear authentication."""
        self._credentials = {}

    @property
    def authenticated(self):
        if 'expire' in self._credentials:
            return True
        return False

    @property
    def token(self):
        if not self.authenticated:
            raise TokenMissingError()

        if now() > utc(self._credentials['expire']):
            raise TokenExpiredError()

        bytes_token = if_unicode_to_bytes(js.dumps(self._credentials,
                                                   indent=None))
        b64_token = base64.b64encode(bytes_token)
        token_sig = if_unicode_to_bytes(self._rsakey.sign(b64_token))
        token = if_bytes_to_unicode(token_sig + b'!!!!' + b64_token)
        if len(token) > 1280:
            raise ValueError("Auth Token exceeded 10KB" +
                             " - Revise Assignments for credentials")

        return token

    @token.setter
    def token(self, token):
        token = if_unicode_to_bytes(token)
        signature, b64_token = token.split(b'!!!!')

        try:
            self._rsakey.verify(signature, b64_token)
        except ValueError as e:
            raise AccessDeniedError('Invalid Auth Token. %s' % e)

        decoded = js.loads(base64.b64decode(b64_token))
        utc_expire = utc(decoded['expire'])

        if now() > utc_expire:
            raise TokenExpiredError()

        self._credentials = decoded

    @property
    def json(self):
        if not self.authenticated:
            raise TokenMissingError()

        utc_expire = utc(self._credentials['expire'])
        if now() > utc_expire:
            raise TokenExpiredError()

        credentials = {}
        credentials['token'] = self.token
        credentials.update(self._credentials)
        return js.dumps(credentials)

    def __len__(self):
        return len(self.token)

    def __repr__(self):
        return self.json

    def __str__(self):
        return self.json

    def new(self, user_id, username=None, domain=None,
            roles=None):
        """New Authentication token.

        Args:
            user_id (str): Unique user identifier.
            username (str): Username (optional).
            domain (str): Domain (optional).
            roles (list): List of roles (optional).
        """

        self.clear()

        if 'expire' not in self._credentials:
            # Create New Token
            expire = (now() + timedelta(seconds=self._token_expire))
            self._credentials['expire'] = expire.strftime("%Y/%m/%d %H:%M:%S")

        self._credentials['user_id'] = user_id

        if username is not None:
            self._credentials['username'] = username

        if domain is not None:
            self._credentials['user_domain'] = domain

        if roles is not None:
            self.roles = roles

    @property
    def roles(self):
        return tuple(self._credentials.get('roles', []))

    @roles.setter
    def roles(self, value):
        self.validate()

        if 'roles' not in self._credentials:
            self._credentials['roles'] = []

        if isinstance(value, (list, tuple,)):
            self._credentials['roles'] += list(value)
            self._credentials['roles'] = list(set(self._credentials['roles']))
        elif isinstance(value, str):
            self._credentials['roles'].append(value)
            self._credentials['roles'] = list(set(self._credentials['roles']))
        else:
            raise ValueError("Appending roles requires 'str', 'tuple'" +
                             " or 'list'")

    @property
    def tenant_id(self):
        return self._credentials.get('tenant_id', None)

    @tenant_id.setter
    def tenant_id(self, value):
        self.validate()

        if ('tenant_id' in self._credentials and
                self._credentials['tenant_id'] is not None):
            if self._credentials['tenant_id'] != value:
                raise AccessDeniedError("Token already scoped in 'tenant'")

        self._credentials['tenant_id'] = value

    @property
    def user_id(self):
        return self._credentials.get('user_id', None)

    @property
    def user_domain(self):
        return self._credentials.get('user_domain', None)

    @property
    def domain(self):
        return self._credentials.get('domain', None)

    @domain.setter
    def domain(self, value):
        self.validate()

        if ('domain' in self._credentials and
                self._credentials['domain'] is not None):
            if self._credentials['domain'] != value:
                raise AccessDeniedError("Token already scoped in 'domain'")

        self._credentials['domain'] = value

    def validate(self):
        """Vaidate current token."""
        if not self.authenticated:
            raise TokenMissingError() from None
        elif 'expire' in self._credentials:
            utc_expire = utc(self._credentials['expire'])
            if now() > utc_expire:
                self.clear()
                raise TokenExpiredError() from None

    def __setattr__(self, attr, value):
        if attr in self.__slots__:
            return object.__setattr__(self, attr, value)
        try:
            return object.__setattr__(self, attr, value)
        except AttributeError:
            self.validate()
            if (attr in self._credentials and
                    self._credentials[attr] is not None):
                raise AccessDeniedError("Token scope '%s'" % attr +
                                        " not allowed") from None
            self._credentials[attr] = value

    def __getattr__(self, attr):
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            try:
                self.validate()
                return self._credentials[attr]
            except KeyError:
                return None
