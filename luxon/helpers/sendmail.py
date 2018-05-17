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
from luxon import g
from luxon.utils.mail import SMTPClient


def sendmail(email, rcpt=None, subject=None, body=None, msg=None,
             fail_callback=None, success_callback=None):

    server = g.app.config.get('smtp', 'host', fallback='127.0.0.1')
    port = g.app.config.getint('smtp', 'port', fallback=587)
    tls = g.app.config.getboolean('smtp', 'tls', fallback=False)
    username = g.app.config.get('smtp', 'username', fallback=None)
    password = g.app.config.get('smtp', 'password', fallback=None)

    if username is not None and password is not None:
        auth = (username, password)
    else:
        auth = None

    with SMTPClient(email, server, port=port,
                    tls=tls, auth=auth) as server:
        if isinstance(rcpt, (list, tuple)):
            rcpt_list = rcpt
            for rcpt in rcpt_list:
                if server.send(rcpt, subject=subject, body=body, msg=msg):
                    if success_callback is not None:
                        success_callback(rcpt)
                else:
                    if fail_callback is not None:
                        fail_callback(rcpt)
        else:
            return server.send(rcpt, subject=subject, body=body, msg=msg)
