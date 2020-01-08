# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020 Christiaan Frans Rademan <chris@fwiw.co.za>.
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
from luxon.utils.sql import sql as sql_util
from luxon.utils.singleton import ThreadSingleton


class SQLAlchemySessionCtxMgr(object):
    __slots__ = ('_session_maker', '_session')

    def __init__(self, session_maker):
        self._session_maker = session_maker
        self._session = None

    def __enter__(self):
        self._session = self._session_maker()
        return self._session

    def __exit__(self, exception,  value, traceback):
        self._session.close()


class SQLAlchemySessionMaker(metaclass=ThreadSingleton):
    __slots__ = ('_session_makers',)

    def __init__(self):
        self._session_makers = {}

    def __call__(self, config='database'):
        if config not in self._session_makers:
            kwargs = g.app.config.kwargs(config)
            self._session_makers[config] = sql_util(kwargs.get('type',
                                                               'mysql'),
                                                    kwargs.get('username',
                                                               'None'),
                                                    kwargs.get('password',
                                                               'None'),
                                                    kwargs.get('host',
                                                               'localhost'),
                                                    kwargs.get('port',
                                                               '3306'),
                                                    kwargs.get('database',
                                                               'tachyonic'))
        return SQLAlchemySessionCtxMgr(self._session_makers[config])
