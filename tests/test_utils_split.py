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
from luxon.utils.split import *

def test_split_by_n():

    seq_str = "Nothing uses up alcohol faster than political argument."
    seq_list = ["1","2","3","4","5","6","7","8","9","0"]

    split_str = split_by_n(seq_str,3)
    assert next(split_str) == "Not"
    assert next(split_str) == "hin"
    assert next(split_str) == "g u"

    split_lst = split_by_n(seq_list,3)
    assert next(split_lst) == ["1","2","3"]
    assert next(split_lst) == ["4","5","6"]

def test_list_of_lines():

    pls = "Nor would anybody suspect.\n" \
          "If was one thing all people took for granted,\n" \
          "was conviction that if you feed honest figures into a computer,\n" \
          "honest figures come out. Never doubted it myself\n" \
          "till I met a computer with a sense of humor."

    pls_lst = list_of_lines(pls)
    assert pls_lst == ["Nor would anybody suspect.",
                       "If was one thing all people took for granted,",
                       "was conviction that if you feed honest figures into a computer,",
                       "honest figures come out. Never doubted it myself",
                       "till I met a computer with a sense of humor."]

    # with bytes
    bpls = b"Drop\ndead-but\nfirst\nget\npermit"
    bpls_lst = list_of_lines(bpls)
    assert bpls_lst == ["Drop","dead-but","first","get","permit"]
