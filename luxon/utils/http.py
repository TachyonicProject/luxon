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
import re
import cgi
import string
from collections import OrderedDict

import requests
from luxon import g
from luxon import js
from luxon import __identity__
from luxon import GetLogger
from luxon.utils.timer import Timer
from luxon.exceptions import (NoContextError,
                              HTTPClientInvalidHeader,
                              HTTPClientInvalidURL,
                              HTTPClientInvalidSchema,
                              HTTPClientMissingSchema,
                              HTTPClientConnectionError,
                              HTTPClientProxyError,
                              HTTPClientSSLError,
                              HTTPClientTimeoutError,
                              HTTPClientConnectTimeoutError,
                              HTTPClientReadTimeoutError,
                              HTTPClientContentDecodingError,
                              HTTPError)
from luxon.constants import HTTP_STATUS_CODES
from luxon.utils.encoding import if_unicode_to_bytes, if_bytes_to_unicode
from luxon.exceptions import JSONDecodeError
from luxon.utils.strings import unquote_string
from luxon.structs.cidict import CiDict
from luxon.utils.hashing import md5sum

log = GetLogger(__name__)

_etag_re = re.compile(r'^([Ww]/)?"?(.*?)"?$')


def etagger(*args):
    to_hash = b"".join([
        if_unicode_to_bytes(str(arg) or b'') for arg in args
    ])
    if to_hash != b'':
        return md5sum(to_hash)


class ETags(object):
    def __init__(self, etags=None, set_callback=None):
        self._strong = []
        self._weak = []
        self._star_tag = False
        self._set_callback = set_callback
        if etags:
            self.set(etags)

    def set(self, etags):
        if not isinstance(etags, (list, tuple, )):
            etags = parse_headers_values(etags)

        for etag in etags:
            match = _etag_re.match(etag)
            if not match:
                print("Invalid Etag '%s'" % etag)
            is_weak, etag = match.groups()
            if etag == "*":
                self._star_tag = True
                continue
            if is_weak:
                self._weak.append(etag)
                if self._set_callback:
                    self._set_callback('etag', 'W/"%s"' % etag)
            else:
                self._strong.append(etag)
                if self._set_callback:
                    self._set_callback('etag', '"%s"' % etag)

    def __len__(self):
        return len(self._strong + self._weak)

    def contains(self, etags, strong=True):
        if self._star_tag:
            return True

        if not isinstance(etags, ETags):
            etags = ETags(etags)

        if len(etags) == 0:
            if etags._star_tag:
                return True
            else:
                return False

        if (strong is True and
                set(
                    etags._strong + etags._weak
                ).issubset(self._strong)):
            return True

        if (strong is False and
                set(
                    etags._strong + etags._weak
                ).issubset(
                    self._strong + self._weak
                )):
            return True

        return False

    def __contains__(self, etags):
        return self.contains(etags)

    def to_header(self):
        """Convert the etags set into a HTTP header string."""
        if self.star_tag:
            return '*'
        return ', '.join(
            ['"%s"' % x for x in self._strong] +
            ['W/"%s"' % x for x in self._weak]
        )


def parse_headers_values(header):
    """Parses comma seperated headers

    Headers with options and values using = seperator
    are trimmed from spaces.

    Returns list of header options and valuea.
    """
    if header is None:
        return []

    return [
        "=".join([value.strip(' ') for value in header.split('=')])
        for header in list(map(str.strip, header.split(',')))
    ]


class ForwardedElement(object):
    """Representation of Forwarded header.

    Reference to RFC 7239, Section 4.

    Attributes:
        src (str): The value of the 'for' parameter or if the
            parameter is absent None. Identifies the node
            making the request to the proxy.
        by (str): The value of the 'by' parameter or if the
            the parameter is absent None. Identifies the
            client-facing interface of the proxy.
        host (str): The value of the 'host' parameter or if
            the parameter is absent None. Provides the host
            request header field as received by the proxy.
        proto (str): The value of the 'proto' parameter or
            if the parameter is absent None. Indicates the
            protocol that was used to make the request to
            the proxy.
    """

    __slots__ = ('src', 'by', 'host', 'proto')

    def __init__(self):
        self.src = None
        self.by = None
        self.host = None
        self.proto = None


