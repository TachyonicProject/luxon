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

import json
import datetime
from decimal import Decimal

from luxon.exceptions import JSONDecodeError
from luxon.utils.timezone import to_user
from luxon.utils.html5 import strip_tags
from luxon.core.regex import DATETIME_RE


class _JsonEncoder(json.JSONEncoder):
    """Custom encoder.

    Overwrites default json.JSONEncoder to support luxon functionality.
    """

    def default(self, o):
        """
        parses data into usable form or encodes it using
        JSONEncoder.default if it is valid.

        Args:
            o(obj): data to be parsed/encoded

        Returns:
            formatted data object
        """
        if isinstance(o, Decimal):
            # Parse Decimal Value
            return str(o)
        elif isinstance(o, datetime.datetime):
            # Parse Datetime
            return str(to_user(o).strftime("%Y-%m-%dT%H:%M:%S%z"))
        elif isinstance(o, bytes):
            return strip_tags(o.decode('utf-8'))
        elif hasattr(o, 'dict'):
            return o.dict
        else:
            # Pass to Default Encoder
            return json.JSONEncoder.default(self, o)


def parse_load(parse):
    if isinstance(parse, list):
        for i, obj in enumerate(parse):
            parse[i] = parse_load(obj)
        return parse
    elif isinstance(parse, dict):
        for obj in parse:
            parse[obj] = parse_load(parse[obj])
        return parse
    else:
        if isinstance(parse, str):
            if DATETIME_RE.match(parse):
                try:
                    parse = to_user(parse)
                except ValueError as e:
                    raise JSONDecodeError(str(e))
            else:
                parse = strip_tags(parse)
        return parse


def loads(json_text, **kwargs):
    """Deserializes a json document to a python object.

    Args:
        json_text (str/bytes): document to be deserialized.

    Returns:
        python object.

    """
    if isinstance(json_text, bytes):
        # JSON requires str not bytes hence decode.
        json_text = json_text.decode('UTF-8')
    try:
        obj = json.loads(json_text, object_hook=parse_load, **kwargs)
        return obj

    except json.decoder.JSONDecodeError as e:
        raise JSONDecodeError(e) from None


def dumps(obj, indent=4):
    """Serializes an object as a JSON formatted stream.

    Args:
        obj(obj): object to be serialized.

    Returns:
        JSON formatted stream.
    """
    return json.dumps(obj, indent=indent, cls=_JsonEncoder)
