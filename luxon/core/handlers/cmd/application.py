# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Christiaan Frans Rademan.
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
import os
import argparse
import traceback

from luxon import g, router
from luxon.core.app import App
from luxon.core.handlers.cmd.request import Request
from luxon.core.handlers.cmd.response import Response
from luxon.exceptions import (Error, NotFoundError,
                              AccessDeniedError, JSONDecodeError,
                              ValidationError, FieldError,
                              HTTPError)
from luxon.core.logger import GetLogger
from luxon.utils.objects import object_name
from luxon.utils.timer import Timer
from luxon.core import register
from luxon.utils.daemon import Daemon

log = GetLogger(__name__)


class Application(object):
    """This class is part of the main entry point into the application.

    Each instance provides a callable interface for WSGI requests.

    Args:
        name (str): Unique Name for application. Use __name__ of module to
            ensure root path for application can be found conveniantly.

    Keyword Arguments:
        app_root (str): Path to application root. (e.g. The location of
            'settings.ini', 'policy.json' and overiding 'templates')
    """
    def __init__(self, name, path=None, ini=None, defaults=False,
                 middleware=None):
        try:
            # Initilize Application
            self._middleware = middleware
            App(name, path=path, ini=ini, defaults=defaults)
            # Started Application
            log.info('CMD'
                     ' %s' % name +
                     ' app_root: %s' % g.app.path)

        except Exception:
            trace = str(traceback.format_exc())
            log.critical("%s" % trace)
            raise

    def __call__(self):
        """Application Request Interface.

        A clean request and response object is provided to the interface that
        is unique this to this thread.

        It passes any args and kwargs to the interface.

        Response object is returned.
        """
        parser = argparse.ArgumentParser(
            description=g.app.name
        )
        action = parser.add_mutually_exclusive_group()
        action.add_argument('-f', '--fork',
                            action='store_true',
                            help='Fork Process')
        action.add_argument('-k', '--kill',
                            action='store_true',
                            help='Stop/Kill Process')
        action.add_argument('-r', '--restart',
                            action='store_true',
                            help='Restart Process')
        action.add_argument('-d', '--debug',
                            action='store_true',
                            help='Debug')
        parser.add_argument('-a', '--app',
                            dest='app',
                            default=None,
                            help='Application Path')
        parser.add_argument('-p', '--pid',
                            dest='pid',
                            default=None,
                            help='PID File')
        subparsers = parser.add_subparsers(dest='method', help='Methods')
        subparsers.required = True

        methods = router.methods
        for m in methods:
            m = m.lower()
            sub = subparsers.add_parser(m,
                                        help='%s resources'
                                        % m)
            sub.set_defaults(method=m.upper())
            sub.add_argument('route',
                             nargs='?',
                             default=None,
                             help='Resource Route')

        args = parser.parse_args()

        if hasattr(args, 'route') and isinstance(args.route, str):
            args.route = args.route.strip('/')
        if args.method is not None:
            args.method = args.method.lower()

        if hasattr(args, 'route') and args.route is None:
            parser.print_help()
            print('\nroutes for %s:' % args.method)
            index = router.routes
            for route in index:
                if route[1] == args.method.upper():
                    print("\t/%s" % route[0])
            exit()

        pid_file = g.app.name.replace(' ', '_').lower()
        pid_file += '_' + args.method.lower() + '_'
        pid_file += args.route.replace('/', '_').lower()
        pid_file += '.pid'

        if args.app:
            g.app._path = os.path.abspath(args.app)
            App(g.app.name, path=args.app)
            pid_file = g.app.path + '/tmp/' + pid_file

        if args.pid:
            pid_file = args.pid

        if not args.app and not args.pid:
            pid_file = g.app.path + '/' + pid_file

        if args.debug:
            GetLogger().level = 'DEBUG'

        if self._middleware:
            if isinstance(self._middleware, (tuple, list,)):
                for func in self._middleware:
                    func()
            else:
                self._middleware()

        fork = Daemon(pid_file, run=self.proc, args=(args.method, args.route,))
        if args.fork:
            fork.start()
        elif args.kill is True:
            fork.stop()
            exit()
        elif args.restart is True:
            fork.restart()
            exit()
        else:
            fork.start(fork=False)

    def proc(self, method, route):
        try:
            with Timer() as elapsed:
                # Request Object.
                request = g.current_request = Request(method,
                                                      route)

                # Response Object.
                response = Response()

                # Set Response object for request.
                request.response = response

                # Debug output
                if g.app.debug is True:
                    log.info('Request %s' % request.route +
                             ' Method %s\n' % request.method)

                # Process the middleware 'pre' method before routing it
                for middleware in register._middleware_pre:
                    middleware(request, response)

                # Route Object.
                resource, method, r_kwargs, target, tag, cache = router.find(
                    request.method,
                    request.route)

                # Route Kwargs in requests.
                request.route_kwargs = r_kwargs

                # Set route tag in requests.
                request.tag = tag

                # If route tagged validate with policy
                if tag is not None:
                    if not request.policy.validate(tag):
                        raise AccessDeniedError("Access Denied by" +
                                                " policy '%s'" % tag)

                # Execute Routed View.
                try:
                    # Process the middleware 'resource' after routing it
                    for middleware in register._middleware_resource:
                        middleware(request, response)
                    # Run View method.
                    if resource is not None:
                        view = resource(request,
                                        response,
                                        **r_kwargs)
                        if view is not None:
                            response.write(view)
                    else:
                        raise NotFoundError("Route not found" +
                                            " Method '%s'" % request.method +
                                            " Route '%s'" % request.route)
                finally:
                    # Process the middleware 'post' at the end
                    for middleware in register._middleware_post:
                        middleware(request, response)
        except KeyboardInterrupt:
            response.write('CTRL-C / KeyboardInterrupt')
        except Exception as exception:
            trace = str(traceback.format_exc())
            self.handle_error(request,
                              response,
                              exception,
                              trace)
            # Return response object.
        finally:
            # Completed Request
            log.info('Completed CMD',
                     timer=elapsed())

    def handle_error(self, req, resp, exception, trace):
        if isinstance(exception, HTTPError):
            log.debug('%s' % (trace))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            title = exception.title
            description = exception.description

        elif isinstance(exception, AccessDeniedError):
            log.debug('%s' % (trace))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            title = "Access Denied"
            description = str(exception)

        elif isinstance(exception, NotFoundError):
            log.debug('%s' % (trace))
            log.error('%s: %s' % (object_name(exception),
                                  exception))
            title = "Not Found"
            description = str(exception)

        elif isinstance(exception, JSONDecodeError):
            log.debug('%s' % (trace))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            title = "Bad Request (JSON)"
            description = str(exception)

        elif isinstance(exception, FieldError):
            log.debug('%s' % (trace))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            title = "Bad Request (Field)"
            description = str(exception)

        elif isinstance(exception, ValidationError):
            log.debug('%s' % (trace))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            title = "Bad Request"
            description = str(exception)

        elif isinstance(exception, Error):
            log.debug('%s' % (trace))
            log.error('%s: %s' % (object_name(exception),
                                  exception))
            title = "Error"
            description = str(exception)

        else:
            log.debug('%s' % (trace))
            log.critical('%s: %s' % (object_name(exception),
                                     exception))
            title = exception.__class__.__name__
            description = str(exception)

        resp.write(title + " " + description + '\n')
        exit(1)
