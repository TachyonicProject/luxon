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

from urllib import parse
import re

from luxon.utils.strings import blank_to_none

_HEX_DIGITS = '0123456789ABCDEFabcdef'
_HEX_TO_BYTE = dict(((a + b).encode(), bytes([int(a + b, 16)]))
                    for a in _HEX_DIGITS
                    for b in _HEX_DIGITS)


def decode(encoded_uri):
    """Decodes percent-encoded characters in a URI or query string.

    Args:
        encoded_uri (str): An encoded URI (full or partial).

    Returns:
        A decoded URL. If the URL contains escaped non-ASCII
        characters, UTF-8 is assumed per RFC 3986.
    """
    decoded_uri = encoded_uri

    # Add spaces.
    if '+' in decoded_uri:
        decoded_uri = decoded_uri.replace('+', ' ')

    # If not encoding return..
    if '%' not in decoded_uri:
        return decoded_uri

    # by encoding to UTF-8 we encode non-ASCII to characters.
    decoded_uri = decoded_uri.encode('utf-8')

    tokens = decoded_uri.split(b'%')
    decoded_uri = tokens[0]
    for token in tokens[1:]:
        token_partial = token[:2]
        try:
            decoded_uri += _HEX_TO_BYTE[token_partial] + token[2:]
        except KeyError:
            decoded_uri += b'%' + token

    # return str
    return decoded_uri.decode('utf-8', 'replace')


def clean_uri(uri):
    """Clean URL.

    Replaces two or more / with one in path.

    A generic URI is of the form:
        scheme://user:password@host:port/path]?query#fragment

    Args:
        uri (string): URL to parse.

    Returns:
    Formatted uri str.
    """
    parsed = list(parse.urlparse(uri))
    parsed[2] = re.sub("/{2,}", "/", parsed[2]).strip('/')  # replace two or more / with one

    cleaned = parse.urlunparse(parsed)

    return cleaned


def host_from_uri(uri):
    """Return only scheme + host + port from uri.

    A generic URI is of the form:
        scheme://user:password@host:port/path]?query#fragment

    Args:
        uri (str): Standard URL as per RFC3986.

    Returns
        Value for scheme + host + port as str.
    """
    uri = parse.urlparse(uri)

    return "%s://%s" % (uri.scheme, uri.netloc)


def parse_host(host, default_port=None):
    """Parse a canonical 'host:port' string into parts.

    Parse a host string (which may or may not contain a port) into
    parts, taking into account that the string may contain
    either a domain name or an IP address. In the latter case,
    both IPv4 and IPv6 addresses are supported.

    Args:
        host (str): Host string to parse, optionally containing a
            port number.
        default_port (int): Port number to return when the host string
            does not contain one (default 'None').

    Returns:
        tuple: A parsed (*host*, *port*) tuple from the given
        host string, with the port converted to an ``int``.
        If the host string does not specify a port, `default_port` is
        used instead.

    """
    if host.startswith('['):
        # IPv6 address with a port
        pos = host.rfind(']:')
        if pos != -1:
            return (host[1:pos], int(host[pos + 2:]))
        else:
            return (host[1:-1], default_port)

    pos = host.rfind(':')
    if (pos == -1) or (pos != host.find(':')):
        # Bare domain name or IP address
        return (host, default_port)

    # There is only a single colon, so we should have an IPv4 address
    # or a domain name plus a port
    name, _, port = host.partition(':')
    return (name, int(port))


def parse_qs(query_string, keep_blanks=False):
    params = {}

    is_encoded = '+' in query_string or '%' in query_string

    for field in query_string.split('&'):
        k, _, v = field.partition('=')
        if not (v or keep_blanks):
            continue

        if is_encoded:
            k = decode(k)
            v = decode(v)

        if k in params:
            old_value = params[k]

            if isinstance(old_value, list):
                old_value.append(blank_to_none(v))
            else:
                params[k] = [old_value, blank_to_none(v)]
        else:
            if is_encoded:
                params[k] = blank_to_none(decode(v))
            else:
                params[k] = blank_to_none(v)

    return params


def build_qs(params, uri=None):
    qs = []
    if isinstance(params, dict):
        params = params.items()
    for param in params:
        try:
            qs.append('%s=%s' % param)
        except TypeError:
            qs.append('%s' % param)

    if uri is None:
        uri = ''

    if len(qs) > 0:
        uri += '?' + '&'.join(qs)

    return uri

def uri(location, proto='http', path=None, params=None):
    uri = proto + '://' + location.strip(' ').strip('/')
    if path is not None:
        path = path.strip('/').strip()
        uri += '/%s' % path

    if params is not None:
        uri += '?' + build_qs(params)

    return uri
