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
from threading import RLock

from luxon import exceptions
from luxon.core.logger import GetLogger
from luxon.core.db.base.cursor import Cursor
from luxon.core.db.base.exceptions import Exceptions as BaseExeptions

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
# Currently only the strings "1.0" and "2.0" are allowed.
# If not given, a DB-API 1.0 level interface should be assumed.
apilevel = "2.0"
#
# threadsafety
# 0	Threads may not share the module.
# 1	Threads may share the module, but not connections.
# 2	Threads may share the module and connections.
# 3	Threads may share the module, connections and cursors.
threadsafety = 1
# Sharing in the above context means that two threads may use a resource
# without wrapping it using a mutex semaphore to implement resource locking.
# Note that you cannot always make external resources thread safe by managing
# access using a mutex: the resource may rely on global variables or other
# external sources that are beyond your control.
#
# paramstyle
paramstyle = "qmark"
# paramstyle	Meaning
# qmark		Question mark style, e.g. ...WHERE name=?
# numeric	Numeric, positional style, e.g. ...WHERE name=:1
# named		Named style, e.g. ...WHERE name=:name
# format	ANSI C printf format codes, e.g. ...WHERE name=%s
# pyformat	Python extended format codes, e.g. ...WHERE name=%(name)s


log = GetLogger(__name__)

error_map = (
)
cast_map = (
)


class Connection(BaseExeptions):
    DB_API = None
    CHARSET = 'utf-8'
    DEST_FORMAT = None
    ERROR_MAP = error_map
    CAST_MAP = cast_map
    _crsr_cls_args = []
    THREADSAFETY = threadsafety
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls.THREADSAFETY == 0:
            if cls not in Connection._instances:
                Connection._instances[cls] = object.__new__(cls)
                Connection._instances[cls]._lock = RLock()
            Connection._instances[cls]._lock.acquire()
            return Connection._instances[cls]
        else:
            return object.__new__(cls)

    def __init__(self, *args, **kwargs):
        try:
            self._conn = self.DB_API.connect(*args, **kwargs)
            self._cached_crsr = None
            self._crsr_cls = None
            self._uncommited = False
            self._cursors = []
        except Exception as e:
            self._error_handler(self, e, self.ERROR_MAP)

    def __repr__(self):
        return str(self)

    def cursor(self):
        """Return a new Cursor Object using the connection.

        If the database does not provide a direct cursor concept, the module
        will have to emulate cursors using other means to the extent needed by
        this specification.

        Reference PEP-0249
        """
        crsr = Cursor(self)
        self._cursors.append(crsr)
        return crsr

    @property
    def _crsr(self):
        if self._cached_crsr is None:
            self._cached_crsr = self.cursor()
        return self._cached_crsr

    @property
    def messages(self):
        """Cursor.messages except that the list are connection oriented.

        The list is cleared automatically by all standard connection methods calls
        (prior to executing the call) to avoid excessive memory usage and can also be
        cleared by executing del connection.messages[:].

        Warning Message: "DB-API extension connection.messages used"

        Reference PEP-0249
        """
        raise NotImplemented()

    def execute(self, *args, **kwargs):
        """Prepare and execute a database operation (query or command).

        This method is for conveniance and non-standard.

        Parameters may be provided as sequence or mapping and will be bound to
        variables in the operation. Variables are specified in a
        database-specific notation (see the module's paramstyle attribute for
        details).

        A reference to the operation will be retained by the cursor. If the
        same operation object is passed in again, then the cursor can optimize
        its behavior. This is most effective for algorithms where the same
        operation is used, but different parameters are bound to it (many
        times).

        For maximum efficiency when reusing an operation, it is best to use the
        .setinputsizes() method to specify the parameter types and sizes ahead
        of time. It is legal for a parameter to not match the predefined
        information; the implementation should compensate, possibly with a loss
        of efficiency.

        The parameters may also be specified as list of tuples to e.g. insert
        multiple rows in a single operation, but this kind of usage is
        deprecated: .executemany() should be used instead.

        Return values are not defined in the standard. However goal is to
        always return a list of rows being dictionary of column/key values in
        this "IMPLEMENTATION".

        Reference PEP-0249
        """
        return self._crsr.execute(*args, **kwargs)

    def has_table(self, table):
        try:
            query = 'SELECT * FROM %s limit 0' % table
            self.execute(query)
            return True
        except exceptions.SQLOperationalError:
            # THIS ONE MATCHES FOR SQLLITE3? Kinda wrong.
            return False
        except exceptions.SQLProgrammingError:
            # MYSQL USES THIS ONE
            return False

    def has_field(self, table, field):
        try:
            query = 'SELECT %s FROM %s LIMIT 0' % (field,
                                                   table)
            self.execute(query)
            return True
        except exceptions.SQLOperationalError:
            # THIS ONE MATCHES FOR SQLLITE3? Kinda wrong.
            return False
        except exceptions.SQLDatabaseError:
            # MYSQL USES THIS ONE?
            return False
        except exceptions.SQLProgrammingError:
            # MYSQL USES THIS ONE?
            return False

    def insert(self, table, data):
        """Insert data into table.

        Args:
            table (str): Table name.
            data (list): List of rows containing values.
        """
        self._crsr.insert(table, data)

    def clean_up(self):
        """Cleanup server Session.

        Auto rollback and Auto commit neccessary for next request to start
        new transactions. If not applied select queries will return cached
        results.

        Pool runs this method to ensure new requests start up in clean state.
        """
        for crsr in self._cursors:
            crsr.clean_up()

    def close(self):
        """Close the connection

        Close the connection now (rather than whenever .__del__() is called).

        The connection will be unusable from this point forward; an Error (or
        subclass) exception will be raised if any operation is attempted with
        the connection. The same applies to all cursor objects trying to use
        the connection. Note that closing a connection without committing the
        changes first will cause an implicit rollback to be performed.

        Reference PEP-0249
        """
        self.clean_up()
        for crsr in self._cursors:
            crsr.close()

        try:
            self._lock.release()
            self._cached_crsr = self.cursor()
        except AttributeError:
            # NOTE(cfrademan) Its not got locking so close it..
            # locking objects are singleton object.
            self._conn.close()

    def commit(self):
        """Commit Transactionl Queries.

        Commit any pending transaction to the database.

        Note that if the database supports an auto-commit feature, this
        must be initially off. An interface method may be provided to
        turn it back on.

        Database modules that do not support transactions should implement
        this method with void functionality.

        Reference PEP-0249
        """
        self._crsr.commit()

    def rollback(self):
        """Rollback current transaction.

        This method is optional since not all databases provide transaction
        support.

        In case a database does provide transactions this method causes the
        database to roll back to the start of any pending transaction. Closing
        a connection without committing the changes first will cause an
        implicit rollback to be performed.

        Reference PEP-0249
        """
        self._crsr.rollback()

    def last_row_id(self):
        """Return last row id.

        This method returns the value generated for an AUTO_INCREMENT
        column by the previous INSERT or UPDATE statement or None
        is no column available or rather AUTO_INCREMENT not used.
        """
        return self._crsr.lastrowid

    def last_row_count(self):
        """Return last row count.

        This method returns the number of rows returned for SELECT statements,
        or the number of rows affected by DML statements such as INSERT
        or UPDATE.
        """
        return self._crsr.rowcount

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()


def connect(*args, **kwargs):
    """Constructor for creating a connection to the database.

    Reference pep-0249.

    Returns a Connection Object. It takes a number of parameters which are
    database dependent.
    """
    return Connection(*args, **kwargs)
