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

from luxon.core.logger import GetLogger
from luxon.utils import imports
from luxon.utils.files import abspath, exists

log = GetLogger(__name__)


def determine_app_root(name, app_root=None):
    """Determines the root directory of a given application

    Args:
        name (str): application name

    Returns:
        Root directory of app, as a string
    """
    if app_root is None:
        if name == "__main__" or "_mod_wsgi" in name:
            app_mod = imports.import_module(name)
            return abspath(
                os.path.dirname(
                    app_mod.__file__)).rstrip('/')
        else:
            log.error("Unable to determine application root." +
                      " Using current working directory '%s'" % os.getcwd())
            return abspath(os.getcwd()).rstrip('/')
    else:
        if exists(app_root) and not os.path.isfile(app_root):
            return abspath(app_root).rstrip('/')
        else:
            raise FileNotFoundError("Invalid path"
                                    + " for root '%s'"
                                    % app_root) from None
