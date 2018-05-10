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
import traceback

from luxon import g
from luxon.utils.app import init
from luxon.core.handlers.wsgi.request import Request
from luxon.core.handlers.wsgi.response import Response
from luxon.exceptions import (Error, NotFoundError,
                              AccessDeniedError, JSONDecodeError,
                              ValidationError, FieldError,
                              HTTPError, HTTPPreconditionFailed)
from luxon.structs.htmldoc import HTMLDoc
from luxon import render_template
from luxon import GetLogger
from luxon.constants import TEXT_HTML
from luxon.utils.objects import object_name
from luxon.utils.timer import Timer
from luxon.utils.http import etagger

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
    def __init__(self, name, app_root=None, ini=None, content_type=None):
        try:
            # Initilize Application
            init(name, app_root, ini)

            # Set Default Content Type
            if content_type is not None:
                self._RESPONSE_CLASS._DEFAULT_CONTENT_TYPE = content_type

            self._cached_policy = None

            # Started Application
            log.info('Started Application'
                     ' %s' % name +
                     ' app_root: %s' % app_root)

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
        global _cache_engine

        def validate_etag_and_modified():
            # Validates if-match and raises HTTPPreconditionFailed,
            # with 412 status, if not valid.
            #
            # Compare 'if-none-match' and as 'last resort' modified-since
            # for cache hits.

            # Cache hit will set status 304 with empty response instructing
            # external cache or user-agent to use local cache.

            # Set Etag
            # NOTE(cfrademan): Needed Encoding for Different Etag.
            if request.method == 'GET':
                if isinstance(response._stream, bytes):
                    encoding = request.get_header('Accept-Encoding')
                    response.etag.set(etagger(response._stream, encoding))

                # Validate Request Conditional Etag with current content.
                if (len(request.if_match) > 0 and
                        request.if_match not in response.etag):
                    # If match does not match etags
                    # raise HTTPPreconditionFailed
                    raise HTTPPreconditionFailed()

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

        try:
            with Timer() as elapsed:
                # Request Object.
                request = g.current_request = Request(*args,
                                                      **kwargs)

                # Response Object.
                response = Response(*args,
                                    **kwargs)

                # Set Response object for request.
                request.response = response

                # Process the middleware 'pre' method before routing it
                for middleware in g.middleware_pre:
                    middleware(request, response)

                # Route Object.
                resource, method, r_kwargs, target, tag, cache = g.router.find(
                    request.method,
                    request.route)

                # Route Kwargs in requests.
                request.route_kwargs = r_kwargs

                # Set route tag in requests.
                request.tag = tag

                # Get session_id if any for Caching
                session_id = request.cookies.get(request.host)

                # If route tagged validate with policy
                if tag is not None:
                    if not request.policy.validate(tag):
                        raise AccessDeniedError("Access Denied by" +
                                                " policy '%s'" % tag)

                # Execute Routed View.
                try:
                    # Process the middleware 'resource' after routing it
                    for middleware in g.middleware_resource:
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
                    for middleware in g.middleware_post:
                        middleware(request, response)

            # Cache GET Response.
            if request.method == 'GET':
                # Only cache for GET responses!
                if cache > 0 and request.query_string is None:
                    # NOTE(cfrademan): Instruct to use cache but revalidate on,
                    # stale cache entry. Expire remote cache in same duration
                    # as internal cache.
                    if session_id:
                        response.cache_control = "must-revalidate" + \
                                ", private, max-age=" + str(cache)
                    else:
                        response.cache_control = "must-revalidate" + \
                                ", max-age=" + str(cache)
                else:
                    # NOTE(cfrademan): Instruct not use cache but revalidate,
                    # then use cached copy when content is same. (304 response)
                    # Also only keep copy in external/user-agent cache for
                    # 7 days. (604800 seconds)
                    if session_id:
                        response.cache_control = "must-revalidate" + \
                                ", private, no-cache, max-age=604800"
                    else:
                        response.cache_control = "must-revalidate" + \
                                ", no-cache, max-age=604800"

                # Set Vary Header
                # NOTE(cfrademan): Client should uniquely cache
                # based these request headers.
                response.set_header('Vary', 'Cookie, Accept-Encoding' +
                                    ', Content-Type')
            else:
                response.cache_control = "no-store, no-cache, max-age=0"

            validate_etag_and_modified()

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

    def handle_error(self, req, resp, exception, traceback):
        # Parse Exceptions.
        resp.cache_control = "no-store, no-cache, max-age=0"
        if isinstance(exception, HTTPError):
            log.debug('%s' % (traceback))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            resp.status = exception.status
            title = exception.title
            description = exception.description
            for header in exception.headers:
                resp.set_header(header, exception.headers[header])

        elif isinstance(exception, AccessDeniedError):
            log.debug('%s' % (traceback))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            title = "Access Denied"
            description = str(exception)
            resp.status = 403

        elif isinstance(exception, NotFoundError):
            log.debug('%s' % (traceback))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            title = "Not Found"
            description = str(exception)
            resp.status = 404

        elif isinstance(exception, JSONDecodeError):
            log.debug('%s' % (traceback))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            title = "Bad Request (JSON)"
            description = str(exception)
            resp.status = 400

        elif isinstance(exception, FieldError):
            log.debug('%s' % (traceback))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            title = "Bad Request (Field)"
            description = str(exception)
            resp.status = 400

        elif isinstance(exception, ValidationError):
            log.debug('%s' % (traceback))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
            title = "Bad Request"
            description = str(exception)
            resp.status = 400

        elif isinstance(exception, Error):
            log.debug('%s' % (traceback))
            log.error('%s: %s' % (object_name(exception),
                                  exception))
            title = "Error"
            description = str(exception)
            resp.status = 500

        else:
            log.debug('%s' % (traceback))
            log.critical('%s: %s' % (object_name(exception),
                                     exception))
            title = exception.__class__.__name__
            description = str(exception)
            resp.status = 500

        # Generate Error Response
        if req.is_ajax and 'ajax_error_template' in g:
            # Check if AJAX Template and AJAX Request.
            resp.content_type = TEXT_HTML
            resp.body(render_template(g.ajax_error_template,
                                      error_title=title,
                                      error_description=description))

        elif 'error_template' in g:
            # Check if Error Template.
            resp.content_type = TEXT_HTML
            resp.body(render_template(g.error_template,
                                      error_title=title,
                                      error_description=description))

        elif resp.content_type is None or 'json' in resp.content_type.lower():
            # Check if JSON Content and provide JSON Error.
            to_return = {}
            to_return['error'] = {}
            to_return['error']['title'] = title
            to_return['error']['description'] = description

            resp.body(to_return)

        elif 'html' in resp.content_type.lower():
            # Else if HTML Content Respond with Generic HTML Error
            dom = HTMLDoc()
            html = dom.create_element('html')
            head = html.create_element('head')
            t = head.create_element('title')
            t.append(resp.status)
            body = html.create_element('body')
            h1 = body.create_element('h1')
            h1.append(title)
            h2 = body.create_element('h2')
            h2.append(description)
            resp.body(dom.get())

        else:
            # Else Generic TEXT Error.
            resp.body(title + ' ' + description)
