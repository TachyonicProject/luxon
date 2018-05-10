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
import os

from luxon import g
from luxon import GetLogger
from luxon.utils import imports
from luxon.core.config.defaults import defaults as default_config

log = GetLogger(__name__)

def determine_app_root(name, app_root=None):
    if app_root is None:
        if name == "__main__" or "_mod_wsgi" in name:
            app_mod = imports.import_module(name)
            return os.path.abspath( \
                os.path.dirname( \
                    app_mod.__file__)).rstrip('/')
        else:
            log.error("Unable to determine application root." +
                      " Using current working directory '%s'" % os.getcwd())
            return os.getcwd().rstrip('/')
    else:
        if os.path.exists(app_root) and not os.path.isfile(app_root):
            return app_root.rstrip('/')
        else:
            raise FileNotFoundError("Invalid path"
                                    + " for root '%s'"
                                    % app_root) from None

def load_config(ini, defaults=True):
    if defaults:
        g.config.read_dict(default_config)

    if os.path.isfile(ini):
        g.config.load(ini)
        return g.config

    log.warning("%s not found" % ini)

    return g.config


def init(name, app_root=None, ini=None, defaults=True):
    # Set Application Name
    g.app_name = name

    # Attempt to determine application root.
    g.app_root = app_root = determine_app_root(name,
                                               app_root)

    # Load Configuration
    if ini is None:
        load_config(app_root +
                    '/settings.ini', defaults)
    else:
        load_config(ini, defaults)

    # Configure Logger.
    log.configure()
