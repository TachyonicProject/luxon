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
from luxon.utils.encoding import is_text


def split(string, by):
    pos = string.find(by)
    if pos > 0:
        return (string[0:pos], string[pos+1:],)
    else:
        return string


def join(obj, seperator=" "):
    parsed = [str(val) for val in obj]
    return seperator.join(parsed)


def filter_none_text(string):
    """Parse String and filter Binary

    If Bytes does not contain string then return 'BINARY'
    else original string will be returned.

    Args:
        string (bytes): Bytes String

    Returns:
        "BINARY" if the argument contained binary

    """
    if string is not None:
        if is_text(string):
            return string
        else:
            return "BINARY"
    else:
        return ''


def blank_to_none(value, default=None):
    """Converts an empty string or byte object to None

    If value is an empty string or an empty byte array None is returned
    else value is returned

    Args:
        value(str/bytes): object to be converted

    """
    if isinstance(value, str) and value == '':
        return default

    return value


def try_lower(string):
    # Ask for, forgiveness seems faster, perhaps better :-)
    """Converts string to lower case

    Args:
        string(str): ascii string

    Returns:
        converted string
    """
    try:
        return string.lower()
    except Exception:
        return string


def indent(text, indent):
    """Indent Text.

    Args:
        text(str): body of text
        indent(str): characters with which to indent
    Returns:
        text indeneted with given characters
    """
    if '\n' not in text:
        return "%s%s" % (indent, text)
    else:
        text = text.splitlines(True)
        return indent.join(text)


def unquote_string(quoted):
    """Unquote an "quoted-string".

    Args:
        quoted (str): Original quoted string

    Returns:
        Unquoted string
    """

    if len(quoted) < 2:
        return quoted
    elif quoted[0] != '"' or quoted[-1] != '"':
        return quoted

    tmp_quoted = quoted[1:-1]

    if '\\' not in tmp_quoted:
        return tmp_quoted
    elif r'\\' not in tmp_quoted:
        return tmp_quoted.replace('\\', '')
    else:
        return '\\'.join([q.replace('\\', '')
                          for q in tmp_quoted.split(r'\\')])
