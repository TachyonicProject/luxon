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
import pickle
import time
import datetime

from luxon import g
from luxon.utils.files import Open


class SessionFile(object):
    """ Session File Interface.

    Used for storing session data in flat files.

    Please refer to Session.
    """
    def __init__(self, expire, session_id, session):
        self._expire = expire
        self._session_id = str(session_id)
        self._session = session
        path = "%s/tmp" % g.app.path
        self._file = "%s/session_%s.pickle" % (path, self._session_id,)

    def load(self):
        try:
            with Open(self._file, 'rb', 0) as sf:
                ts = int(time.mktime(datetime.datetime.now().timetuple()))
                stat = os.stat(self._file)
                lm = int(stat.st_mtime)
                if ts - lm > self._expire:
                    self._session.clear()
                    try:
                        os.unlink(self._file)
                    except FileNotFoundError:
                        pass
                else:
                    try:
                        self._session.update(pickle.load(sf))
                    except EOFError:
                        self._session.clear()
                        pass
        except FileNotFoundError:
            self._session.clear()

    def save(self):
        if len(self._session) > 0:
            with Open(self._file, 'wb', 0) as fd:
                pickle.dump(self._session, fd)

    def clear(self):
        with Open(self._file, 'rb', 0):
            self._session.clear()
            try:
                os.unlink(self._file)
            except FileNotFoundError:
                pass
