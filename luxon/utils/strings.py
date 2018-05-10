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

def blank_to_none(value):
    """Converts an empty string or byte object to None

    If value is an empty string or an empty byte array None is returned
    else value is returned

    Args:
        value(str/bytes): object to be converted

    """
    if ((isinstance(value, str) and value == '') or
            (isinstance(value, bytes) and
             value == b'')):
        return None
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
    if not isinstance(text, str):
        raise ValueError("indent expecting text type 'str' not '%s'" % type(text))
    if not isinstance(indent, str):
        raise ValueError("indent expecting indent type 'str' not '%s'" % type(indent))

    if '\n' not in text:
        return "%s%s" % (indent, text)
    else:
        text = text.splitlines(True)
        return indent.join(text)
    #(Rony): does not indent the first line of a multiline block, peep the unit test

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
