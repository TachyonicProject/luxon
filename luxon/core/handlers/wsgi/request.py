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

import base64
from cgi import FieldStorage
from http.cookies import SimpleCookie, CookieError

from luxon import g
from luxon.utils.http import parse_forwarded_header, parse_cache_control_header
from luxon.utils.files import FileObject
from luxon.utils.uri import parse_qs, parse_host
from luxon.utils import js
from luxon.utils.cast import to_tuple
from luxon.utils.timezone import TimezoneGMT, to_gmt
from luxon.utils.objects import dict_value_property
from luxon.utils.text import blank_to_none
from luxon.utils.imports import get_class
from luxon.exceptions import (HTTPInvalidHeader,
                              HTTPMissingHeader, HTTPMissingFormField)
from luxon.core.session import Session
from luxon.utils.http import ETags
from luxon.core.handlers.request import RequestBase


class Request(RequestBase):
    """Represents a clients HTTP request.

    Args:
        env (dict): A WSGI environment dict passed in from the server.
            As per PEP-3333.
        start_response (function): callback function supplied by the server
            which takes the HTTP status and headers as arguments.

    Attributes:
        access_hops(list): IP address of the original client, as well
            as any addresses of proxies fronting the WSGI server.

            The following request headers are checked, in order of
            preference, to determine the addresses:

                * Forwarded
                * X-Forwarded-For
                * X-Real-IP

            If none of these headers are available, the value of
            remote_addr attribute is returned.

            In RFC 7239, the access route may contain "unknown"
            and obfuscated identifiers, in addition to IPv4 and
            IPv6 addresses

            Headers can be forged by any client or proxy. Use this
            property with caution and validate all values before
            using them. Do not rely on the access route to authorize
            requests.

        app (str): The initial portion of the request URI's path that
            corresponds to the applicationm so that the
            application knows its virtual location. This could be an
            empty string, if the application corresponds to the root
            of the server.

            Reference to the 'SCRIPT_NAME' environ variable defined
            by PEP-3333.

        app_uri (str): Absolute URI to WSGI Application.

        id (str): Unique request identifier.

        env (str): Reference to the WSGI environ from the server.

        cache_control(obj): A luxon.utils.http.CacheControl obj populated from
                            the Request Headers.

        context_domain (str): The domain in which the request is currently
                              scoped.

        context_interface (str): The interface in which the request is
                                 currently scoped.

        context_region (str): The region in which the request is currently
                              scoped.

        context_tenant_id (str): The uuid of the Tenant in which the request is
                                 currently scoped.

        log: Dictionary/Property object to hold any data about the
            request which is specific to your app for appending to logs.
            (e.g. USERNAME)

        max_age (int): Maximum age, as specified for Cache control.

        method (str): HTTP method requested (e.g., 'GET', 'POST', etc.)
            May be set to new value by  'process' middleware method in order
            to influence routing.

        route (str): Path portion of the request URI. May be set to a new value
            by a 'process' middleware method in order to influence routing.
            Does not include the query string.

        tag (str): Route tag, used by policies to apply rules.

        forwarded_app_uri (str): Absolute original URI to WSGI Application.
        uri (str): The fully-qualified absolute URI for the request.
        forwarded_uri (str): URI for proxied requests.
        relative_uri (str): The path and query string portion.

        forwarded (list): Value of the Forwarded header, as a parsed list
            of :class:`luxon.core.http.headers.ForwardedElement` objects or
            if the header is missing None

            Reference RFC 7239, Section 4

        scheme (str): URL scheme used in the request. Either 'http' or 'https'.
            If the request was proxied, the scheme may not match what was
            originally requested by the client. For this 'forwarded_scheme' can
            be used used instead.

        forwarded_scheme (str): Original URL scheme requested by the user
            agent, if the request as proxied.  Either 'http' or https'.

            The following request headers are checked, in order of preference
            to determine the value:

                * Forwarded
                * X-Forwarded-For

            if none of these headers are availible or does not contain a
            'proto' parameter in the first hop, the value of the 'scheme' is
            returned.

            Reference RFC 7239, Section 1.

        host (str): Only host in request header field. The Host request-header
            field specifies the Internet host and port number of the resource
            being requested, as obtained from the original URI given by the
            user or referring resource.

            Use other methods such as port, netloc to include the port.

        forwarded_host (str): Original host request header as received
            by the first proxy in front of the application server.

            The following request headers are checked, in order of
            preference, to determine the forwarded scheme:

                * Forwarded
                * X-Forwarded-Host

            If none of the above headers are available, or if the
            Forwarded header is available but the host
            parameter is not included in the first hop, the value of
            host is returned instead.

            Reverse proxies are often configured to set the Host
            header directly to the one that was originally
            requested by the user agent; in that case, using
            host is sufficient.

            Refer RFC 7239, Section 4.

        port (int): Port used for the request. If the request URI does
            not specify a port, the default one for the given schema is
            returned (80 for HTTP and 443 for HTTPS).

        netloc (str): Returns the 'host:port' portion of the request
            URL. The port may be ommitted if it is the default one for
            the URL's schema (80 for HTTP and 443 for HTTPS).

        subdomain (str): Leftmost (i.e., most specific) subdomain from the
            hostname. If only a single domain name is given, `subdomain`
            will be None.

            Note:
                If the hostname in the request is an IP address, the value
                for `subdomain` is undefined.

        remote_addr(str): IP address of the closest client or proxy to
            the WSGI server.

            This property is determined by the value of 'REMOTE_ADDR'
            in the WSGI environment dict. Since this address is not
            derived from an HTTP header, clients and proxies can not
            forge it.

            If your application is behind one or more reverse proxies,
            you can use 'access_hops' attribute to retrieve the real
            IP address of the client.

        query_string (str): Query string portion of the request URI, without
            the preceding '?' character.

        query_params (dict): The mapping of request query parameter names to
            their values.  Where the parameter appears multiple times in the
            query string, the value mapped to that parameter key will be a list
            of all the values in the order seen.

        relative_resource_uri (str): Portion of the URI that comprising of the
                                     app and route.

        content_type (str): Value of the Content-Type header, or None if the
            header is missing.

        content_length (int): Value of the Content-Length header converted to
            an 'int' or None if the header is missing.

        stream: File-like input object for reading the body of the request.

        json (object): JSON Payload as object.

        form: cgi.FieldStorage() To get at submitted form data. As per Common
            Gateway Interface support provided by Python natively.

        form_dict (dict): Generated dictionary of form data submitted with
            field names as keys and values provided as either str, bytes or
            list. List values are for when multiple values exist for the same
            form field.

        form_array (list): Not Implemented yet, will provide ability to get
            a list of dicts providing providing form data similiar to PHP use
            case.

        form_json (str): Provides form and all its submitted data as json
            serialized string.

        date (datetime): Value of the Date Header. The header value is assumed
            to conform to RFC 1123.

        auth (str): Value of the Authorization header, or None if missing.
        user_agent (str): Value of the User-Agent header, or None if missing.
        referer (str): Value of the Referer header, or None if missing.
        expect (str): Value of the Expect header, or None if missing.
        if_match (str): Value of the If-Match header, or None if missing.

        if_none_match (str): Value of the If-None-Match header,
           or None if missing.

        if_modified_since (datetime): Value of the If-Modified-Since header,

        if_unmodified_since (datetime): Value of the If-Unmodified-Since
            header, or None if missing.

        if_range (str): Value of the If-Range header, or None.

        is_ajax (bool): Whether or not Request is an AJAX request.

        range (tuple of int): A 2-member 'tuple' parsed from the value
            of the Range header.

            The two members correspond to the first and last byte
            positions of the requested resource, inclusive. Negative
            indices indicate offset from the end of the resource,
            where -1 is the last byte, -2 is the second-to-last byte,
            and so forth.

            None continues would result in an HTTPBadRequest exception
            when the attribute is accessed.
            e.g. "bytes=0-0,-1".

        range_unit (str): Unit of the range parsed from the value of the
            Range header, or None if the header is missing.

        static (str): Cached value of the Applications static path.

        session (obj): Cached luxon.core.session.Session obj initialized
                       with session backend class specified in the settings.ini
                       file.

        user_token (str): The value of the token for the user's current
                          request.

        scope_token (str): The value of the scoped token for the user's current
                           scoped request.

        cookies (dict): A dict of name/value cookie pairs.
        is_bot (bool): If user-agent is detected as 'Bot' e.g Google Bot
        is_mobile (bool): If user-agent is detected as mobile. e.g. Iphone
    """
    _WSGI_CONTENT_HEADERS = ('CONTENT_TYPE', 'CONTENT_LENGTH')

    __slots__ = (
        'tag',
        'method',
        'route',
        'route_kwargs',
        'env',
        'response',
        '_cached_uri',
        '_cached_app_uri',
        '_cached_forwarded_app_uri',
        '_cached_forwarded_uri',
        '_cached_relative_uri',
        '_cached_forwarded',
        '_cached_query_string',
        '_cached_query_params',
        '_cached_content_type',
        '_cached_content_length',
        '_cached_params',
        '_cached_form',
        '_cached_access_hops',
        '_cached_cookies',
        '_cached_is_mobile',
        '_cached_is_bot',
        '_cached_static',
        '_cached_is_ajax',
        '_cached_json',
        '_cached_session',
        '_cached_log',
        '_cached_cache_control',
        '_cached_match',
        '_cached_none_match',
        '_user_token',
        '_scope_token',
    )

    def __init__(self, env, start_response):
        super().__init__()
        # Response Object for Request
        self.response = None

        # Set HTTP Request Method - Router uses this.
        self.method = env['REQUEST_METHOD']

        # WSGI Error Handling.
        # NOTE(cfrademan): To be looked into...

        # Set HTTP Request Application URL - Router uses this.
        # PEP 3333 specifies that PATH_INFO may be the
        # empty string, so normalize it in that case.
        route = env['PATH_INFO'] or '/'

        # PEP 3333 specifies that PATH_INFO variable are alwaysa
        # "bytes tunneled as latin-1" and must be encoded back
        self.route = route.encode('latin1').decode('utf-8', 'replace')

        # Set Environ
        self.env = env

        # Caching
        self._user_token = None
        self._scope_token = None
        self._cached_json = None
        self._cached_session = None
        self._cached_app_uri = None
        self._cached_forwarded_app_uri = None
        self._cached_uri = None
        self._cached_forwarded_uri = None
        self._cached_relative_uri = None
        self._cached_forwarded = None
        self._cached_query_string = None
        self._cached_query_params = None
        self._cached_content_type = None
        self._cached_content_length = None
        self._cached_params = None
        self._cached_form = None
        self._cached_access_hops = None
        self._cached_cookies = None
        self._cached_is_mobile = None
        self._cached_is_bot = None
        self._cached_static = None
        self._cached_is_ajax = None
        self._cached_log = None
        self._cached_cache_control = None
        self._cached_match = None
        self._cached_none_match = None

    @property
    def if_match(self):
        if self._cached_match is None:
            self._cached_match = ETags(self.get_header('if-match'))

        return self._cached_match

    @property
    def if_none_match(self):
        if self._cached_none_match is None:
            self._cached_none_match = ETags(self.get_header('if-none-match'))

        return self._cached_none_match

    @property
    def cache_control(self):
        return parse_cache_control_header(self.get_header('cache-control'))

    @property
    def max_age(self):
        if 'max-age' in self.cache_control:
            return int(self.cache_control['max-age'])
        else:
            return 0

    @property
    def stream(self):
        return self.env.get('wsgi.input')

    @property
    def json(self):
        if self._cached_json is None:
            self._cached_json = js.loads(self.stream.read())

        return self._cached_json

    def read(self, size=None):
        """Read at most size bytes, returned as a bytes object.

        Keyword Args:
            size (int): Size in octets to read.

        Returns:
            bytes: Bytes within the request payload.

        Raises:
            HTTPUnsupportedMediaType: Expected payload.
        """
        if size:
            return self.stream.read(size)
        return self.stream.read()

    def readline(self, size=None):
        """Read at most size bytes, returned as a bytes object.

        Keyword Args:
            size (int): Size in octets to read.

        Returns:
            bytes: Bytes within the request payload.

        Raises:
            HTTPUnsupportedMediaType: Expected payload.
        """
        if size:
            return self.stream.readline(size)
        return self.stream.readline()

    @property
    def session(self):
        if self._cached_session is None:
            expire = g.app.config.getint('sessions', 'expire', fallback=86400)
            backend = g.app.config.get(
                'sessions', 'backend',
                fallback='luxon.core.session:SessionFile')
            backend = get_class(backend)
            session_id = g.app.config.get(
                'sessions', 'session',
                fallback='luxon.core.session:cookie')
            session_id = get_class(session_id)

            self._cached_session = Session(
                session_id,
                expire=expire,
                backend=backend
            )

        return self._cached_session

    @property
    def log(self):
        if self._cached_log is None:
            self._cached_log = {}
            self._cached_log['REMOTE-HOST'] = self.remote_addr

        return self._cached_log

    @property
    def app(self):
        try:
            return self.env['SCRIPT_NAME']
        except KeyError:
            return ''

    @property
    def static(self):
        if self._cached_static is None:
            try:
                self._cached_static = \
                        g.app.config.application.static.rstrip('/')
            except AttributeError:
                self._cached_static = ''

        return self._cached_static

    @property
    def app_uri(self):
        if self._cached_app_uri is None:
            if g.app.config.get('application', 'use_forwarded') is True:
                self._cached_app_uri = (self.forwarded_scheme + '://' +
                                        self.forwarded_host +
                                        self.app)
            else:
                self._cached_app_uri = (
                    self.env['wsgi.url_scheme'] + '://' +
                    self.netloc +
                    self.app
                )

        return self._cached_app_uri

    @property
    def forwarded_app_uri(self):
        if self._cached_forwarded_app_uri is None:
            self._cached_forwarded_app_uri = (
                self.forwarded_scheme + '://' +
                self.forwarded_host +
                self.app
            )

        return self._cached_forwarded_app_uri

    @property
    def uri(self):
        if self._cached_uri is None:
            if g.app.config.get('application', 'use_forwarded') is True:
                self._cached_uri = self.forwarded_uri
            else:
                scheme = self.env['wsgi.url_scheme']

                value = (scheme + '://' +
                         self.netloc +
                         self.relative_uri)

                self._cached_uri = value

        return self._cached_uri

    url = uri

    @property
    def forwarded_uri(self):
        if self._cached_forwarded_uri is None:
            value = (self.forwarded_scheme + '://' +
                     self.forwarded_host +
                     self.relative_uri)

            self._cached_forwarded_uri = value

        return self._cached_forwarded_uri

    @property
    def relative_uri(self):
        if self._cached_relative_uri is None:
            if self.query_string:
                self._cached_relative_uri = (self.app + self.route + '?' +
                                             self.query_string)
            else:
                self._cached_relative_uri = self.app + self.route

        return self._cached_relative_uri

    @property
    def relative_resource_uri(self):
        return self.app + self.route

    @property
    def forwarded(self):
        if self._cached_forwarded is None:
            try:
                forwarded = self.env['HTTP_FORWARDED']
            except KeyError:
                return None

            self._cached_forwarded = parse_forwarded_header(forwarded)

        return self._cached_forwarded

    @property
    def scheme(self):
        return self.env['wsgi.url_scheme']

    @property
    def forwarded_scheme(self):
        if 'HTTP_FORWARDED' in self.env:
            first_hop = self.forwarded[0]
            scheme = first_hop.scheme or self.scheme
        else:
            try:
                scheme = self.env['HTTP_X_FORWARDED_PROTO'].lower()
            except KeyError:
                scheme = self.env['wsgi.url_scheme']
        return scheme

    @property
    def host(self):
        try:
            host_header = self.env['HTTP_HOST']
            host, port = parse_host(host_header)
        except KeyError:
            # According to PEP-3333, this header
            # will always be present.
            host = self.env['SERVER_NAME']

        return host

    @property
    def forwarded_host(self):
        if 'HTTP_FORWARDED' in self.env:
            first_hop = self.forwarded[0]
            host = first_hop.host or self.host
        else:
            try:
                host = self.env['HTTP_X_FORWARDED_HOST']
            except KeyError:
                host = self.host

        return host

    @property
    def port(self):
        try:
            host_header = self.env['HTTP_HOST']
            default_port = 80 if self.env['wsgi.url_scheme'] == 'http' else 443
            host, port = parse_host(host_header, default_port=default_port)
        except KeyError:
            # PEP-3333 requires that the port never be an empty string.
            port = int(self.env['SERVER_PORT'])

        return port

    @property
    def netloc(self):
        env = self.env
        protocol = env['wsgi.url_scheme']

        # As per PEP-3333 use the host header first if present.
        try:
            netloc_value = env['HTTP_HOST']
        except KeyError:
            netloc_value = env['SERVER_NAME']

            port = env['SERVER_PORT']
            if protocol == 'https':
                if port != '443':
                    netloc_value += ':' + port
            else:
                if port != '80':
                    netloc_value += ':' + port

        return netloc_value

    @property
    def subdomain(self):
        subdomain, sep, remainder = self.host.partition('.')
        return subdomain if sep else None

    @property
    def remote_addr(self):
        return self.env.get('REMOTE_ADDR')

    @property
    def access_hops(self):
        if self._cached_access_hops is None:
            if 'HTTP_FORWARDED' in self.env:
                self._cached_access_hops = []
                for hop in self.forwarded:
                    if hop.src is not None:
                        host, __ = parse_host(hop.src)
                        self._cached_access_hops.append(host)
            elif 'HTTP_X_FORWARDED_FOR' in self.env:
                addresses = self.env['HTTP_X_FORWARDED_FOR'].split(',')
                self._cached_access_hops = [ip.strip() for ip in addresses]
            elif 'HTTP_X_REAL_IP' in self.env:
                self._cached_access_hops = [self.env['HTTP_X_REAL_IP']]
            elif 'REMOTE_ADDR' in self.env:
                self._cached_access_hops = [self.env['REMOTE_ADDR']]
            else:
                self._cached_access_hops = []

        return self._cached_access_hops

    @property
    def query_string(self):
        # URI QUERY_STRING try/catch cheaper and faster
        if self._cached_query_string is not None:
            return self._cached_query_string

        try:
            if self.env['QUERY_STRING'].strip() != '':
                self._cached_query_string = self.env['QUERY_STRING']
            else:
                self._cached_query_string = None
        except KeyError:
            self._cached_query_string = None

        return self._cached_query_string

    @property
    def query_params(self):
        # URI QUERY_STRING try/catch cheaper and faster
        if self._cached_query_params is None:
            try:
                if self.query_string:
                    self._cached_query_params = parse_qs(self.query_string,
                                                         True)
                else:
                    self._cached_query_params = {}
            except KeyError:
                self._cached_query_params = {}

        return self._cached_query_params

    @property
    def content_type(self):
        if self._cached_content_type is not None:
            return self._cached_content_type

        # CONTENT_TYPE try/catch cheaper and faster
        try:
            self._cached_content_type = self.env['CONTENT_TYPE']
        except KeyError:
            self._cached_content_type = None

        return self._cached_content_type

    @property
    def content_length(self):
        # CONTENT_LENGTH try/catch cheaper and faster
        try:
            length = int(self.env['CONTENT_LENGTH'])
            if length < 0:
                raise HTTPInvalidHeader(
                    'Content-Length',
                    'Negative Length not allowed.'
                )
            return length
        except KeyError:
            return 0
        except ValueError:
            raise HTTPInvalidHeader('Content-Length',
                                    'Not an integer')

    @property
    def form(self):
        if self._cached_form is not None:
            return self._cached_form

        environ = {'REQUEST_METHOD': 'POST',
                   'CONTENT_LENGTH': self.content_length}

        if 'CONTENT_TYPE' in self.env:
            environ['CONTENT_TYPE'] = self.env['CONTENT_TYPE']

        self._cached_form = FieldStorage(fp=self, keep_blank_values=True,
                                         environ=environ)

        return self._cached_form

    @property
    def form_dict(self):
        form = self.form

        json_safe_object = {}

        for prop in form:
            field = form[prop]
            if isinstance(field, list):
                for item in field:
                    if prop not in json_safe_object:
                        json_safe_object[prop] = []
                    if item.filename:
                        data = base64.encodestring(item.file.read())
                        file_obj = {'name': item.filename,
                                    'type': item.type,
                                    'base64': data}
                        json_safe_object[prop].append(file_obj)
                    else:
                            json_safe_object[prop].append(
                                blank_to_none(item.value)
                            )
            else:
                if field.filename:
                    data = base64.encodestring(field.file.read())
                    file_obj = {'name': field.filename,
                                'type': field.type,
                                'base64': data}
                    json_safe_object[prop] = file_obj
                else:
                    json_safe_object[prop] = blank_to_none(field.value)

        return json_safe_object

    @property
    def form_array(self):
        raise NotImplementedError('Todo!')

    @property
    def form_json(self):
        return js.dumps(self.form_dict)

    def get_header(self, name, required=False, default=None):
        """Retrieve the raw string value for the given header.

        Args:
            name (str): Header name, case-insensitive (e.g., 'Content-Type')

        Keyword Args:
            required (bool): Set to 'True' to raise
                'HTTPMissingHeader' instead of returning
                gracefully when header is not found
                (default 'False').
            default (any): Value to return if the header
                is not found (default None).

        Returns:
            str: The value of the specified header if it exists, or
            the default value if the header is not found and is not
            required.

        Raises:
            HTTPMissingHeader: The header was not found in the request, but
                it was required.
        """
        wsgi_name = name.upper().replace('-', '_')

        try:
            return self.env['HTTP_' + wsgi_name]

        except KeyError:
            if wsgi_name in self._WSGI_CONTENT_HEADERS:
                try:
                    return self.env[wsgi_name]
                except KeyError:
                    pass

            if not required:
                return default

            raise HTTPMissingHeader(name)

    def get_header_as_datetime(self, header, required=False, obs_date=False):
        """Return an HTTP header with HTTP-Date values as a datetime.

        Args:
            name (str): Header name, case-insensitive (e.g., 'Date')

        Keyword Args:
            required (bool): raise HTTPBadRequest (default False)

            obs_date (bool): Support obs-date formats according to
                RFC 7231 (e.g. Sunday, 06-Nov-94 08:49:37 GMT)
                (default False).

        Returns:
            datetime: The value of the specified header if it exists,
                or None if the header is not found and is not required.

        Raises:
            HTTPBadRequest: The header was not found in the request, but
                it was required.

            HttpInvalidHeader: The header contained a malformed/invalid value.
        """
        try:
            http_date = self.get_header(header, required=required)
            if http_date is not None:
                return to_gmt(http_date, src=TimezoneGMT())
        except TypeError:
            return None
        except ValueError:
            msg = "It must be formatted according to RFC 7231, Section 7.1.1.1"
            raise HTTPInvalidHeader(header, msg)

    @property
    def user_token(self):
        if self._user_token is not None:
            return self._user_token

        if self.get_header('X-Auth-Token'):
            self._user_token = self.get_header('X-Auth-Token')
        elif self.host in self.cookies and 'token' in self.session:
            return self.session['token']

        return self._user_token

    @user_token.setter
    def user_token(self, value):
        self._user_token = value

        # if value is None:
        #     value = ''

        self.session['token'] = value
        self.session.save()

    @property
    def scope_token(self):
        if self._scope_token is not None:
            return self._scope_token

        elif self.host in self.cookies and 'scoped' in self.session:
            return self.session['scoped']

        return self._scope_token

    @scope_token.setter
    def scope_token(self, value):
        self._scope_token = value

        # if value is None:
        #     value = ''

        self.session['scoped'] = value
        self.session.save()

    @property
    def context_region(self):
        if self.get_header('X-Region'):
            return self.get_header('X-Region')

        elif self.host in self.cookies and 'region' in self.session:
            return self.session.get('region')

        return g.app.config.get('restapi', 'region', fallback=None)

    @property
    def context_interface(self):
        if self.get_header('X-Interface'):
            return self.get_header('X-Interface')

        elif self.host in self.cookies and 'interface' in self.session:
            return self.session.get('interface')

        return g.app.config.get('restapi', 'interface', fallback='public')

    @property
    def context_domain(self):
        if self.get_header('X-Domain'):
            return self.get_header('X-Domain')

        elif self.host in self.cookies and 'domain' in self.session:
            return self.session.get('domain')

        return self.credentials.domain

    @property
    def context_tenant_id(self):
        if self.get_header('X-Tenant-Id'):
            return self.get_header('X-Tenant-Id')

        elif self.host in self.cookies and 'tenant_id' in self.session:
            return self.session.get('tenant_id')

        return self.credentials.tenant_id

    def get_first(self, field, required=False, default=None):
        """Get the value for the given field name in form.

        This method always returns only one value associated with form field
        name. The method returns only the first value in case that more
        values were posted under such name. Please note that the order in which
        the values are received may vary from browser to browser and should not
        be counted on. If no such form field or value exists then the method
        returns the value specified by the optional parameter default. This
        parameter defaults to None if not specified.

        Args:
            field (str): Form field name.

        Keyword Args:
            required (bool): Set to 'True' to raise
                'HTTPMissingParam' instead of returning
                gracefully when field is not found
                (default 'False').

            default (str): Value to return if field is not found.

        Returns:
            str: String Value of Field.

        Raises:
            HTTPMissinParam: The parameter was not found in the request, but
                it was required.

            HTTPUnsupportedMediaType: Expected payload.
        """
        form = self.form

        if required is True and field not in form:
            raise HTTPMissingFormField(field)

        if default is not None and required is False:
            default = str(default)

        try:
            if field in form:
                return blank_to_none(form.getfirst(field), default)
            else:
                return default
        except TypeError:
            pass

        return default

    def get_list(self, field, required=False):
        """Get list of values for the requested field name in form.

        Returns an empty list if the file doesn’t exist. It’s guaranteed to
        return a list unless the field is required as per keyword args.

        Args:
            field (str): Form field name.

        Keyword Args:
            required (bool): Set to 'True' to raise
                'HTTPMissingParam' instead of returning
                gracefully when field is not found
                (default 'False').

        Returns:
            tuple: List of values.

        Raises:
            HTTPMissinParam: The parameter was not found in the request, but
                it was required.

            HTTPUnsupportedMediaType: Expected payload.
        """
        form = self.form

        if required is True and field not in form:
            raise HTTPMissingFormField(field)

        try:
            return to_tuple(form.getlist(field))
        except TypeError:
            pass

        if required is True:
            raise HTTPMissingFormField(field)

        return ()

    def get_file(self, field, required=False):
        """Get file for the given field name in form.

        This method always returns only one value associated with form field
        name. The method returns only the first value in case that more
        values were posted under such name. Please note that the order in which
        the values are received may vary from browser to browser and should not
        be counted on. If no such form field or value exists then the method
        returns the value specified by the optional parameter default. This
        parameter defaults to None if not specified.

        Args:
            field (str): Form field name.

        Keyword Args:
            required (bool): Set to 'True' to raise
                'HTTPMissingParam' instead of returning
                gracefully when field is not found
                (default 'False').

        Returns:
            tuple: FileObject Instance.

        Raises:
            HTTPMissinParam: The parameter was not found in the request, but
                it was required.

            HTTPUnsupportedMediaType: Expected payload.
        """
        form = self.form

        if required is True and field not in form:
            raise HTTPMissingFormField(field)

        try:
            value = form[field]
            if isinstance(value, list):
                if value[0].filename:
                    return FileObject(value[0].filename,
                                      value[0].type,
                                      value[0].file)

            else:
                if value.filename:
                    return FileObject(value.filename,
                                      value.type,
                                      value.file)
        except TypeError:
            pass
        except KeyError:
            pass

        if required is True:
            raise HTTPMissingFormField(field)

        return (None, None, None)

    def get_files(self, field, required=False):
        """Get multiple files for the given field name in form.

        Returns an empty list if the file doesn’t exist. It’s guaranteed to
        return a list unless the field is required as per keyword args.

        Args:
            field (str): Form field name.

        Keyword Args:
            required (bool): Set to 'True' to raise
                'HTTPMissingParam' instead of returning
                gracefully when field is not found
                (default 'False').

        Returns:
            tuple: Sequence of FileObject Instances.

        Raises:
            HTTPMissinParam: The parameter was not found in the request, but
                it was required.

            HTTPUnsupportedMediaType: Expected payload.
        """

        files = []
        form = self.form

        if required is True and field not in form:
            raise HTTPMissingFormField(field)

        try:
            value = form[field]
            if isinstance(value, list):
                for item in value:
                    if item.filename:
                        obj = FileObject(item.filename,
                                         item.type,
                                         item.file)
                        files.append(obj)

            else:
                if value.filename:
                    obj = FileObject(value.filename,
                                     value.type,
                                     value.file)
                    files.append(obj)

            return tuple(files)

        except TypeError:
            pass
        except KeyError:
            pass

        return tuple(files)

    def get_all_files(self):
        """Get multiple files for the form.

        Returns an empty list if no files. It’s guaranteed to
        return a list.

        Returns:
            tuple: Sequence of FileObject Instances.
        """
        files = []
        form = self.form

        try:
            for field in form:
                files += self.get_files(field)

            return tuple(files)

        except TypeError:
            return ()
        except TypeError:
            return ()

    @property
    def date(self):
        return self.get_header_as_datetime('Date')

    @property
    def if_modified_since(self):
        return self.get_header_as_datetime('If-Modified-Since')

    @property
    def if_unmodified_since(self):
        return self.get_header_as_datetime('If-Unmodified-Since')

    @property
    def range(self):
        try:
            value = self.env['HTTP_RANGE']
            if '=' in value:
                unit, sep, req_range = value.partition('=')
            else:
                msg = "The value must be prefixed with a" + \
                      " range unit, e.g. 'bytes='"
                raise HTTPInvalidHeader('Range', msg)
        except KeyError:
            return None

        if ',' in req_range:
            msg = 'The value must be a continuous range.'
            raise HTTPInvalidHeader('Range', msg)

        try:
            first, sep, last = req_range.partition('-')

            if not sep:
                raise ValueError()

            if first:
                return (int(first), int(last or -1))
            elif last:
                return (-int(last), -1)
            else:
                msg = 'The range offsets are missing.'
                raise HTTPInvalidHeader(msg, 'Range')

        except ValueError:
            msg = ('Range must be formatted according to RFC 7233.')
            raise HTTPInvalidHeader('Range', msg)

    @property
    def range_unit(self):
        try:
            value = self.env['HTTP_RANGE']

            if '=' in value:
                unit, sep, req_range = value.partition('=')
                return unit
            else:
                msg = "The value must be prefixed with a" + \
                      " range unit, e.g. 'bytes='"
                raise HTTPInvalidHeader('Range', msg)
        except KeyError:
            return None

    @property
    def cookies(self):
        if self._cached_cookies is None:
            cookie_header = self.get_header('Cookie', default='')
            parser = SimpleCookie()
            for cookie_part in cookie_header.split('; '):
                try:
                    parser.load(cookie_part)
                except CookieError:
                    pass
            cookies = {}
            for morsel in parser.values():
                cookies[morsel.key] = morsel.value

            self._cached_cookies = cookies

        return self._cached_cookies.copy()

    @property
    def is_ajax(self):
        if self._cached_is_ajax is None:
            rw = self.get_header('X_REQUESTED_WITH')
            if rw is not None and 'xmlhttprequest' in rw.lower():
                self._cached_is_ajax = True
            else:
                self._cached_is_ajax = False

        return self._cached_is_ajax

    @property
    def is_mobile(self):
        """Returns True if mobile client is used.
        """
        if self._cached_is_mobile is None:
            agent = self.user_agent.lower()
            devices = ('iphone',
                       'android',)

            for device in devices:
                if device in agent:
                    self._cached_is_mobile = True
                    break

            self._cached_is_mobile = False

        return self._cached_is_mobile

    @property
    def is_bot(self):
        """Returns True if client is bot.
        """
        if self._cached_is_bot is None:
            agent = self.user_agent.lower()
            bots = ('google',
                    'bot',
                    'bingpreview',
                    'yandex',
                    'yahoo',
                    'slurp',
                    'baidu',)

            for bot in bots:
                if bot in agent:
                    self._cached_is_bot = True
                    break

            self._cached_is_bot = False

        return self._cached_is_bot

    auth = dict_value_property('env', 'HTTP_AUTHORIZATION')
    user_agent = dict_value_property('env', 'HTTP_USER_AGENT')
    referer = dict_value_property('env', 'HTTP_REFERER')
    expect = dict_value_property('env', 'HTTP_EXPECT')
    if_range = dict_value_property('env', 'HTTP_IF_RANGE')
