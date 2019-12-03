# -*- coding: utf-8 -*-
# Copyright (c) 2019-2020 Christiaan Frans Rademan <chris@fwiw.co.za>.
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
import json

from prance import ResolvingParser

from luxon.exceptions import NotFoundError


class Parser(object):
    def __init__(self, schema, base_path=None, default_policy=None):
        schema = 'python://' + schema.strip('/')
        try:
            parser = ResolvingParser(schema,
                                     backend='openapi-spec-validator')
        except (FileNotFoundError, IsADirectoryError):
            raise NotFoundError('OpenAPI Schema not found')
        self._spec = parser.specification
        self._paths = self._spec.get('paths', [])
        self._policy = {}
        if base_path:
            self._spec['basePath'] = base_path.rstrip('/')

        self._request_body = {}
        self._response_body = {}
        self._request_params = {}
        self._operation_ids = {}
        self._routes = []
        self._schemas = []

        for path in self._paths:
            route = self.base_path + '/' + path.strip('/')
            for method in self._paths[path]:
                op_id = self._paths[path][method].get('operationId')
                params = self._paths[path][method].get('parameters', [])
                resps = self._paths[path][method].get('responses', [])

                if op_id:
                    if op_id not in self._operation_ids:
                        self._operation_ids[op_id] = []
                        self._request_params[op_id] = {}
                        self._request_body[op_id] = None
                        self._response_body[op_id] = {}

                    for param in params:
                        if param.get('in', '') == 'query':
                            p_name = param.get('name')
                            if p_name:
                                self._request_params[op_id][p_name] = param
                        elif param.get('in', '') == 'body':
                            self._request_body[op_id] = param

                    for resp in resps:
                        self._response_body[op_id][resp] = resps[resp]

                    _route = (method,
                              route,
                              op_id,
                              default_policy,)

                    self._routes.append(_route)

                    if op_id not in self._operation_ids:
                        self._operation_ids[op_id] = []

                    self._operation_ids[op_id].append(route)

    def set_policy(self, operation_id, policy):
        try:
            self._operation_ids[operation_id][3] = policy
        except KeyError:
            raise ValueError("Unknown OpenAPI operationId '%s'" %
                             operation_id)

    def request_params(self, operation_id):
        return self._request_params[operation_id]

    def request_schema(self, operation_id):
        return self._request_body[operation_id].get('schema')

    def response_schema(self, operation_id, code):
        return self._request_body[operation_id][code].get('schema')

    @property
    def operation_ids(self):
        return tuple(self._operation_ids.keys())

    @property
    def specification(self):
        return self._spec

    @property
    def json(self):
        return json.dumps(self._spec, indent=4)

    @property
    def base_path(self):
        return self._spec.get('basePath', '/')

    @property
    def consumes(self):
        self._consumes = self._spec.get('consumes', ['application/json'])

    @property
    def produces(self):
        self._produces = self._spec.get('produces', ['application/json'])

    @property
    def paths(self):
        return self._paths

    @property
    def routes(self):
        return self._routes
