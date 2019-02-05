# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019, Christiaan Frans Rademan.
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
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTI-
# TUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUP-
# TION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY,OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import re
from decimal import Decimal
from datetime import datetime

pyformat_re = r"%\([\w]+\)\w"
numeric_re = r":\d+"
named_re = r":[a-z]*\w+"
format_re = r"\%[-\d.]*[sdf]+"
qmark_re = r"\?+"
match_re = pyformat_re + r'|' + \
    named_re + r'|' + \
    numeric_re + r'|' + \
    format_re + r'|' + qmark_re
interpolation_format_match = re.compile(match_re, re.IGNORECASE)
named_re_match = re.compile(named_re, re.IGNORECASE)
numeric_re_match = re.compile(numeric_re, re.IGNORECASE)
pyformat_re_match = re.compile(pyformat_re, re.IGNORECASE)


def _parse_param(value, cast_map):
    """Parse SQL paramters provided to query.
    """
    if isinstance(value, bool):
        if value is True:
            return 1
        else:
            return 0
    elif hasattr(value, '__call__'):
        value = value()
        if isinstance(value, (Decimal, int, float, str, bytes, datetime)):
            return value
        else:
            return str(value)

    for cast in cast_map:
        if isinstance(value, cast[0]):
            return cast[1](value)

    return value


def args_to(query, args, to='qmark', cast=None):
    if isinstance(args, tuple):
        args = list(args)
    if not isinstance(args, (list, dict)):
        if args is None:
            return (query, args)
        args = [args, ]
    else:
        args = args.copy()

    if to == "qmark" or to == "numeric" or to == "format":
        new_args = []
    else:
        new_args = {}

    counter = 0
    expressions = interpolation_format_match.findall(query)
    for expr in expressions:
        if pyformat_re_match.match(expr):
            if not isinstance(args, dict):
                raise TypeError('Can only match pyformat using dict args')
            column = expr[2:][:-2]
        elif named_re_match.match(expr):
            if not isinstance(args, dict):
                raise TypeError('Can only match named using dict args')
            column = expr[1:]
        else:
            column = expr
        try:
            if to == "qmark":
                query = query.replace(expr, '?', 1)
                if isinstance(args, dict):
                    new_args.append(_parse_param(args[column], cast))
                else:
                    new_args.append(_parse_param(args.pop(0), cast))
            elif to == "numeric":
                query = query.replace(expr, ':%s' % counter, 1)
                if isinstance(args, dict):
                    new_args.append(_parse_param(args[column], cast))
                else:
                    new_args.append(_parse_param(args.pop(0), cast))
                counter += 1
            elif to == "named":
                query = query.replace(expr, ':%s' % column, 1)
                if isinstance(args, dict):
                    new_args.append(_parse_param(args[column], cast))
                else:
                    new_args.append(_parse_param(args.pop(0), cast))
            elif to == "format":
                query = query.replace(expr, '%s', 1)
                if isinstance(args, dict):
                    new_args.append(_parse_param(args[column], cast))
                else:
                    new_args.append(_parse_param(args.pop(0), cast))
            elif to == "pyformat":
                query = query.replace(expr, '%' + '(%s)s' % column, 1)
                if isinstance(args, dict):
                    new_args.append(_parse_param(args[column], cast))
                else:
                    new_args.append(_parse_param(args.pop(0), cast))
            else:
                raise ValueError("Unknown type '%s'" % type) from None
        except KeyError:
            raise KeyError("DB Query: Field '%s' value not in" % column +
                           " dictionary provided") from None
        except IndexError:
            raise IndexError("DB Query: Not all field" +
                             " values provided") from None

    return (query, new_args)
