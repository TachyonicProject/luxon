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
import mimetypes

from luxon import g
from luxon import metadata
from luxon import register_resource
from luxon import constants as const
from luxon.structs.htmldoc import HTMLDoc


@register_resource(['GET', 'POST'],
                   'regex:^/' +
                   g.config.get('application', 'static').strip('/')
                   + '.*$', cache=604800)
def static(req, resp):
    """Serves files from static directory"""
    sfile_path = g.app_root.rstrip('/') + '/static' \
        + '/' + '/'.join(req.relative_resource_uri.strip('/').split('/')[1:])
    try:
        if os.path.isfile(sfile_path):
            sfile = open(sfile_path, 'rb').read()
            resp.content_type = const.APPLICATION_OCTET_STREAM
            mime_type = mimetypes.guess_type(sfile_path)
            if mime_type is not None:
                resp.content_type = mime_type[0]
                if mime_type[1] is not None:
                    resp.content_type += ';charset=%s' % mime_type[1]
            return sfile
        elif os.path.isdir(sfile_path):
            page = HTMLDoc()
            resp.content_type = const.TEXT_HTML
            folder = os.listdir(sfile_path)
            html = page.create_element('HTML')
            head = html.create_element('HEAD')
            title = head.create_element('TITLE')
            title.append(req.relative_resource_uri)
            body = html.create_element('BODY')
            h1 = body.create_element('H1')
            h1.append(req.relative_resource_uri)
            for item in folder:
                item = req.relative_resource_uri.rstrip('/') + '/' + item
                a = body.create_element('A')
                a.set_attribute('href', item)
                a.append(item)
                body.create_element('BR')
            h3 = body.create_element('H3')
            h3.append(metadata.identity)
            return str(page)
        else:
            raise FileNotFoundError(
                "No such file or directory: '%s'" % sfile_path
            )
    except Exception as e:
        return "Error %s" % (e,)
