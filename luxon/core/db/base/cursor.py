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
from luxon.core.logger import GetLogger
from luxon.core.db.base.args import args_to
from luxon.core.db.base.exceptions import Exceptions as BaseExeptions
from luxon.utils.timer import Timer

log = GetLogger(__name__)


def _log(cursor, msg, elapsed=0, values=None):
    """Debug Log Function

    Function to log in the case where debugging
    is enabled.

    Args:
        db (object): MysqlConnect connection object.
        msg (str): Log message.
        elapsed (float): Time elapsed.
    """
    #if values is not None:
    #    log_msg = msg % values
    #else:
    log_msg = msg + " (%s) (%s)" % (values, cursor,)

    if elapsed is not None and elapsed > 0.1:
        log_msg = " !!!SLOW!!! " + log_msg
    log.info(log_msg, timer=elapsed)

class Cursor(BaseExeptions):
    def __init__(self, conn):
        try:
            self._conn = conn
            self._crsr = conn._crsr_cls(*conn._crsr_cls_args)
            self._uncommited = False
            self.arraysize = 1
            self._rownumber = 0
            self._executed = False
        except Exception as e:
            self._error_handler(self, e, self._conn.ERROR_MAP)

    def __str__(self):
        return "DB-Cursor %s" % self._conn

    def __repr__(self):
        return str(self)

    @property
    def connection(self):
        return self._conn

    @property
    def description(self):
        return self._crsr.description

    @property
    def rowcount(self):
        return self._crsr.rowcount

    @property
    def lastrowid(self):
        return self._crsr.lastrowid

    @property
    def rownumber(self):
        return self._rownumber

    def scroll(self, value, mode='relative'):
        """Scroll the cursor in the result set new position according to mode.

        Warning:
            !!! NOT IMPLEMENTED !!!

        If mode is relative (default), value is taken as offset to the current
        position in the result set, if set to absolute, value states an
        absolute target position.

        An IndexError should be raised in case a scroll operation would leave
        the result set. In this case, the cursor position is left undefined
        (ideal would be to not move the cursor at all).

        Reference PEP-0249
        """
        raise NotImplemented()

    @property
    def messages(self):
        """List of Messages from interfaces from database cursor.

        Warning:
            !!! NOT IMPLEMENTED !!!

        This is a Python list object to which the interface appends tuples
        (exception class, exception value) for all messages which the
        interfaces receives from the underlying database for this cursor.

        The list is cleared by all standard cursor methods calls (prior to
        executing the call) except for the .fetch*() calls automatically to
        avoid excessive memory usage and can also be cleared by executing del
        cursor.messages[:].

        All error and warning messages generated by the database are placed
        into this list, so checking the list allows the user to verify correct
        operation of the method calls.

        The aim of this attribute is to eliminate the need for a Warning
        exception which often causes problems (some warnings really only have
        informational character).

        Reference PEP-0249
        """
        raise NotImplemented()

    def next(self):
        """Return the next row.

        Return the next row from the currently executing SQL statement using
        the same semantics as .fetchone(). A StopIteration exception is raised
        when the result set is exhausted for Python versions 2.2 and later.
        Previous versions don't have the StopIteration exception and so the
        method should raise an IndexError instead.

        Reference PEP-0249
        """
        return self.fetchone()

    def __iter__(self):
        """Return self to make cursors compatible to the iteration protocol

        Reference PEP-0249
        """
        while True:
            value = self.fetchone()
            if value is not None:
                yield value
            else:
                break

    def execute(self, query, args=None):
        """Prepare and execute a database operation (query or command).

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
        with Timer() as elapsed:
            self._rownumber = 0
            try:
                if args is not None and not isinstance(args, (dict,
                                                              list,
                                                              tuple)):
                    args = [ args ]

                query, args = args_to(query, args, self._conn.DEST_FORMAT,
                                      self._conn.CAST_MAP)
                _log(self, "Start " + query, elapsed(), values=args)
                if args is not None:
                    self._crsr.execute(query, args)
                    self._uncommited = True
                else:
                    self._crsr.execute(query)
                    self._uncommited = True
                self._executed = True
                return self
            except Exception as e:
                self._error_handler(self, e, self._conn.ERROR_MAP)
            finally:
                _log(self, "Completed " + query, elapsed(), values=args)

    def executemany(self, query, params):
        """Pepare and Execute Many.

        Warning:
            !!! NOT IMPLEMENTED !!!

        Prepare a database operation (query or command) and then execute it
        against all parameter sequences or mappings found in the sequence
        seq_of_parameters.

        Modules are free to implement this method using multiple calls to the
        .execute() method or by using array operations to have the database
        process the sequence as a whole in one call.

        Use of this method for an operation which produces one or more result
        sets constitutes undefined behavior, and the implementation is
        permitted (but not required) to raise an exception when it detects that
        a result set has been created by an invocation of the operation.

        The same comments as for .execute() also apply accordingly to this method.

        Return values are not defined.

        Reference PEP-0249
        """
        raise NotImplemented()

    def fetchone(self):
        """Fetch row.

        Fetch the next row of a query result set, returning a single sequence,
        or None when no more data is available.

        An Error (or subclass) exception is raised if the previous call to
        .execute*() did not produce any result set or no call was issued yet.

        Reference PEP-0249
        """
        if self._executed is False:
            raise self.ProgrammingError('No data, use execute method first')
        try:
            row = dict(self._crsr.fetchone())
            self._rownumber += 1
            return row
        except TypeError as e:
            return None

    def fetchmany(self, size=None):
        """Fetch many rows.

        Fetch the next set of rows of a query result, returning a sequence of
        sequences (e.g. a list of tuples). An empty sequence is returned when
        no more rows are available.

        The number of rows to fetch per call is specified by the parameter. If
        it is not given, the cursor's arraysize determines the number of rows
        to be fetched. The method should try to fetch as many rows as indicated
        by the size parameter. If this is not possible due to the specified
        number of rows not being available, fewer rows may be returned.

        An Error (or subclass) exception is raised if the previous call to
        .execute*() did not produce any result set or no call was issued yet.

        Note there are performance considerations involved with the size
        parameter. For optimal performance, it is usually best to use the
        .arraysize attribute. If the size parameter is used, then it is best
        for it to retain the same value from one .fetchmany() call to the next.

        Reference PEP-0249
        """
        many = []
        if size is None:
            size = self.arraysize
        for a in range(size):
            many.append(self.fetchone())
        return many

    def fetchall(self):
        """Fetch all rows.

        Fetch all (remaining) rows of a query result, returning them as a
        sequence of sequences (e.g. a list of tuples). Note that the cursor's
        arraysize attribute can affect the performance of this operation.

        An Error (or subclass) exception is raised if the previous call to
        .execute*() did not produce any result set or no call was issued yet.

        Reference PEP-0249
        """
        all = []
        for a in self:
            all.append(a)
        return all

    def nextset(self):
        """Return next result set.

        Warning:
            !!! NOT IMPLEMENTED !!!

        This method is optional since not all databases support multiple result
        sets.

        This method will make the cursor skip to the next available set,
        discarding any remaining rows from the current set.

        If there are no more sets, the method returns None. Otherwise, it
        returns a true value and subsequent calls to the .fetch*() methods will
        return rows from the next result set.

        An Error (or subclass) exception is raised if the previous call to
        .execute*() did not produce any result set or no call was issued yet.

        Reference PEP-0249
        """
        raise NotImplemented()

    def setinputsize(self, size):
        """Predefine memory areas for operations.

        Warning:
            !!! NOT IMPLEMENTED !!!

        This can be used before a call to .execute*() to predefine memory areas
        for the operation's parameters.

        sizes is specified as a sequence — one item for each input parameter.
        The item should be a Type Object that corresponds to the input that
        will be used, or it should be an integer specifying the maximum length
        of a string parameter. If the item is None, then no predefined memory
        area will be reserved for that column (this is useful to avoid
        predefined areas for large inputs).

        This method would be used before the .execute*() method is invoked.

        Implementations are free to have this method do nothing and users are
        free to not use it.

        Reference PEP-0249
        """
        pass

    def setoutputsize(self, size, columns=None):
        """Set output size for fetches of large columns.

        Warning:
            !!! NOT IMPLEMENTED !!!

        Set a column buffer size for fetches of large columns (e.g. LONGs,
        BLOBs, etc.). The column is specified as an index into the result
        sequence. Not specifying the column will set the default size for all
        large columns in the cursor.

        This method would be used before the .execute*() method is invoked.

        Implementations are free to have this method do nothing and users are
        free to not use it.

        Reference PEP-0249
        """
        pass

    def clean_up(self):
        """Cleanup server Session.

        Auto rollback and Auto commit neccessary for next request to start
        new transactions. If not applied select queries will return cached
        results.

        Pool runs this method to ensure new requests start up in clean state.
        """
        if self._uncommited is True:
            self.rollback()
            self.commit()

    def close(self):
        """Close the cursor now (rather than whenever __del__ is called).

        The cursor will be unusable from this point forward; an Error (or
        subclass) exception will be raised if any operation is attempted with
        the cursor.
        """
        self._crsr.close()

    def commit(self):
        """Commit Transactionl Queries.

        If the database and the tables support transactions, this commits the
        current transaction; otherwise this method successfully does nothing.
        """
        if self._uncommited is True:
            with Timer() as elapsed:
                try:
                    self._crsr.commit()
                except AttributeError:
                    self._conn._conn.commit()

            _log(self, "Commit", elapsed())
            self._uncommited = False

    def rollback(self):
        """Rollback Transactional Queries

        If the database and tables support transactions, this rolls back
        (cancels) the current transaction;
        otherwise a NotSupportedError is raised.
        """
        if self._uncommited is True:
            with Timer() as elapsed:
                try:
                    self._crsr.rollback()
                except AttributeError:
                    self._conn._conn.rollback()
            _log(self, "Rollback", elapsed())


    def insert(self, table, data):
        """Insert data into table.

        Args:
            table (str): Table name.
            data (list): List of rows containing values.
        """
        if data is not None:
            for row in data:
                if isinstance(row, dict):
                    query = "INSERT INTO %s (" % table
                    query += ','.join(row.keys())
                    query += ')'
                    query += ' VALUES'
                    query += ' ('
                    placeholders = []
                    for ph in range(len(row)):
                        placeholders.append('%s')
                    query += ','.join(placeholders)
                    query += ')'
                    self.execute(query, list(row.values()))
                elif isinstance(row, (list, tuple)):
                    query = "INSERT INTO %s" % table
                    query += ' VALUES'
                    query += ' ('
                    placeholders = []
                    for ph in range(len(row)):
                        placeholders.append('%s')
                    query += ','.join(placeholders)
                    query += ')'
                    self.execute(query, list(row))
                else:
                    pass
            self.commit()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()
