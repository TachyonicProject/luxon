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
from docutils.core import publish_parts

from luxon import g
from luxon.utils.timezone import format_datetime, now
from luxon.exceptions import NoContextError

_cached_env = None


def render_template(template, *args, rst2html=False, **kwargs):
    """Function to return a jinja2 rendered template.

    Imports the Environment class from luxon.core.template only when required,
    in order to imporve performance as jinja2 libraries are low to import.

    Args:
        template (str): filename of template to render.

    Retruns:
        jinja2 rendered template with supplied args and kwargs.

    """
    global _cached_env

    if _cached_env is None:
        from luxon.core.template import Environment
        _cached_env = Environment()
        _cached_env.globals['format_datetime'] = format_datetime
        _cached_env.globals['datetime'] = now
        _cached_env.globals['G'] = g

    try:
        app = g.current_request.app.strip('/').strip()
        if app != '':
            app = '/' + app

        context = {
            'APP': app,
            'REQ': g.current_request,
            'REQUEST_ID': g.current_request.id,
            'STATIC': g.current_request.static,
            'CONTEXT': g.current_request.context,
        }

        if hasattr(g.current_request, 'policy'):
            context['POLICY'] = g.current_request.policy.validate

    except NoContextError:
        context = {}

    context.update(kwargs)

    template = _cached_env.get_template(template)
    content = template.render(*args, **context)

    if rst2html:
        content = publish_parts(writer_name='html',
                                source=content)['body']

    return content
