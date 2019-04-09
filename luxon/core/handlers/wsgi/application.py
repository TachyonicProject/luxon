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
import traceback

from luxon import g, router
from luxon.core.app import App
from luxon.core.handlers.wsgi.request import Request
from luxon.core.handlers.wsgi.response import Response
from luxon.exceptions import (Error, NotFoundError,
                              AccessDeniedError, JSONDecodeError,
                              ValidationError, FieldError,
                              HTTPError, TokenExpiredError)
from luxon.utils.html5 import error_page, error_ajax
from luxon import render_template
from luxon.core.logger import GetLogger
from luxon.constants import TEXT_HTML, TEXT_PLAIN
from luxon.utils.objects import object_name
from luxon.utils.timer import Timer
from luxon.utils.http import etagger
from luxon.core import register

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
    def __init__(self, name, path=None, ini=None, content_type=None):
        try:
            # Initilize Application
            app = App(name, path, ini)

            # Set Default Content Type
            if content_type is not None:
                Response._DEFAULT_CONTENT_TYPE = content_type

            # Started Application
            log.info('Started Application'
                     ' %s' % app.name +
                     ' path: %s' % app.path)

        except Exception:
            trace = str(traceback.format_exc())
            log.critical("%s" % trace)
            raise

    def __call__(self, *args, **kwargs):
        """Application Request Interface.

        A clean request and response object is provided to the interface that
        is unique this to this thread.

        It passes any args and kwargs to the interface.

        Response object is returned.
        """
        try:
            with Timer() as elapsed:
                # Request Object.
                request = g.current_request = Request(*args,
                                                      **kwargs)
                request.env['SCRIPT_NAME'] = g.app.config.get(
                    'application',
                    'script',
                    fallback=request.env['SCRIPT_NAME'])

                script_name = request.get_header('X-Script-Name')
                if script_name:
                    request.env['SCRIPT_NAME'] = script_name

                # Response Object.
                response = Response(*args,
                                    **kwargs)

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
                            response.body(view)
                    else:
                        raise NotFoundError("Route not found" +
                                            " Method '%s'" % request.method +
                                            " Route '%s'" % request.route)
                finally:
                    # Process the middleware 'post' at the end
                    for middleware in register._middleware_post:
                        middleware(request, response)

            # Cache GET Response.
            # Only cache for GET responses!
            if cache > 0 and request.method == 'GET':
                # Get session_id if any for Caching
                session_id = request.cookies.get(request.host)

                # NOTE(cfrademan): Instruct to use cache but revalidate on,
                # stale cache entry. Expire remote cache in same duration
                # as internal cache.
                if session_id:
                    response.set_header(
                        "cache-control",
                        "must-revalidate, private, max-age=" + str(cache)
                    )
                else:
                    response.set_header(
                        "cache-control",
                        "must-revalidate, max-age=" + str(cache)
                    )

                # Set Vary Header
                # NOTE(cfrademan): Client should uniquely cache
                # based these request headers.
                response.set_header('Vary',
                                    'Cookie, Accept-Encoding' +
                                    ', Content-Type')

                # Set Etag
                # NOTE(cfrademan): Needed Encoding for Different Etag.
                if isinstance(response._stream, bytes):
                    encoding = request.get_header('Accept-Encoding')
                    response.etag.set(etagger(response._stream, encoding))

                # If Etag matches do not return full body use
                # external/user-agent cache.
                if (len(request.if_none_match) > 0 and
                        request.if_none_match in response.etag):
                    # Etag matches do not return full body.
                    response.not_modified()

                # NOTE(cfrademan): Use last_modified as last resort for
                # external/user-agent cache.
                elif (request.if_modified_since and
                      response.last_modified and
                      request.if_modified_since <= response.last_modified):
                    # Last-Modified matches do not return full body.
                    response.not_modified()
            else:
                response.set_header("cache-control",
                                    "no-store, no-cache, max-age=0")

            # Return response object.
            return response()

        except HTTPError as exception:
            trace = str(traceback.format_exc())
            self.handle_error(request, response, exception, trace)
            # Return response object.
            return response()
        except Error as exception:
            trace = str(traceback.format_exc())
            self.handle_error(request, response, exception, trace)
            # Return response object.
            return response()
        except Exception as exception:
            trace = str(traceback.format_exc())
            self.handle_error(request,
                              response,
                              exception,
                              trace)
            # Return response object.
            return response()
        finally:
            # Completed Request
            log.info('Completed Request',
                     timer=elapsed())

    def handle_error(self, req, resp, exception, trace):
        # Parse Exceptions.
        resp.cache_control = "no-store, no-cache, max-age=0"
        if isinstance(exception, HTTPError):
            log.debug('%s' % (trace))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            resp.status = exception.status
            title = exception.title
            description = exception.description
            for header in exception.headers:
                resp.set_header(header, exception.headers[header])

        elif isinstance(exception, AccessDeniedError):
            log.debug('%s' % (trace))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            title = "Access Denied"
            description = str(exception)

            if isinstance(exception, TokenExpiredError):
                resp.set_header('X-Expired-Token', 'true')

            resp.status = 403

        elif isinstance(exception, NotFoundError):
            log.debug('%s' % (trace))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            title = "Not Found"
            description = str(exception)
            resp.status = 404

        elif isinstance(exception, JSONDecodeError):
            log.debug('%s' % (trace))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            title = "Bad Request (JSON)"
            description = str(exception)
            resp.status = 400

        elif isinstance(exception, FieldError):
            log.debug('%s' % (trace))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            title = "Bad Request (Field)"
            description = str(exception)
            resp.status = 400

        elif isinstance(exception, ValidationError):
            log.debug('%s' % (trace))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            title = "Bad Request"
            description = str(exception)
            resp.status = 400

        elif isinstance(exception, Error):
            log.debug('%s' % (trace))
            log.error('%s: %s' % (object_name(exception),
                                  exception))
            title = "Error"
            description = str(exception)
            resp.status = 500

        elif isinstance(exception, ValueError):
            log.debug('%s' % (trace))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            title = "Bad Request"
            description = str(exception)
            resp.status = 400
        else:
            log.debug('%s' % (trace))
            log.critical('%s: %s' % (object_name(exception),
                                     exception))
            title = exception.__class__.__name__
            description = str(exception)
            resp.status = 500

        # Generate Error Response
        if req.is_ajax and register._ajax_error_template:
            # if AJAX Template and AJAX Request.
            resp.content_type = TEXT_HTML
            try:
                resp.body(render_template(register._ajax_error_template,
                                          error_title=title,
                                          error_description=description))
            except Exception:
                trace = str(traceback.format_exc())
                log.error('Unable to render ajax error template\n%s' % trace)
                resp.body(error_ajax(title, description))

        elif register._error_template:
            # If Error Template.
            resp.content_type = TEXT_HTML
            try:
                resp.body(render_template(register._error_template,
                                          error_title=title,
                                          error_description=description))
            except Exception:
                trace = str(traceback.format_exc())
                log.error('Unable to render page error template\n%s' % trace)
                resp.body(error_page(title, description))

        elif resp.content_type is None or 'json' in resp.content_type.lower():
            # Check if JSON Content and provide JSON Error.
            to_return = {}
            to_return['error'] = {}
            to_return['error']['title'] = title
            to_return['error']['description'] = description

            resp.body(to_return)

        elif 'html' in resp.content_type.lower():
            # Else if HTML Content Respond with Generic HTML Error
            resp.content_type = TEXT_HTML
            resp.body(error_page(title, description))

        else:
            # Else Generic TEXT Error.
            resp.content_type = TEXT_PLAIN
            resp.body(title + ' ' + description)