def parse_forwarded_header(forwarded):
    """Parses the value of a Forwarded header.

    Parse Forwarded headers as specified by RFC 7239:

        * Check that every value has valid syntax in general.
        * Un-escapes found escape sequences.

    Arguments:
        forwarded (str): Value of a Forwarded header

    Returns:
        list: Sequence of ForwardedElement instances.
    """
    tchar = string.digits + string.ascii_letters + r"!#$%&'*+.^_`|~-"

    token = r'[{tchar}]+'.format(tchar=tchar)

    qdtext = r'[{0}]'.format(
        r''.join(chr(c)
                 for c in (0x09, 0x20, 0x21) + tuple(range(0x23, 0x7F))))

    quoted_pair = r'\\[\t !-~]'

    quoted_string = r'"(?:{quoted_pair}|{qdtext})*"'.format(
        qdtext=qdtext, quoted_pair=quoted_pair)

    forwarded_pair = (
        r'({token})=({token}|{quoted_string})'.format(
            token=token,
            quoted_string=quoted_string))

    forwarded_pair_re = re.compile(forwarded_pair)

    elements = []

    pos = 0
    end = len(forwarded)
    need_separator = False
    parsed_element = None

    while 0 <= pos < end:
        match = forwarded_pair_re.match(forwarded, pos)

        if match is not None:
            if need_separator:
                pos = forwarded.find(',', pos)
            else:
                pos += len(match.group(0))
                need_separator = True

                name, value = match.groups()

                # Reference to RFC 7239.
                # Forwarded parameter names are
                # not case sensitive.
                name = name.lower()

                if value[0] == '"':
                    value = unquote_string(value)
                if not parsed_element:
                    parsed_element = ForwardedElement()
                if name == 'by':
                    parsed_element.by = value
                elif name == 'for':
                    parsed_element.src = value
                elif name == 'host':
                    parsed_element.host = value
                elif name == 'proto':
                    # RFC 7239 only requires that 'proto' value
                    # HOST ABNF described in RFC 7230.
                    parsed_element.proto = value.lower()
        elif forwarded[pos] == ',':
            need_separator = False
            pos += 1

            if parsed_element:
                elements.append(parsed_element)
                parsed_element = None

        elif forwarded[pos] == ';':
            need_separator = False
            pos += 1

        elif forwarded[pos] in ' \t':
            # Allow whitespace even between forwarded-pairs.
            # This however is not permitted in RFC 7239 doesn't.
            pos += 1

        else:
            pos = forwarded.find(',', pos)

    if parsed_element:
        elements.append(parsed_element)

    return elements


def content_type_encoding(header):
    """Gets the encoding from Content-Type header.

    Args:
        header (str): Content-Type header value.
    """

    if not header:
        return None

    content_type, params = cgi.parse_header(header)

    if 'charset' in params:
        return params['charset'].strip("'\"")

    if 'text' in content_type:
        return 'ISO-8859-1'

    return None


CACHE_CONTROL_RE = re.compile(r"[a-z_\-]+=[0-9]+", re.IGNORECASE)
CACHE_CONTROL_OPTION_RE = re.compile(r"[a-z_\-] +", re.IGNORECASE)


class CacheControl(object):
    __slots__ = ('max_age',
                 'max_stale',
                 'min_fresh',
                 'no_cache',
                 'no_store',
                 'no_transform',
                 'only_if_cached',
                 'must_revalidate',
                 'public',
                 'private',
                 'proxy_revalidate',
                 's_maxage')

    def __getattribute__(self, attr):
        try:
            return super().__getattribute__(attr)
        except AttributeError:
            if attr not in self.__slots__:
                raise
            return None


def parse_cache_control_header(header):
    cachecontrol = CacheControl()

    if header is not None:
        CACHE_CONTROL_OPTION_RE.findall(header)
        for option in CACHE_CONTROL_OPTION_RE.findall(header):
            option = option.replace('-', '_').lower().strip()
            setattr(cachecontrol, option, True)

        CACHE_CONTROL_RE.findall(header)
        for option in CACHE_CONTROL_RE.findall(header):
            option, value = option.split('=')
            option = option.replace('-', '_').lower().strip()
            setattr(cachecontrol, option, value.strip())

    return cachecontrol


