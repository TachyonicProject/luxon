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
    def __init__(self, name, path=None, ini=None, defaults=None):
        try:
            # Initilize Application
            App(name, path, ini)

            # Started Application
            log.info('Started'
                     ' %s' % name +
                     ' app_root: %s' % g.app.path)

        except Exception:
            trace = str(traceback.format_exc())
            log.critical("%s" % trace)
            raise

    def __call__(self):
        """Start Application Process.
        """

    def handle_error(self, req, resp, exception, trace):
        if isinstance(exception, HTTPError):
            log.debug('%s' % (trace))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
        elif isinstance(exception, AccessDeniedError):
            log.debug('%s' % (trace))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
        elif isinstance(exception, NotFoundError):
            log.debug('%s' % (trace))
            log.error('%s: %s' % (object_name(exception),
                                  exception))
        elif isinstance(exception, JSONDecodeError):
            log.debug('%s' % (trace))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
        elif isinstance(exception, FieldError):
            log.debug('%s' % (trace))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
        elif isinstance(exception, ValidationError):
            log.debug('%s' % (trace))
            log.warning('%s: %s' % (object_name(exception),
                                    exception))
        elif isinstance(exception, Error):
            log.debug('%s' % (trace))
            log.error('%s: %s' % (object_name(exception),
                                  exception))
        else:
            log.debug('%s' % (trace))
            log.critical('%s: %s' % (object_name(exception),
                                     exception))
