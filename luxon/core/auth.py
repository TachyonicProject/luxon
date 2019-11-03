# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Christiaan Rademan <chris@fwiw.co.za>.
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

from authlib.jose import jwt
from authlib.jose.rfc7519 import JWTClaims
import authlib.jose.errors

from luxon import g
from luxon.core.logger import GetLogger
from luxon.exceptions import (AccessDeniedError,
                              TokenExpiredError,
                              TokenMissingError)
from luxon.utils import js
from luxon.utils.timezone import epoch
from luxon.utils import files

log = GetLogger(__name__)


class Auth(object):
    """Authentication class.

    Luxon token / authentication provider. Uses JWT Tokens with RSA private
    keys to sign tokens. Endpoints will require the public key to validate
    token authenticity.

    The keys should be stored in the application root. Usually where the
    wsgi file is located.

    Generate RSA Private/Public Key pairs:
        luxon -r

    Args:
        expire (int): Token life-span in seconds. (default 60 seconds)
    """
    __slots__ = ('_token',
                 '_token_expire',
                 '_header',
                 '_jwt',
                 '_rsa_pub',
                 '_rsa_prv',
                 )

    def __init__(self, expire=60):
        def read_file(path):
            with open(path, 'rb') as f:
                return f.read()

        # JWT Token header.
        self._header = {'alg': 'RS256'}

        # Create initial token dict.
        self.clear()

        # Token expiry.
        self._token_expire = expire

        # Read private key.
        if files.exists(g.app.path.rstrip('/') + '/private.pem'):
            with open(g.app.path.rstrip('/') + '/private.pem', 'rb') as f:
                self._rsa_prv = f.read()
        else:
            self._rsa_prv = None

        # Read public key.
        if files.exists(g.app.path.rstrip('/') + '/public.pem'):
            with open(g.app.path.rstrip('/') + '/public.pem', 'rb') as f:
                self._rsa_pub = f.read()
        else:
            self._rsa_pub = None

    def clear(self):
        """Clear authentication."""
        self._token = None
        self._jwt = None

    def validate(self):
        if self._jwt:
            try:
                self._jwt.validate()
                return True
            except authlib.jose.errors.ExpiredTokenError:
                raise TokenExpiredError()
        else:
            raise TokenMissingError()

    @property
    def authenticated(self):
        try:
            return self.validate()
        except TokenExpiredError:
            return False
        except TokenMissingError:
            return False

    @property
    def token(self):
        if not self.authenticated:
            raise TokenMissingError()

        if not self._token:
            if self._rsa_prv:
                return jwt.encode(self._header,
                                  self._jwt,
                                  self._rsa_prv)
            else:
                raise AccessDeniedError('No private key for signing JWT Token')
        else:
            return self._token

    @token.setter
    def token(self, token):
        if not self._rsa_pub:
            raise AccessDeniedError('No public key for validating JWT Token')

        if token is not None:
            self._token = token
            self._jwt = jwt.decode(token, self._rsa_pub)
            self.validate()

    @property
    def json(self):
        self.validate()
        return js.dumps({**self._jwt, 'token': self.token})

    def new(self, user_id, username=None, domain=None,
            roles=None, region=None, confederation=None, metadata={}):
        self.clear()

        claims = {}
        claims['user_id'] = user_id
        claims['metadata'] = metadata

        if region is not None:
            claims['user_region'] = region

        if confederation is not None:
            claims['user_confederation'] = confederation

        if username is not None:
            claims['username'] = username

        if domain is not None:
            claims['user_domain'] = domain

        if roles is not None:
            claims['roles'] = list(set(roles))

        claims['exp'] = int(epoch() + self._token_expire)
        self._jwt = JWTClaims(claims, self._header)

    def extend(self):
        self._token = None
        self.validate()
        self._jwt['exp'] = int(epoch() + self._token_expire)

    @property
    def roles(self):
        if self._jwt:
            self.validate()
            return tuple(self._jwt.get('roles', []))
        return ()

    @roles.setter
    def roles(self, value):
        self._token = None
        self.validate()

        if 'roles' not in self._jwt:
            self._jwt['roles'] = []

        if isinstance(value, (list, tuple,)):
            self._jwt['roles'] += list(value)
            self._jwt['roles'] = list(set(self._jwt['roles']))
        elif isinstance(value, str):
            self._jwt['roles'].append(value)
            self._jwt['roles'] = list(set(self._jwt['roles']))
        else:
            raise ValueError("Appending roles requires 'str', 'tuple'" +
                             " or 'list'")

    @property
    def metadata(self):
        if self._jwt:
            self.validate()
            return self._jwt.get('metadata', None)

    @metadata.setter
    def metadata(self, value):
        self._token = None
        self.validate()
        self._jwt['metadata'] = value

    @property
    def user_id(self):
        if self._jwt:
            self.validate()
            return self._jwt.get('user_id', None)

    @property
    def username(self):
        if self._jwt:
            self.validate()
            return self._jwt.get('username', None)

    @property
    def user_domain(self):
        if self._jwt:
            self.validate()
            return self._jwt.get('user_domain', None)

    @property
    def user_region(self):
        if self._jwt:
            self.validate()
            return self._jwt.get('user_region', None)

    @property
    def user_confederation(self):
        if self._jwt:
            self.validate()
            return self._jwt.get('user_confederation', None)

    @property
    def default_tenant_id(self):
        if self._jwt:
            self.validate()
            return self._jwt.get('default_tenant_id', None)

    @default_tenant_id.setter
    def default_tenant_id(self, value):
        if self._jwt:
            self.validate()
            self._jwt['default_tenant_id'] = value

    @property
    def tenant_id(self):
        if self._jwt:
            self.validate()
            return self._jwt.get('tenant_id', None)

    @tenant_id.setter
    def tenant_id(self, value):
        self._token = None
        self.validate()

        if ('tenant_id' in self._jwt and
                self._jwt['tenant_id'] is not None):
            if self._jwt['tenant_id'] != value:
                raise AccessDeniedError("Token already scoped in 'tenant'")

        self._jwt['tenant_id'] = value

    @property
    def domain(self):
        if self._jwt:
            self.validate()
            return self._jwt.get('domain', None)

    @domain.setter
    def domain(self, value):
        self._token = None
        self.validate()

        if ('domain' in self._jwt and
                self._jwt['domain'] is not None):
            if self._jwt['domain'] != value:
                raise AccessDeniedError("Token already scoped in 'domain'")

        self._jwt['domain'] = value

    def __repr__(self):
        return repr(self._jwt)

    def __str__(self):
        return self.json