def _debug(method, url, params, payload, request_headers, response_headers,
           response, status_code, elapsed):
    if g.debug:
        log.debug('Method: %s' % method +
                  ', URL: %s' % url +
                  ', Params: %s' % params +
                  ' (%s %s)' % (status_code, HTTP_STATUS_CODES[status_code]),
                  timer=elapsed)
        for header in request_headers:
            log.debug('Request Header: %s="%s"' % (header,
                                                   request_headers[header]))
        for header in response_headers:
            log.debug('Response Header: %s="%s"' % (header,
                                                    response_headers[header]))
        log.debug(payload, prepend='Request Payload')
        log.debug(response, prepend='Response Payload')


class Response(object):
    __slots__ = ('_result', '_cached_json', '_cached_headers',)

    def __init__(self, requests_response):
        self._cached_json = None
        self._cached_headers = None
        self._result = requests_response

    @property
    def iter_content(self):
        return self._result.iter_content()

    @property
    def iter_lines(self):
        return self._result.iter_lines()

    @property
    def content(self):
        return self._result.content

    @property
    def headers(self):
        if self._cached_headers is None:
            self._cached_headers = CiDict()
            self._cached_headers.update(self._result.headers)
        return self._cached_headers

    @property
    def text(self):
        return if_bytes_to_unicode(self.content, self.encoding)

    @property
    def status_code(self):
        return int(self._result.status_code)

    def __len__(self):
        return len(self.body)

    @property
    def content_type(self):
        try:
            header = self.headers['content-type']
            content_type, params = cgi.parse_header(header)
            if content_type is not None:
                return str(content_type).upper()
            else:
                return None
        except KeyError:
            return None

    @property
    def json(self):
        if self._cached_json is None:
            if self.encoding is not None and self.encoding != 'UTF-8':
                raise HTTPClientContentDecodingError(
                    'JSON requires UTF-8 Encoding') from None

            try:
                if self.status_code != 204:
                    self._cached_json = js.loads(self.content)
                else:
                    self._cached_json = None

            except JSONDecodeError as e:
                raise HTTPClientContentDecodingError(
                    'JSON Decode: %s' % e) from None

        return self._cached_json

    @property
    def encoding(self):
        try:
            header = self.headers['content_type']
            content_type, params = cgi.parse_header(header)
            if 'charset' in params:
                return params['charset'].strip("'\"").upper()
            if 'text' in content_type:
                return 'ISO-8859-1'
        except KeyError:
            pass

        return self._result.encoding.upper()

    def close(self):
        self._result.close()


def request(client, method, uri, params=None,
            data=None, headers={}, stream=False, **kwargs):

    with Timer() as elapsed:
        try:
            if g.current_request.user_token:
                headers['X-Auth-Token'] = g.current_request.user_token
            if g.current_request.context_domain:
                headers['X-Domain'] = g.current_request.context_domain
            if g.current_request.context_tenant_id:
                headers['X-Tenant-Id'] = g.current_request.context_tenant_id
        except NoContextError:
            pass

        for kwarg in kwargs:
            headers[kwarg] = kwargs

        if data is not None:
            if hasattr(data, 'json'):
                data = data.json
            elif isinstance(data, (dict, list, OrderedDict)):
                data = js.dumps(data)
            data = if_unicode_to_bytes(data)

        if uri.startswith('http'):
            url = uri
        elif client._url is not None:
            url = client._url.rstrip('/') + '/' + uri.lstrip('/')

        if isinstance(data, bytes):
            headers['Content-Length'] = str(len(data))

        try:
            response = Response(client._s.request(method.upper(),
                                                  url,
                                                  params=params,
                                                  data=data,
                                                  headers=headers,
                                                  stream=stream))
            if response.status_code > 400:
                try:
                    title = None
                    description = None
                    if 'error' in response.json:
                        error = response.json['error']
                        try:
                            title = error.get('title')
                            description = error.get('description')
                        except AttributeError:
                            pass

                    raise HTTPError(response.status_code, description, title)
                except HTTPClientContentDecodingError:
                    raise HTTPError(response.status_code)

        # except requests.exceptions.InvalidProxyURL as e:
        #    raise HTTPClientInvalidProxyURL(e)
        except requests.exceptions.InvalidHeader as e:
            raise HTTPClientInvalidHeader(e)
        except requests.exceptions.InvalidURL as e:
            raise HTTPClientInvalidURL(e)
        except requests.exceptions.InvalidSchema as e:
            raise HTTPClientInvalidSchema(e)
        except requests.exceptions.MissingSchema as e:
            raise HTTPClientMissingSchema(e)
        except requests.exceptions.ConnectionError as e:
            raise HTTPClientConnectionError(e)
        except requests.exceptions.ProxyError as e:
            raise HTTPClientProxyError(e)
        except requests.exceptions.SSLError as e:
            raise HTTPClientSSLError(e)
        except requests.exceptions.Timeout as e:
            raise HTTPClientTimeoutError(e)
        except requests.exceptions.ConnectTimeout as e:
            raise HTTPClientConnectTimeoutError(e)
        except requests.exceptions.ReadTimeout as e:
            raise HTTPClientReadTimeoutError(e)
        except requests.exceptions.HTTPError as e:
            raise HTTPError(e.response.status_code, e)

        _debug(method, url, params, data, headers, response.headers,
               response.content, response.status_code, elapsed())

    return response


