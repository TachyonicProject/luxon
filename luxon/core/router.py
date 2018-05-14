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
import re
from collections import OrderedDict

from luxon.utils.cast import to_tuple
from luxon.utils.objects import object_name
from luxon.core.logger import GetLogger
from luxon.ext.falcon.compiled import CompiledRouter
from luxon.core.cls.singleton import Singleton
from luxon import exceptions

log = GetLogger(__name__)

_routers = {}
_routes = {}
_regex_routes = {}

# NOTE(cfrademan): Discover the type at runtime for RE compiled. When the type
# of something isn't well specified, there's nothing wrong with using the type
# builtin to discover the answer at runtime. Discovering the type at runtime
# protects you from having to access private attributes and against future
# changes to the return type. There's nothing inelegant about using type here,
# though there may be something inelegant about wanting to know the type
# at all.
retype = type(re.compile('hello, world'))


class Router(metaclass=Singleton):
    """ Simple Router Interface.

    The router is used to index and return views based on url and method.

    Attributes:
        routes (list): List of tuples containing routes.
            e.g. [ ( 'GET', '/test', 'rule1', resource_view_object), ]
    """
    __slots__ = ()

    @property
    def routes(self):
        routes = []
        for route in _routes:
            resource, method, kwargs, route, tag, cache = _routes[route]
            if not isinstance(route, retype):
                uri = route
            else:
                uri = str(route)
            try:
                cls = resource.__self__.__class__
            except AttributeError:
                cls = None
            routes.append((uri, method, tag, cls, resource))
        routes.sort()

        return routes

    @property
    def index(self):
        routes = OrderedDict()

        for route in self.routes:
            route, method, tag, cls, resource = route

            cls_doc = cls.__doc__

            if cls is not None:
                try:
                    name = cls._resources_name
                except AttributeError:
                    name = cls.__name__

                if name not in routes:
                    routes[name] = OrderedDict()
                cls = routes[name]
                cls['doc'] = cls_doc
            else:
                cls = routes

            if route not in cls:
                cls[route] = OrderedDict()
            if method not in cls[route]:
                cls[route][method] = OrderedDict()
                cls[route][method]['doc'] = resource.__doc__
                cls[route][method]['tag'] = tag

        return routes

    def find(self, method, route):
        """Route based on Request Object.

        Search for a route that matches the given partial URI.

        Args:
            method (str): Request method.
                For example in HTTP...
                luxon.constants. can be used ie HTTP_GET
                * HTTP_GET
                * HTTP_POST
                * HTTP_PUT
                * HTTP_PATCH
                * HTTP_DELETE
            route (str): The requested path to route.
        """
        method = method.upper()

        if method + ':' + route.strip('/') in _routes:
            return _routes['%s:%s' % (method, route.strip('/'))]
        try:
            found = _routers[method].find(route)
            if found[0]:
                return found
        except KeyError:
            pass
        try:
            for regex_route in _regex_routes[method]:
                if regex_route[3].match(route):
                    return regex_route
        except KeyError:
            pass

        # DEFAULT EMPTY
        return (None, None, {}, None, None, 0)

    def add(self, methods, route, resource, tag=None, cache=0):
        """Add route to view.

        The route() method is used to associate a URI template with
        a resource. Luxon then maps incoming requests to resources
        based on these templates.

        URI Template example: "/music/rock"

        If the route’s template contains field expressions, any responder that
        desires to receive requests for that route must accept arguments named
        after the respective field names defined in the template.

        A field expression consists of a bracketed field name.
        For example, given the following template: "/music/{genre}"

        The view would look like:
            def genre(self, req, resp, genre):

        Args:
            methods (list): List of Methods. Use constants in
                For example in HTTP...
                luxon.constants. can be used ie HTTP_GET
                * HTTP_GET
                * HTTP_POST
                * HTTP_PUT
                * HTTP_PATCH
                * HTTP_DELETE
            route (str): Route resource. (URI Template)
            resource (object): Actual view function or method.

        Keyword Args:
            tag (str): Used to identify rule_set to apply. default: 'None'
        """
        methods = to_tuple(methods)
        if route[0:6].lower() == "regex:":
            route = route[6:]
            for method in methods:
                method = method.upper()
                try:
                    route = re.compile(route)
                    _regex_routes[method].append((resource,
                                                  method,
                                                  {},
                                                  route,
                                                  tag,
                                                  cache,))
                    _routes['%s:%s' % (method, route)] = (resource,
                                                          method,
                                                          {},
                                                          route,
                                                          tag,
                                                          cache)
                except KeyError:
                    _regex_routes[method] = []
                    route = re.compile(route)
                    _routes['%s:%s' % (method, route)] = (resource,
                                                          method,
                                                          {},
                                                          route,
                                                          tag,
                                                          cache)
                    _regex_routes[method].append(_routes['%s:%s' % (method,
                                                                    route)])
                except Exception as e:
                    raise exceptions.Error("Bad RE expression for route '%s'" %
                                           route
                                           + ". (%s)" % e)
        else:
            route = route.strip('/')
            for method in methods:
                method = method.upper()
                try:
                    if not isinstance(route, retype) and '{' in route:
                        _routers[method].add_route(route,
                                                   method,
                                                   resource,
                                                   tag,
                                                   cache)

                    _routes['%s:%s' % (method, route)] = (resource,
                                                          method,
                                                          {},
                                                          route,
                                                          tag,
                                                          cache)
                except KeyError:
                    if not isinstance(route, retype) and '{' in route:
                        _routers[method] = CompiledRouter()
                        _routers[method].add_route(route,
                                                   method,
                                                   resource,
                                                   tag,
                                                   cache)

                    _routes['%s:%s' % (method, route)] = (resource,
                                                          method,
                                                          {},
                                                          route,
                                                          tag,
                                                          cache)

        log.info('Added Route: %s' % route +
                 ' Methods: %s' % str(methods) +
                 ' Resource: %s' % object_name(resource) +
                 ' Tag: %s' % tag +
                 ' Cache: %s' % cache)
