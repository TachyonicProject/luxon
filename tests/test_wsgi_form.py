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
import pytest

from luxon import register

@pytest.fixture(scope="module")
def client():
    from luxon.testing.wsgi.client import Client
    return Client(__file__)

payload = """-----------------------------88571074919314010861842727997
Content-Disposition: form-data; name="text"

test
-----------------------------88571074919314010861842727997
Content-Disposition: form-data; name="multiple_text"

test
-----------------------------88571074919314010861842727997
Content-Disposition: form-data; name="multiple_text"

test
-----------------------------88571074919314010861842727997
Content-Disposition: form-data; name="file"; filename="file"
Content-Type: application/octet-stream

test

-----------------------------88571074919314010861842727997
Content-Disposition: form-data; name="multiple_file"; filename="file"
Content-Type: application/octet-stream

test

-----------------------------88571074919314010861842727997
Content-Disposition: form-data; name="multiple_file"; filename="file"
Content-Type: application/octet-stream

test

-----------------------------88571074919314010861842727997--"""

headers = {}
headers['Content-Type'] = "multipart/form-data;" + \
        "boundary=---------------------------" + \
        "88571074919314010861842727997"
headers['Content-Length'] = "950"

def test_wsgi_form_json(client):
    @register.resource('POST', '/form_json')
    def form_json(req, resp):
        return req.form_json

    result = client.post(path='/form_json', headers=headers, body=payload)
    assert result.status_code == 200

    response = result.json

    assert response['text'] == 'test'

    assert isinstance(response['multiple_text'], list)
    for i in range(2):
        assert response['multiple_text'][i] == 'test'

    assert response['file']['name'] == 'file'
    assert response['file']['type'] == 'application/octet-stream'
    assert response['file']['base64'] == 'dGVzdAo=\n'

    assert isinstance(response['multiple_file'], list)
    for i in range(2):
        assert response['multiple_file'][i]['name'] == 'file'
        assert response['multiple_file'][i]['type'] == 'application/octet-stream'
        assert response['multiple_file'][i]['base64'] == 'dGVzdAo=\n'

def test_wsgi_form_get_first(client):
    @register.resource('POST', '/form_get_first')
    def form_get_first(req, resp):
        return req.get_first('text')

    result = client.post(path='/form_get_first', headers=headers, body=payload)
    assert result.status_code == 200
    assert result.text == 'test'

def test_wsgi_form_get_list(client):
    @register.resource('POST', '/form_get_list')
    def form_get_list(req, resp):
        return req.get_list('multiple_text')

    result = client.post(path='/form_get_list', headers=headers, body=payload)
    assert result.status_code == 200
    response = result.json

    assert isinstance(response, list)
    for i in range(2):
        assert response[i] == 'test'

def test_wsgi_form_get_file(client):
    @register.resource('POST', '/form_get_file')
    def form_get_file(req, resp):
        file = req.get_file('file')
        response = {}
        response['name'] = file.filename
        response['type'] = file.type
        response['data'] = file.file.read()
        return response

    result = client.post(path='/form_get_file', headers=headers, body=payload)
    assert result.status_code == 200
    response = result.json
    assert response['name'] == 'file'
    assert response['type'] == 'application/octet-stream'
    assert response['data'] == 'test\n'

def test_wsgi_form_get_files(client):
    @register.resource('POST', '/form_get_files')
    def form_get_files(req, resp):
        file = req.get_files('multiple_file')
        response = []
        for f in file:
            o = {}
            o['name'] = f.filename
            o['type'] = f.type
            o['data'] = f.file.read()
            response.append(o)
        return response

    result = client.post(path='/form_get_files', headers=headers, body=payload)
    assert result.status_code == 200
    response = result.json

    for i in range(2):
        assert response[i]['name'] == 'file'
        assert response[i]['type'] == 'application/octet-stream'
        assert response[i]['data'] == 'test\n'

def test_wsgi_form_get_all_files(client):
    @register.resource('POST', '/form_get_all_files')
    def form_get_all_files(req, resp):
        file = req.get_all_files()
        response = []
        for f in file:
            o = {}
            o['name'] = f.filename
            o['type'] = f.type
            o['data'] = f.file.read()
            response.append(o)
        return response

    result = client.post(path='/form_get_all_files', headers=headers, body=payload)
    assert result.status_code == 200
    response = result.json

    for i in range(3):
        assert response[i]['name'] == 'file'
        assert response[i]['type'] == 'application/octet-stream'
        assert response[i]['data'] == 'test\n'