class Stream(object):
    def __init__(self, client, method, uri, params=None,
                 data=None, headers={}, **kwargs):
        self._client = client
        self._method = method
        self._uri = uri
        self._params = params
        self._data = data
        self._headers = headers
        self._response = None
        self._kwargs = kwargs

    def __enter__(self):
        self._response = request(self._client, self._method, self._uri,
                                 params=self._params,
                                 data=self._data,
                                 headers=self._headers,
                                 stream=True,
                                 **self._kwargs)
        return self._response

    def __exit__(self, type, value, traceback):
        self._response.close()


class Client(object):
    def __init__(self, url=None, timeout=(2, 8),
                 auth=None, verify=True,
                 cert=None):

        self._url = url
        self._s = requests.Session()
        self._s.headers.update({'User-Agent': __identity__})

        if auth:
            self._s.auth = auth

        self._s.verify = verify
        self._s.cert = cert
        self._s.timeout = timeout

    def stream(self, method, uri, params=None,
               data=None, headers={}, **kwargs):

        return Stream(self,
                      method,
                      uri,
                      params,
                      data,
                      headers,
                      **kwargs)

    def execute(self, method, uri, params=None,
                data=None, headers={}, **kwargs):

        return request(self, method, uri,
                       params=params,
                       data=data,
                       headers=headers,
                       stream=False,
                       **kwargs)

    def __setitem__(self, header, value):
        if self._s is None:
            raise ValueError('Not within context')
        self._s.headers.update({header: value})


def http_moved_permanently(url):
    """ 301 Moved Permanently.

    The HTTP response status code 301 Moved Permanently is used
    for permanent URL redirection, meaning current links or records
    using the URL that the response is received for should be updated.
    The new URL should be provided in the Location field included with
    the response. The 301 redirect is considered a best practice for
    upgrading users from HTTP to HTTPS.

    Args:
        url (str): Redirected to URL.
    """
    req = g.current_request
    resp = g.current_request.response

    if 'http' not in url.lower():
        url = "%s/%s" % (req.app_uri, url.strip('/'))
    resp.status = 301
    resp.set_header('Location', url)


def http_found(url):
    """ 302 Found.

    The HTTP response status code 302 Found is a common way of
    performing URL redirection.

    An HTTP response with this status code will additionally provide
    a URL in the header field location. The user agent (e.g. a web browser)
    is invited by a response with this code to make a second, otherwise
    identical, request to the new URL specified in the location field.
    The HTTP/1.0 specification (RFC 1945) initially defined this code,
    and gives it the description phrase "Moved Temporarily".

    Many web browsers implemented this code in a manner that violated
    this standard, changing the request type of the new request to GET,
    regardless of the type employed in the original request (e.g. POST).
    For this reason, HTTP/1.1 (RFC 2616) added the new status codes 303
    and 307 to disambiguate between the two behaviours, with 303 mandating
    the change of request type to GET, and 307 preserving the request
    type as originally sent. Despite the greater clarity provided by this
    disambiguation, the 302 code is still employed in web frameworks to
    preserve compatibility with browsers that do not implement the
    HTTP/1.1 specification.

    As a consequence, the update of RFC 2616 changes the definition to
    allow user agents to rewrite POST to GET.

    Args:
        url (str): Redirected to URL.
    """
    req = g.current_request
    resp = g.current_request.response

    if 'http' not in url.lower():
        url = "%s/%s" % (req.app_uri, url.strip('/'))
    resp.status = 302
    resp.set_header('Location', url)


