# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020 Christiaan Frans Rademan <chris@fwiw.co.za>.
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

###########################################
# EXPRESSIONS USED IN REGULAR EXPRESSIONS #
###########################################
# MATCH FULLY QUALIFIED DOMAIN
FQDN_EXPR = r'([0-9a-z]+\.?)+'

# MATCH IPV4 ONLY ADDRESS
IP4_BITS_EXPR = r'(([1-2]?[0-9]{1})|(3[0-2]{1}))'
IP4_VALUE_EXPR = r'(([0-9]{1,2})|([0-1]{1}[0-9]{2})|(2[0-5]{2}))'
IP4_EXPR = (IP4_VALUE_EXPR + r'{1}\.' +
            IP4_VALUE_EXPR + r'{1}\.' +
            IP4_VALUE_EXPR + r'{1}\.' +
            IP4_VALUE_EXPR)

IP4PREFIX_EXPR = (IP4_VALUE_EXPR + r'{1}' +
                  r'(\.' + IP4_VALUE_EXPR + r')?' +
                  r'(\.' + IP4_VALUE_EXPR + r')?' +
                  r'(\.' + IP4_VALUE_EXPR + r')?')

# MATCH IPV6 ONLY ADDRESS
IP6_BITS_EXPR = r'(([0-9]{1,2})|(1[0-2]{1}[0-8]{1}))'
IP6_EXPR = (r'(([0-9a-f]{1,4}:){1,6}' +
            r'((:[0-9a-f]{1,4}){1}|' +
            r'[0-9a-f]{1,4}:[0-9a-f]{1,4}))')

IP6_PREFIX_EXPR = (r'((([0-9a-f]{1,4}:){1,6})' +
                   r'((:([0-9a-f]{0,4}))|' +
                   r'[0-9a-f]{1,4}:[0-9a-f]{1,4}))')


#######################
# REGULAR EXPRESSIONS #
#######################

# MATCH WORD STARTING WITH ALPHA CHARACTERS AND HAS INTEGERS
WORD_RE = re.compile(r'^[a-z]+[a-z0-9]+$', re.IGNORECASE)

# MATCH USERNAME or USERNAME@DOMAIN.CO.ZA
USERNAME_RE = re.compile(r'^([a-z0-9\.\-_]+@[a-z0-9\.\-_]+' +
                         r'|^[a-z0-9\._]+)$', re.IGNORECASE)

# MATCH PASSWORD WITH NO SPACES ANY CHARACTERS
PASSWORD_RE = re.compile(r'^[^\s]+$', re.IGNORECASE)

# MATCH EMAIL ADDRESS
EMAIL_RE = re.compile(r'^[a-z0-9\.\-_]+@[a-z0-9\.\-_]+$',
                      re.IGNORECASE)

# MATCH URI
URI_RE = re.compile(r'^(?:http|ftp)s?://'
                    r'(' +
                    FQDN_EXPR +
                    r'|' +
                    IP6_EXPR +
                    r')' +
                    r'(?::\d+)?' +  # optional port
                    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

# MATCH FULLY QUALIFIED DOMAIN
FQDN_RE = re.compile(r'^' + FQDN_EXPR + r'$', re.IGNORECASE)

# MATCH IPV4 ADDRESS
IP4_RE = re.compile(r'^' + IP4_EXPR + r'$')
# MATCH IPV4 PREFIX
IP4_PREFIX_RE = re.compile(r'^' + IP4PREFIX_EXPR + r'/' + IP4_BITS_EXPR + r'$')
# MATCH IPV4 SUBNETMASK
SUBNETMASK_RE = IP4_RE
# MATCH IPV4 WILDCARD
WILDCARD_RE = IP4_RE

# MATCH IPV6 ADDRESS
IP6_RE = re.compile(r'^' + IP6_EXPR + r'$', re.IGNORECASE)
# MATCH IPV6 PREFIX
IP6_PREFIX_RE = re.compile(r'^' + IP6_PREFIX_EXPR +
                           r'/' + IP6_BITS_EXPR + r'$', re.IGNORECASE)

# MATCH DATETIME (detection for Datetime values)
DATETIME_RE = re.compile(r'^[0-9]{4}[-/][0-9]{2}[-/][0-9]{2}[ T]'
                         r'[0-9]{2}:[0-9]{2}:[0-9]{2}' +
                         r'([+-][0-9]{2}:?[0-9]{2})?$')

# MATCH ISO DATETIME
ISODATETIME_RE = re.compile(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}T'
                            r'[0-9]{2}:[0-9]{2}:[0-9]{2}' +
                            r'([+-][0-9]{2}:[0-9]{2})?$')

# MATCH SQL FIELD
SQLFIELD_RE = re.compile(r'^[a-z0-9_\.]+$', re.IGNORECASE)
