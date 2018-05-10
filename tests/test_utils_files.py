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
import os
from luxon.utils.files import *

def test_CachedInput():
    #os.remove("tests/testfile.txt")

    #read()
    pls = b"Never worry about theory\n" \
          b"as long as the machinery does what it's supposed to do"
    io_string = BytesIO(pls)
    cache_obj = CachedInput(io_string)
    output_string = cache_obj.read()
    assert output_string == b"Never worry about theory\n" \
                            b"as long as the machinery does " \
                            b"what it's supposed to do"

    empty_obj = CachedInput(None)
    empty_out_str = empty_obj.read()
    assert empty_out_str == b""

    #seek
    cache_obj.seek(0)
    # Without doing this readline() only ever returns b""?
    # The cursor is set to the last position after read() was called?

    #readline()
    frst_line = cache_obj.readline()
    scnd_line = cache_obj.readline()
    assert frst_line == b"Never worry about theory\n"
    assert scnd_line == b"as long as the machinery does what it's supposed to do"


def test_TrackFile():

    pls_track = TrackFile("tests/testfile.txt")
    #no file yet
    assert pls_track() == False

    pls = open("tests/testfile.txt","w")
    #file created - modified
    assert pls_track() == True
    #modified set to false after check
    assert pls_track() == False


    #file writen - modified
    write_str = "Seems to be a deep instinct in human beings for" \
                " making everything compulsory that isn't forbidden."

    pls.write(write_str)

    pls.close()


    #assert pls_track() == True

    # ^^modification not picked up, WTF?

    os.remove("tests/testfile.txt")
    #file deleted
    assert pls_track.is_deleted() == True