def http_see_other(url):
    """ 303 See Other.

    The HTTP response status code 303 See Other is a way to redirect
    web applications to a new URI, particularly after a HTTP POST has
    been performed, since RFC 2616 (HTTP 1.1).

    According to RFC 7231, which obsoletes RFC 2616, "A 303 response to
    a GET request indicates that the origin server does not have a
    representation of the target resource that can be transferred by the
    server over HTTP. However, the Location field value refers to a resource
    that is descriptive of the target resource, such that making a retrieval
    request on that other resource might result in a representation that is
    useful to recipients without implying that it represents the original
    target resource."

    This status code should be used with the location header, as described
    below. If a server responds to a POST or other non-idempotent request
    with a 303 See Other response and a value for the location header, the
    client is expected to obtain the resource mentioned in the location
    header using the GET method; to trigger a request to the target resource
    using the same method, the server is expected to provide a 307 Temporary
    Redirect response.

    303 See Other has been proposed as one way of responding to a request for
    a URI that identifies a real-world object according to Semantic Web theory
    (the other being the use of hash URIs). For example,
    if http://www.example.com/id/alice identifies a person, Alice, then it
    would be inappropriate for a server to respond to a GET request with 200 OK
    , as the server could not deliver Alice herself. Instead the server would
    issue a 303 See Other response which redirected to a separate URI providing
    a description of the person Alice.

    303 See Other can be used for other purposes. For example, when building a
    RESTful web API that needs to return to the caller immediately but continue
    executing asynchronously (such as a long-lived image conversion), the web
    API can provide a status check URI that allows the original client who
    requested the conversion to check on the conversion's status. This status
    check web API should return 303 See Other to the caller when the task is
    complete, along with a URI from which to retrieve the result in the
    Location HTTP header field.

    Args:
        url (str): Redirected to URL.
    """
    req = g.current_request
    resp = g.current_request.response

    if 'http' not in url.lower():
        url = "%s/%s" % (req.app_uri, url.strip('/'))
    resp.status = 303
    resp.set_header('Location', url)


def http_not_modified():
    """ 304 Not Modified.
    """
    resp = g.current_request.response
    resp.status = 304


def http_temporary_redirect(url):
    """ 307 Temporary Redirect.

    The target resource resides temporarily under a different URI and the
    user agent MUST NOT change the request method if it performs an automatic
    redirection to that URI.

    Since the redirection can change over time, the client ought to continue
    using the original effective request URI for future requests.

    The server SHOULD generate a Location header field in the response
    containing a URI reference for the different URI. The user agent MAY use
    the Location field value for automatic redirection. The server's response
    payload usually contains a short hypertext note with a hyperlink to the
    different URI(s).

    Note: This status code is similar to 302 Found, except that it does not
    allow changing the request method from POST to GET. This specification
    defines no equivalent counterpart for 301 Moved Permanently (RFC7238,
    however proposes defining the status code 308 Permanent Redirect for
    this purpose).

    Args:
        url (str): Redirected to URL.
    """
    req = g.current_request
    resp = g.current_request.response

    if 'http' not in url.lower():
        url = "%s/%s" % (req.app_uri, url.strip('/'))
    resp.status = 307
    resp.set_header('Location', url)


def http_permanent_redirect(url):
    """ 308 Permanent Redirect.

    The target resource has been assigned a new permanent URI and any future
    references to this resource ought to use one of the enclosed URIs.

    Clients with link editing capabilities ought to automatically re-link
    references to the effective request URI1 to one or more of the new
    references sent by the server, where possible.

    The server SHOULD generate a Location header field in the response
    containing a preferred URI reference for the new permanent URI. The
    user agent MAY use the Location field value for automatic redirection.
    The server's response payload usually contains a short hypertext note
    with a hyperlink to the new URI(s).

    A 308 response is cacheable by default; i.e., unless otherwise indicated
    by the method definition or explicit cache controls.

    Note: This status code is similar to 301 Moved Permanently, except that
    it does not allow changing the request method from POST to GET.

    Args:
        url (str): Redirected to URL.
    """
    req = g.current_request
    resp = g.current_request.response

    if 'http' not in url.lower():
        url = "%s/%s" % (req.app_uri, url.strip('/'))
    resp.status = 308
    resp.set_header('Location', url)
