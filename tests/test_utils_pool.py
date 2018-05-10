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
from luxon.utils.pool import *


def test_pool():
    #trashy stub to simulate connection objects
    class Connect():
        def __init__(self,x,y,z):
            self.host = x
            self.username = y
            self.password = z

    def con_func():
        return Connect("host","username","password")



    #create pool
    pool = Pool(con_func, pool_size = 3, max_overflow = 2)
    assert pool._count == 0

    #fetch/create conn objects

    conn = pool()
    assert pool._count == 1
    assert conn.host == "host"

    conn = pool()
    assert pool._count == 2

    conn = pool()
    assert pool._count == 3

    #overflow starts
    conn = pool()
    assert pool._count == 4

    conn = pool()
    assert pool._count == 5

    #max size reached
    try:
        conn = pool()
        assert False
    except:
        assert True

    #close/return connection objects

    conn.close()
    assert pool._count == 4

    conn.close()
    assert pool._count == 3

    #overflow empty
    conn.close()
    assert pool._count == 3

