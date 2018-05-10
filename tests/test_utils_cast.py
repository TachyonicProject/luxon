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

import pytest
from luxon.utils.cast import *

def test_to_tuple():

    # string
    a = "Beware the jabberwock"
    # tuple
    b = ("blah", 5)
    #int
    c = 42
    #list
    d = ["1","2",3]
    #none
    e = None

    cast_a = to_tuple(a)
    assert cast_a == ("Beware the jabberwock", )

    cast_b = to_tuple(b)
    assert cast_b == ("blah",5)

    cast_c = to_tuple(c)
    assert cast_c == (42,)

    cast_d = to_tuple(d)
    assert cast_d == ("1","2",3)

    cast_e = to_tuple(e)
    assert cast_e == ()

def test_to_list():

    # string
    a = "Beware the jabberwock"
    # tuple
    b = ("blah", 5)
    #int
    c = 42
    #list
    d = ["1","2",3]
    #none
    e = None

    cast_a = to_list(a)
    assert cast_a == ["Beware the jabberwock"]

    cast_b = to_list(b)
    assert cast_b == ["blah",5]

    cast_c = to_list(c)
    assert cast_c == [42]

    cast_d = to_list(d)
    assert cast_d == ["1","2",3]

    cast_e = to_list(e)
    assert cast_e == []
