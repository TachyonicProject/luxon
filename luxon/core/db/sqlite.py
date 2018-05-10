# -*- coding: utf-8 -*-
# Copyright (c) 2018, Christiaan Frans Rademan.
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
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTI-
# TUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUP-
# TION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY,OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
import sqlite3
from decimal import Decimal as PyDecimal

from luxon import exceptions
from luxon.core.db.base.connection import Connection as BaseConnection

# LOCALIZE Exceptions to Module as pep-0249
from luxon.core.db.base.exceptions import (Error, Warning,
                                           InterfaceError,
                                           DatabaseError,
                                           DataError,
                                           OperationalError,
                                           IntegrityError,
                                           InternalError,
                                           ProgrammingError,
                                           NotSupportedError)

# Globals as per pep-0249
#########################
# String constant stating the supported DB API level.
# Currently only the strings "1.0" and "2.0" are allowed. If not given, a DB-API 1.0 level interface should be assumed.
apilevel = "2.0"
#
# threadsafety
# 0     Threads may not share the module.
# 1     Threads may share the module, but not connections.
# 2     Threads may share the module and connections.
# 3     Threads may share the module, connections and cursors.
threadsafety = 0
# Sharing in the above context means that two threads may use a resource
# without wrapping it using a mutex semaphore to implement resource locking.
# Note that you cannot always make external resources thread safe by managing
# access using a mutex: the resource may rely on global variables or other
# external sources that are beyond your control.
#
# paramstyle
paramstyle = "qmark"
# paramstyle    Meaning
# qmark         Question mark style, e.g. ...WHERE name=?
# numeric       Numeric, positional style, e.g. ...WHERE name=:1
# named         Named style, e.g. ...WHERE name=:name
# format        ANSI C printf format codes, e.g. ...WHERE name=%s
# pyformat      Python extended format codes, e.g. ...WHERE name=%(name)s

# MAP Python SQLITE3 Exceptions to Luxon.
error_map = (
    (sqlite3.Warning, 'Warning'),
    (sqlite3.ProgrammingError, 'ProgrammingError'),
    (sqlite3.OperationalError, 'OperationalError'),
    (sqlite3.IntegrityError, 'IntegrityError'),
    (sqlite3.DatabaseError, 'DatabaseError'),
    (sqlite3.Error, 'Error'),
)
# MAP Python Types.
cast_map = (
    (PyDecimal, float),
)


class Connection(BaseConnection):
    DB_API = sqlite3
    ERROR_MAP = error_map
    CAST_MAP = cast_map
    DEST_FORMAT='qmark'
    THREADSAFETY = threadsafety

    def __init__(self, db):
        super().__init__(db)
        self._crsr_cls = getattr(self._conn, 'cursor')
        self._db = db
        self._conn.row_factory = sqlite3.Row
        self.execute('PRAGMA foreign_keys = ON;')

    def __str__(self):
        return "SQLite3 Database '%s'" % self._db

def connect(*args, **kwargs):
    """Constructor for creating a connection to the database.

    Reference pep-0249.

    Returns a Connection Object. It takes a number of parameters which are
    database dependent.
    """
    return Connection(*args, **kwargs)
