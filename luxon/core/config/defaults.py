# -*- coding: utf-8 -*-
# Copyright (c) 2016-2017, Christiaan Frans Rademan.
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

defaults = {
    'DEFAULT': {
        'host': '127.0.0.1',
    },
    'application': {
        'name': 'Application',
        'static': '/static',
        'use_forwarded': 'false',
        'timezone': 'local',
        'default_theme': 'default',
        'log_stdout': 'True',
        'log_level': 'WARNING',
        'debug': 'False',
    },
    'restapi': {
        'uri': 'http://127.0.0.1/infinitystone',
        'interface': 'public',
        'region': 'default',
        'connect_timeout': '2',
        'read_timeout': '8',
        'verify': 'True',
    },
    'tokens': {
        'expire': '3600',
    },
    'sessions': {
        'expire': '86400',
        'backend': 'luxon.core.session:Cookie',
        'session': 'luxon.core.session:TrackCookie',
    },
    'database': {
        'type': 'sqlite3',
    },
    'redis': {
        'db': '0',
    },
    'cache': {
        'backend': 'luxon.core.cache:Memory',
        'max_objects': '5000',
        'max_object_size': '50',
    },
}
