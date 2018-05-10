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
from luxon.utils.password import *

def test_hash():

    password = "Aligator"

    #default: BLOWFISH
    hashed_password = hash(password)
    assert hashed_password[:7] == "$2b$12$"
    # CLEARTEXT
    assert hash(password,const.CLEARTEXT)[:3] == "Ali"
    # SHA256
    assert hash(password, const.SHA256)[:3] == "$5$"
    # SHA512
    assert hash(password, const.SHA512)[:3] == "$6$"
    # LDAP_MD5
    assert hash("spot", const.LDAP_MD5)=="{MD5}suGJq/hegJpRUizbDlMIOg=="
    # LDAP_SMD5
    assert hash(password, const.LDAP_SMD5)[:6] == "{SMD5}"
    # LDAP_SHA1
    assert hash("spot", const.LDAP_SHA1)=="{SHA}n0tScfwMV/tDFLSeqRM78OEqW0U="
    # LDAP_SSHA1
    assert hash(password, const.LDAP_SSHA1)[:6] == "{SSHA}"
    # LDAP_CLEARTEXT
    assert hash(password, const.LDAP_CLEARTEXT)=="Aligator"
    # LDAP_BLOWFISH
    assert hash(password, const.LDAP_BLOWFISH)[:14] == "{CRYPT}$2b$12$"
    # LDAP_SHA256
    assert hash(password, const.LDAP_SHA256)[:10] == "{CRYPT}$5$"
    # LDAP_SHA512
    assert hash(password, const.LDAP_SHA512)[:10] == "{CRYPT}$6$"

def test_valid():

    password = "Aligator"
    hashed_password = hash(password)
    assert valid(password,hashed_password)

    password = "Crocodile"
    hashed_password = hash(password,const.SHA512)
    assert valid(password,hashed_password)

    password = "Caiman"
    hashed_password = hash(password,const.LDAP_SSHA1)
    assert valid(password,hashed_password)
