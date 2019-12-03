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
import os
import datetime
from textwrap import indent, wrap


def format_seconds(secs):
    """Format Seconds to string.

    Args:
        ms (float): Milliseconds.

    Returns:
        Time as human friendly string
    """
    # Minutes
    if secs >= 60:
        secs = str(datetime.timedelta(seconds=round(secs)))
        hours, days, seconds = secs.split(':')
        return '%sh %sm %ss' % (hours, days, seconds)
    # Seconds
    if secs >= 1:
        return '%.3fs' % secs

    # Milliseconds
    secs = secs * 1000
    return '%.3fms' % secs


def format_obj(obj, dent=0):
    """Formats an object

    Takes a list or a dict
    """
    rows, columns = os.popen('stty size', 'r').read().split()
    string = ""
    if isinstance(obj, list):
        dent = dent + 4
        for item in obj:
            string += indent(format_obj(item, dent), ' '*dent)
            string += '\n\n'
    elif isinstance(obj, dict):
        for key in obj:
            string += "%s: %s " % (key, obj[key],)
        return '\n'.join(wrap(string, int(columns)-dent, drop_whitespace=False,
                              subsequent_indent='|'))
    return string
