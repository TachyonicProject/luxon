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
from luxon.utils.pool import Pool
from luxon.core.db.mysql import connect

_cached_pool = {}


def _get_conn():
    """_get_conn function for internal use

    Returns a connect object populated with the information under
    the 'database' section
    """
    kwargs = g.app.config.kwargs('database')
    if kwargs.get('type') == 'mysql':
        return connect(kwargs.get('write',
                                  kwargs.get('host', '127.0.0.1')),
                       kwargs.get('username', 'tachyonic'),
                       kwargs.get('password', 'password'),
                       kwargs.get('database', 'tachyonic'),
                       port=int(kwargs.get('write_port',
                                           kwargs.get('port', 3306))))


def dbw():
    """Function db - returns a Database Connection object from pool.

    A Connection pool is created if one does not exist yet.

    Database types and parameters obtained from settings.ini file.

    Write only database connection for MariaDB / MySQL Only.

    Returns:
         Database Connection object
    """
    kwargs = g.app.config.kwargs('database')
    global _cached_pool
    if kwargs.get('type') == 'mysql':
        if _cached_pool.get(os.getpid()) is None:
            _cached_pool[os.getpid()] = Pool(
                _get_conn,
                pool_size=kwargs.get('pool_size', 64),
                max_overflow=kwargs.get('max_overflow', 0))
        return _cached_pool[os.getpid()]()
    else:
        raise TypeError('Unknown Database type defined in configuration')
