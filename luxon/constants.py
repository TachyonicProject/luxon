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

# ALL CONSTANTS DEFINED BELOW

TEXT_HTML = 'text/html; charset=utf-8'
TEXT_PLAIN = 'text/plain; charset=utf-8'
TEXT_CSS = 'text/css; charset=utf-8'
IMAGE_JPEG = 'image/jpeg'
IMAGE_GIF = 'image/gif'
IMAGE_PNG = 'image/png'
APPLICATION_XML = 'application/xml; charset=utf-8'
APPLICATION_JSON = 'application/json; charset=utf-8'
APPLICATION_OCTET_STREAM = 'application/octet-stream'
APPLICATION_FORM_DATA = 'application/x-www-form-urlencoded'
APPLICATION_PDF = 'application/pdf'

HTTP_GET = 'GET'
HTTP_POST = 'POST'
HTTP_PUT = 'PUT'
HTTP_DELETE = 'DELETE'
HTTP_PATCH = 'PATCH'
HTTP_OPTIONS = 'OPTIONS'
HTTP_HEAD = 'HEAD'
HTTP_TRACE = 'TRACE'
HTTP_CONNECT = 'CONNECT'

HTTP_100 = '100 Continue'
HTTP_101 = '101 Switching Protocols'
HTTP_200 = '200 OK'
HTTP_201 = '201 Created'
HTTP_202 = '202 Accepted'
HTTP_203 = '203 Non-Authoritative Information'
HTTP_204 = '204 No Content'
HTTP_205 = '205 Reset Content'
HTTP_206 = '206 Partial Content'
HTTP_226 = '226 IM Used'
HTTP_300 = '300 Multiple Choices'
HTTP_301 = '301 Moved Permanently'
HTTP_302 = '302 Found'
HTTP_303 = '303 See Other'
HTTP_304 = '304 Not Modified'
HTTP_305 = '305 Use Proxy'
HTTP_306 = '306 Switch Proxy'
HTTP_307 = '307 Temporary Redirect'
HTTP_308 = '308 Permanent Redirect'
HTTP_400 = '400 Bad Request'
HTTP_401 = '401 Unauthorized'  # <-- Really means "unauthenticated"
HTTP_402 = '402 Payment Required'
HTTP_403 = '403 Forbidden'  # <-- Really means "unauthorized"
HTTP_404 = '404 Not Found'
HTTP_405 = '405 Method Not Allowed'
HTTP_406 = '406 Not Acceptable'
HTTP_407 = '407 Proxy Authentication Required'
HTTP_408 = '408 Request Time-out'
HTTP_409 = '409 Conflict'
HTTP_410 = '410 Gone'
HTTP_411 = '411 Length Required'
HTTP_412 = '412 Precondition Failed'
HTTP_413 = '413 Payload Too Large'
HTTP_414 = '414 URI Too Long'
HTTP_415 = '415 Unsupported Media Type'
HTTP_416 = '416 Range Not Satisfiable'
HTTP_417 = '417 Expectation Failed'
HTTP_418 = "418 I'm a teapot"
HTTP_422 = "422 Unprocessable Entity"
HTTP_426 = '426 Upgrade Required'
HTTP_428 = '428 Precondition Required'
HTTP_429 = '429 Too Many Requests'
HTTP_431 = '431 Request Header Fields Too Large'
HTTP_451 = '451 Unavailable For Legal Reasons'
HTTP_500 = '500 Internal Server Error'
HTTP_501 = '501 Not Implemented'
HTTP_502 = '502 Bad Gateway'
HTTP_503 = '503 Service Unavailable'
HTTP_504 = '504 Gateway Time-out'
HTTP_505 = '505 HTTP Version not supported'
HTTP_511 = '511 Network Authentication Required'

HTTP_STATUS_CODES = {100: 'Continue',
                     101: 'Switching Protocols',
                     200: 'OK',
                     201: 'Created',
                     202: 'Accepted',
                     203: 'Non-Authoritative Information',
                     204: 'No Content',
                     205: 'Reset Content',
                     206: 'Partial Content',
                     226: 'IM Used',
                     300: 'Multiple Choices',
                     301: 'Moved Permanently',
                     302: 'Found',
                     303: 'See Other',
                     304: 'Not Modified',
                     305: 'Use Proxy',
                     306: 'Switch Proxy',
                     307: 'Temporary Redirect',
                     308: 'Permanent Redirect',
                     400: 'Bad Request',
                     401: 'Unauthorized',
                     402: 'Payment Required',
                     403: 'Forbidden',
                     404: 'Not Found',
                     405: 'Method Not Allowed',
                     406: 'Not Acceptable',
                     407: 'Proxy Authentication Required',
                     408: 'Request Time-out',
                     409: 'Conflict',
                     410: 'Gone',
                     411: 'Length Required',
                     412: 'Precondition Failed',
                     413: 'Payload Too Large',
                     414: 'URI Too Long',
                     415: 'Unsupported Media Type',
                     416: 'Range Not Satisfiable',
                     417: 'Expectation Failed',
                     418: "I'm a teapot",
                     422: 'Unprocessable Entity',
                     426: 'Upgrade Required',
                     428: 'Precondition Required',
                     429: 'Too Many Requests',
                     431: 'Request Header Fields Too Large',
                     451: 'Unavailable For Legal Reasons',
                     500: 'Internal Server Error',
                     501: 'Not Implemented',
                     502: 'Bad Gateway',
                     503: 'Service Unavailable',
                     504: 'Gateway Time-out',
                     505: 'HTTP Version not supported',
                     511: 'Network Authentication Required'}

BLOWFISH = 1
MD5 = 2
SHA256 = 3
SHA512 = 4
CLEARTEXT = 5
LDAP_BLOWFISH = 6
LDAP_MD5 = 7
LDAP_SMD5 = 8
LDAP_SHA1 = 9
LDAP_SSHA1 = 10
LDAP_SHA256 = 11
LDAP_SHA512 = 12
LDAP_CLEARTEXT = 13

LEFT = 1
RIGHT = 2
