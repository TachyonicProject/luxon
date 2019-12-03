# -*- coding: utf-8 -*-
# Copyright (c) 2019-2020 Christiaan Frans Rademan <chris@fwiw.co.za>.
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
from datetime import datetime

from luxon.utils.cast import to_list
from luxon.utils.text import split
from luxon.utils.timezone import TimezoneUser, to_utc

DATE_SEPARATORS = (' ', '/', '-')

def search_params(req):
    searches = to_list(req.query_params.get('search'))
    for search in searches:
        try:
            search_field, value = split(search, ':')
        except (TypeError, ValueError):
            raise ValueError("Invalid field search field value." +
                             " Expecting 'field:value'")

        yield (search_field, value,)


def search_datetime(val):
    partial = False

    # NOTE(Vuader): We allow for for 4 digits of year, but if the
    # next character is not a date separator, we are assuming this
    # is not a date. Otherwise this has undesirable effects, for example
    # a search on one field for 12345@ wil return all results where
    # datetime field is greater than 1983
    if len(val) > 4 and val[4] not in DATE_SEPARATORS:
        return (None, False,)
    elif len(val) < 4:
        return (None, False,)

    try:
        year = int(val[0:4])
        if year < 1983:
            year = 1983
        elif year > 5000:
            return (None, False,)
    except ValueError:
        return (None, False,)

    try:
        month = int(val[5:7])
        if month < 1:
            month = 1
    except ValueError:
        month = 1
        partial = True

    try:
        day = int(val[8:10])
        if day < 1:
            day = 1
    except ValueError:
        day = 1
        partial = True

    try:
        hour = int(val[11:13])
    except ValueError:
        hour = 0
        partial = True

    try:
        minute = int(val[14:16])
    except ValueError:
        minute = 0
        partial = True

    try:
        second = int(val[17:19])
    except ValueError:
        second = 0
        partial = True

    return (
        to_utc(
            datetime(year=year, month=month, day=day,
                     hour=hour, minute=minute, second=second),
            src=TimezoneUser()
        ),
        partial,)
