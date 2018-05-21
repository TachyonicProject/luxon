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


def build_where(**kwargs):
    """Generates an SQL WHERE string.

    Will replace None's with IS NULL's.

    Keyword Args:
       Containing SQL search string
       Eg: {"foo": 1, "bar": None}

    Returns:
        Tuple containing string that can
        be used after WHERE in SQL statement,
        along with a list of the values.
        Eg. ("foo=? AND bar IS NULL", [ 1 ])

    """
    vals = []
    query = []
    for k in kwargs:
        if kwargs[k] is None:
            query.append(k + " IS NULL")
        else:
            query.append(k + " = ?")
            vals.append(kwargs[k])

    return (" AND ".join(query), vals)


def build_like(**kwargs):
    """Generates an SQL WHERE string.

    Will replace None's with IS NULL's.

    Keyword Args:
       Containing SQL search string
       Eg: {"foo": 1, "bar": None}

    Returns:
        Tuple containing string that can
        be used after WHERE in SQL statement,
        along with a list of the values.
        Eg. ("foo=? AND bar IS NULL", [ 1 ])

    """
    vals = []
    query = []
    for k in kwargs:
        if kwargs[k] is None:
            query.append(k + " IS NULL")
        else:
            query.append(k + " LIKE ?")
            vals.append(kwargs[k] + '%')

    return (" AND ".join(query), vals)
