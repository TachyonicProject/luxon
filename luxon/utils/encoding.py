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


def if_unicode_to_bytes(string, codec='UTF-8'):
    """Encode if Unicode to Bytes UTF8.

    Args:
        string (bytes): Bytes String
        codec (str): codec type
    Returns:
        UTF8 encoded string
    """
    try:
        return string.encode(codec)
    except Exception:
        return string


def if_bytes_to_unicode(string, codec='UTF-8'):
    """Decode UTF-8 Bytes to string UTF8.

    Args:
        string (bytes): Bytes String
        codec (str): Codec type
    Returns:
        Unicode string
    """
    try:
        return string.decode(codec)
    except AttributeError:
        return string
    except UnicodeDecodeError:
        return "<non-'%s' encoded data omitted>" % codec


def is_text(text):
    """Is Text?

    Args:
        text (str/bytes): Socket path.
    Returns:
        True if text.
    """
    if isinstance(text, str):
        return True
    elif isinstance(text, bytes):
        if is_binary(text):
            return False
        return True
    return False


def is_binary(data):
    """Is Binary?

    Args:
        data (str/bytes): Possible binary or string.
    Returns:
        True if binary.
    """
    if isinstance(data, str):
        return False
    elif isinstance(data, bytes):
        try:
            # if s contains any null, it's not text:
            if b"\0" in data:
                return True
            # Decode UTF-8 - will fail on binary.
            data.decode('UTF-8')
            return False
        except UnicodeDecodeError:
            # UnicodeDecodError means binary...
            return True
        return True
    else:
        return False


def is_ascii(string):
    """Check if argument encodes to ascii without error.

    Args:
        string (str): string of bytes

    Returns:
        True if string can successfully be encoded
    """
    try:
        string.encode('ascii')
    except UnicodeEncodeError:
        return False
    except UnicodeDecodeError:
        return False
    except AttributeError:
        return False
    return True


def is_utf8(string):
    """Check if argument encodes to UTF8 without error.

    Args:
        string(str): string of bytes

    Returns:
        True if string can be successfully encoded
    """
    try:
        string.encode('utf-8')
    except UnicodeEncodeError:
        return False
    except UnicodeDecodeError:
        return False
    except AttributeError:
        return False
    return True
