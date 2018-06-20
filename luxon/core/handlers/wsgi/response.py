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
from io import BytesIO
from collections import OrderedDict
from http.cookies import SimpleCookie, CookieError

from luxon import __identity__
from luxon import constants as const
from luxon.utils.encoding import is_ascii
from luxon.utils.timezone import TimezoneGMT, to_gmt, format_http_datetime
from luxon.core.handlers.wsgi.redirects import Redirects
from luxon.structs.cidict import CiDict
from luxon.utils.encoding import if_unicode_to_bytes
from luxon.utils.http import (parse_cache_control_header,
                              ETags)
from luxon.utils import js

GMT_TIMEZONE = TimezoneGMT()


class Response(Redirects):
    """Represents an HTTP response to a client request.

    Args:
        env (dict): A WSGI environment dict passed in from the server.
            As per PEP-3333.
        start_response (function): callback function supplied by the server
            which takes the HTTP status and headers as arguments.

    Attributes:
        status (int): HTTP status code. (e.g. '200') Default 200.
        etags (obj): The luxon.utils.http.Etags obj associated with the
                     Response.
        cache_control(str): The value of cache-control in the Response header.
        expire(str): The value of expire in the Response header.
        last_modified(str): The value of last-modified in the Response header.
        age(int): The value of age in the Response header.
    """
    _DEFAULT_CONTENT_TYPE = const.APPLICATION_JSON
    _BODILESS_STATUS_CODES = (
        100,
        101,
        204,
        304,
    )
    _STREAM_BLOCK_SIZE = 8 * 1024  # 8 KiB
    _DEFAULT_ENCODING = 'UTF-8'

    __slots__ = (
        'content_type',
        '_stream',
        '_headers',
        '_http_response_status_code',
        '_cookies',
        '_start_response',
        '_etags',
    )

    def __init__(self, environ, start_response):
        self.content_type = None
        self._stream = None
        self._headers = {}

        self._start_response = start_response

        # Used internally.
        self._http_response_status_code = 200

        # Some Default Headers..
        self._headers['X-Powered-By'] = __identity__

        self._cookies = None
        self._etags = None

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.status)

    def __str__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.status)

    @property
    def rows(self):
        return (self._total_rows, self._filtered_rows)

    @property
    def content_length(self):
        """Value of bytes in response.

        Returns:
            int: total octects for response.
        """
        try:
            return self._stream.getbuffer().nbytes
        except AttributeError:
            pass

        try:
            return len(self._stream)
        except TypeError:
            return None

    def body(self, obj):
        """Set Response Body.

        Accepts following objects:
            'str', and 'bytes', if str will be encoded to bytes.
            file, iter like objects must return bytes.
            OrderedDict, dict and list will be translated json
            and encoded to 'UTF-8'

        Args:
            obj (object): Any valid object for response body.
        """
        if isinstance(obj, (str, bytes,)):
            # If Body is string, bytes.
            obj = if_unicode_to_bytes(obj)
            if self.content_type is None:
                self.content_type = self._DEFAULT_CONTENT_TYPE
            self._stream = obj
        elif isinstance(obj, (OrderedDict, dict, list, tuple,)):
            # If JSON serializeable object.
            self.content_type = const.APPLICATION_JSON
            self._stream = if_unicode_to_bytes(js.dumps(obj))
        elif hasattr(obj, 'json'):
            # If JSON serializeable object.
            self.content_type = const.APPLICATION_JSON
            self._stream = if_unicode_to_bytes(obj.json)
        elif hasattr(obj, 'read') or hasattr(obj, '__iter__'):
            # If body content behaves like file.
            if self.content_type is None:
                self.content_type = const.APPLICATION_OCTET_STREAM
            self._stream = obj
        else:
            raise ValueError('resource not returning acceptable object %s' %
                             type(obj))

    def write(self, value):
        """Write bytes to response body.

        Args:
            value (bytes): Data to be written.

        Returns:
            int: The number of bytes written.
        """
        value = if_unicode_to_bytes(value)

        if not isinstance(self._stream, BytesIO):
            self._stream = BytesIO()

        length = self._stream.write(value)

        if self.content_type is None:
            self.content_type = self._DEFAULT_CONTENT_TYPE

        return length

    @property
    def status(self):
        return self._http_response_status_code

    @status.setter
    def status(self, value):
        self._http_response_status_code = int(value)

    def set_header(self, name, value):
        """Set a header for this response to a given value.

        Names and values must be convertable to 'str' or be str'.
        Strings must contain only US-ASCII characters.

        Args:
            name (str): Header name (case-insensitive).
            value (str): Value for the header.
        """

        name = str(name)
        value = str(value)

        self._headers[name.title()] = value

    @property
    def etag(self):
        if self._etags is None:
            self._etags = ETags(set_callback=self.append_header)

        return self._etags

    @etag.setter
    def etag(self, value):
        self.delete_header('etag')
        self._etags = ETags(value, set_callback=self.append_header)

    @property
    def cache_control(self):
        return parse_cache_control_header(self.get_header('cache-control'))

    @cache_control.setter
    def cache_control(self, options):
        self.append_header('cache-control', options)

    @property
    def expires(self):
        expires = self.get_header('expires')
        if expires is not None:
            return to_gmt(expires, src=TimezoneGMT())

    @expires.setter
    def expires(self, value):
        self.set_header('expires', format_http_datetime(value))

    @property
    def last_modified(self):
        last_modified = self.get_header('last-modified')
        if last_modified is not None:
            return to_gmt(last_modified, src=TimezoneGMT())

    @last_modified.setter
    def last_modified(self, value):
        self.set_header('last-modified', format_http_datetime(value))

    @property
    def age(self):
        try:
            return int(self.get_header('age'))
        except ValueError:
            raise ValueError('Invalid Integer Value for age')

    @age.setter
    def age(self, value):
        self.set_header('age', str(value))

    def delete_header(self, name):
        """Delete a header that was previously set for this response.

        If the header was not previously set, nothing is done (no error is
        raised).

        Names and values must be convertable to 'str' or be str'.
        Strings must contain only US-ASCII characters.

        Args:
            name (str): Header name (case-insensitive).
        """

        self._headers.pop(name.title(), None)

    def append_header(self, name, value):
        """Set or append a header for this response.

        If the header already exists, the new value will be appended
        to it, delimited by a comma. Some header specifications support
        this format, Set-Cookie being the notable exceptions.

        Names and values must be convertable to 'str' or be str'.
        Strings must contain only US-ASCII characters.

        Args:
            name (str): Header name (case-insensitive).
            value (str): Value for the header.
        """
        name = str(name)
        value = str(value)

        name = name.title()
        if name in self._headers:
            value = self._headers[name] + ',' + value

        self._headers[name] = value

    def set_headers(self, headers):
        """Set several headers at once.

        Calling this method overwrites existing values, if any.

        Names and values must be convertable to 'str' or be str'.
        Strings must contain only US-ASCII characters.

        Args:
            headers (dict or list): A dictionary of header names and values
                to set, or a 'list' of (*name*, *value*) tuples.

        Raises:
            ValueError: `headers` was not a 'dict' or 'list' of 'tuple'.
        """

        if isinstance(headers, (dict, CiDict,)):
            headers = headers.items()

        _headers = self._headers

        for name, value in headers:
            name = str(name)
            value = str(value)

            _headers[name.title()] = value

    def get_header(self, name):
        """Retrieve the raw string value for the given header.

        Names and values must be convertable to 'str' or be str'.
        Strings must contain only US-ASCII characters.

        Args:
            name (str): Header name (case-insensitive).

        Returns:
            str: The header's value if set, otherwise None.
        """
        return self._headers.get(name.title(), None)

    def set_cookie(self, name, value, expires=None, max_age=None,
                   domain=None, path=None, secure=False, http_only=True):
        """Set a response cookie.

        This method can be called multiple times to add one or
        more cookies to the response.

        Args:
            name (str): Cookie name
            value (str): Cookie value

        Keyword Args:
            expires (datetime): Specifies when the cookie should expire.
                By default, cookies expire when the user agent exits.

                Refer to RFC 6265, Section 4.1.2.1

            max_age (int): Defines the lifetime of the cookie in
                seconds. By default, cookies expire when the user agent
                exits. If both 'max_age' and 'expires' are set, the
                latter is ignored by the user agent.

                Refer to RFC 6265, Section 4.1.2.2

            domain (str): Restricts the cookie to a specific domain and
                any subdomains of that domain. By default, the user
                agent will return the cookie only to the origin server.
                When overriding this default behavior, the specified
                domain must include the origin server. Otherwise, the
                user agent will reject the cookie.

                Refer to RFC 6265, Section 4.1.2.3

            path (str): Scopes the cookie to the given path plus any
                subdirectories under that path (the "/" character is
                interpreted as a directory separator). If the cookie
                does not specify a path, the user agent defaults to the
                path component of the requested URI.

                User agent interfaces do not always isolate cookies by
                path and so this should not be considered an effective
                security measure.

                Refer to RFC 6265, Section 4.1.2.4

            secure (bool): Direct the client to only return the cookie
                in subsequent requests if they are made over HTTPS

                Defaults to False.

                Enabling this can help prevents attackers from reading
                sensitive cookie data.

                Refer RFC 6265, Section 4.1.2.5

            http_only (bool): Direct the client to only transfer the
                cookie with unscripted HTTP requests.

                Default True.

                This is intended to mitigate some forms of cross-site
                scripting.

                Refer to RFC 6265, Section 4.1.2.6

        Raises:
            KeyError: `name` is not a valid cookie name.
            ValueError: `value` is not a valid cookie value.
        """

        if not is_ascii(name):
            raise KeyError('"name" is not ascii encodable')
        if not is_ascii(value):
            raise ValueError('"value" is not ascii encodable')

        name = str(name)
        value = str(value)

        if self._cookies is None:
            self._cookies = SimpleCookie()

        try:
            self._cookies[name] = value
        except CookieError as e:  # pragma: no cover
            # NOTE(tbug): we raise a KeyError here, to avoid leaking
            # the CookieError to the user. SimpleCookie (well, BaseCookie)
            # only throws CookieError on issues with the cookie key
            raise KeyError(str(e))

        if expires:
            # set Expires on cookie. Format is Wdy, DD Mon YYYY HH:MM:SS GMT

            # NOTE(tbug): we never actually need to
            # know that GMT is named GMT when formatting cookies.
            # It is a function call less to just write "GMT" in the fmt string:
            fmt = '%a, %d %b %Y %H:%M:%S GMT'
            if expires.tzinfo is None:
                # naive
                self._cookies[name]['expires'] = expires.strftime(fmt)
            else:
                # aware
                gmt_expires = expires.astimezone(GMT_TIMEZONE)
                self._cookies[name]['expires'] = gmt_expires.strftime(fmt)

        if max_age:
            # RFC 6265 section 5.2.2 says about the max-age value:
            #   "If the remainder of attribute-value contains a non-DIGIT
            #    character, ignore the cookie-av."
            # That is, RFC-compliant response parsers will ignore the max-age
            # attribute if the value contains a dot, as in floating point
            # numbers. Therefore, attempt to convert the value to an integer.
            self._cookies[name]['max-age'] = int(max_age)
        if domain:
            self._cookies[name]['domain'] = domain

        if path:
            self._cookies[name]['path'] = path

        if secure is None:
            is_secure = self.options.secure_cookies_by_default
        else:
            is_secure = secure

        if is_secure:
            self._cookies[name]['secure'] = True

        if http_only:
            self._cookies[name]['httponly'] = http_only

    def unset_cookie(self, name, domain=None, path=None):
        """Unset a cookie in the response

        Clears the contents of the cookie, and instructs the user
        agent to immediately expire its own copy of the cookie.

        In order to successfully remove a cookie, both the
        path and the domain must match the values that were
        used when the cookie was created.

        Args:
            name (str): Cookie Name
        """
        if self._cookies is None:
            self._cookies = SimpleCookie()

        self._cookies[name] = ''
        self._cookies[name]['expires'] = -1
        if domain:
            self._cookies[name]['domain'] = domain

        if path:
            self._cookies[name]['path'] = path

    def __call__(self):
        # Localized for a little more speed.
        status = self.status
        headers = self._headers
        content_type = self.content_type
        content_length = self.content_length

        # Set Content-Length Header.
        if content_length is not None:
            headers['Content-Length'] = str(content_length)

            # Set Content-Type Header.
            if content_type is not None:
                headers['Content-Type'] = content_type

        elif (content_type is None and
                status not in self._BODILESS_STATUS_CODES):
            headers['Content-Type'] = self._DEFAULT_CONTENT_TYPE

        headers = list(self._headers.items())

        # Load cookies.
        if self._cookies is not None:
            headers += [('Set-Cookie', c.OutputString())
                        for c in self._cookies.values()]

        self._start_response("%s %s" % (status,
                             const.HTTP_STATUS_CODES[status]),
                             headers)

        return self

    def __iter__(self):
        stream = self._stream
        status = self.status

        _STREAM_BLOCK_SIZE = self._STREAM_BLOCK_SIZE

        if status not in self._BODILESS_STATUS_CODES:
            try:
                # Rewind file like object to beginning
                stream.seek(0)
            except AttributeError:
                pass

            try:
                while True:
                    chunk = stream.read(_STREAM_BLOCK_SIZE)
                    if not chunk:
                        break
                    yield chunk
            except AttributeError:
                # If iterable body...
                try:
                    for i in range(0, len(stream), _STREAM_BLOCK_SIZE):
                        yield stream[i:i + _STREAM_BLOCK_SIZE]
                except TypeError:
                    pass

        yield b''

    def read(self):
        """Reads the entire Response body.
        """
        try:
            self._stream.seek(0)
            return self._stream.read()
        except AttributeError:
            return self._stream
