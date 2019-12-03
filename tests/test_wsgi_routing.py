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
import pytest

from luxon import g
from luxon import register
from luxon import router

g.router = router

@pytest.fixture(scope="module")
def client():
    from luxon.testing.wsgi.client import Client
    return Client(__file__)

METHODS = ('GET', 'POST', 'PUT', 'PATCH',
           'DELETE', 'HEAD', 'OPTIONS', )

@register.resources()
class Routing(object):
    def __init__(self):
        g.router.add('GET', '/routing', self.home)
        g.router.add(['POST', 'PUT',
                      'PATCH', 'DELETE',
                      'HEAD', 'OPTIONS',],
                      '/routing', self.home)

        g.router.add('GET', '/routing/{key1}/{key2}', self.keywords)
        g.router.add('GET', '/routing/{key1}/next/{key2}', self.keywords)

    def home(self, req, resp):
        return req.method

    def keywords(self, req, resp, key1, key2):
        return "%s:%s" % (key1, key2,)

def test_wsgi_methods(client):
    for method in METHODS:
        req = getattr(client, method.lower())
        result = req(path='/routing')
        assert result.status_code == 200
        assert result.text == method

def test_wsgi_route_keywords(client):
    # route = /routing/{key1}/{key2}
    result = client.get(path='/routing/iamkey1/iamkey2')
    assert result.status_code == 200
    assert result.text == "iamkey1:iamkey2"

    # route = /routing/{key1}/next/{key2}
    result = client.get(path='/routing/iamkey1/next/iamkey2')
    assert result.status_code == 200
    assert result.text == "iamkey1:iamkey2"
