# -*- coding: utf-8 -*-
# Copyright (c) 2018 Hieronymus Crouse.
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

import datetime
from luxon import g
from luxon.core.config import *
from luxon.utils.timezone import *

def test_parse_http_date():

    z = "Wed, 23 Sep 2009 22:15:29 GMT"
    z2 = "Wednesday, 23-Sep-09 22:15:29 GMT"
    x = parse_http_date(z)
    u = parse_http_date(z2, True)
    y = datetime.datetime(2009,9,23,22,15,29)

    assert u == x == y

    print(type(x))
    print(type(y))

test_parse_http_date()

def test_TimezoneGMT():
    z = "Wed, 23 Sep 2009 22:15:29 GMT"
    pls = TimezoneGMT()

    #utcoffset
    o = pls.utcoffset(z)
    r = datetime.timedelta(0)
    assert o==r

    #tzname
    name = pls.tzname(z)
    assert name == "GMT"

    #dst
    sav = pls.dst(z)
    assert sav == datetime.timedelta(0)


def test_TimezoneSystem():
    x = TimezoneSystem()
    y = get_localzone()
    assert x == y

def test_parse_datetime():

    try:
        x = parse_datetime("2009,9,23,22,15,29")
        assert False
    except ValueError:
        assert True

    pls = py_datetime(2009,9,23,22,15,29)
    z = "2009-09-23 22:15:29"

    assert parse_datetime(pls) == datetime.datetime(2009,9,23,22,15,29)

    y = parse_datetime(z)
    assert y == datetime.datetime(2009,9,23,22,15,29)



def test_now():

    x = now()
    y = py_datetime.now(TimezoneUTC())
    z = type(y)
    assert x is not None and type(x) == z



# TimezoneApp() and format_datetime() mess with g.app.config, will take a look later
