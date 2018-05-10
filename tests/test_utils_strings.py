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
from luxon.utils.strings import *

def test_blank_to_none():
    str = "abcd"
    empstr = ""
    empbyt =b""

    assert blank_to_none(str) == "abcd"
    assert blank_to_none(empstr) == None
    assert blank_to_none(empbyt) == None

def test_try_lower():
    numstr = "123456"
    charstr = "Secrecy BegeTs TyranNy"

    assert try_lower(numstr) == "123456"
    assert try_lower(charstr) == "secrecy begets tyranny"

def test_indent():
    str = "There is no safety this side of the grave"
    longstr = "Its very variety,\n" \
              "subtlety,\n" \
              "and utterly irrational,\n" \
              "idiomatic complexity\n" \
              "makes it possible to say things in English\n" \
              "which simply cannot be said in any other language"

    ind_str = indent(str, "&&&&&")
    assert ind_str == "&&&&&There is no safety this side of the grave"

    ind_longstr = indent(longstr,"&&&&&")
    assert ind_longstr == "Its very variety,\n" \
                          "&&&&&subtlety,\n" \
                          "&&&&&and utterly irrational,\n" \
                          "&&&&&idiomatic complexity\n" \
                          "&&&&&makes it possible to say things in English\n" \
                          "&&&&&which simply cannot be said in any other language"

def test_unquote_string():
    shortstr =r'"AB"'
    unqtdstr = "He's an honest politician--he stays bought"
    assert unquote_string(shortstr) == "AB"
    assert unquote_string(unqtdstr) == "He's an honest politician--he stays bought"
    qtdstr = "\"I grok in fullness\""
    assert unquote_string(qtdstr) == "I grok in fullness"
    escpstr = r'"I grok in\\fullness"'
    assert unquote_string(escpstr) == r"I grok in\fullness"

