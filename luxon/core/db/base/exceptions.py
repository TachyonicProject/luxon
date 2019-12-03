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
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTI-
# TUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUP-
# TION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY,OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
from luxon import exceptions


class Error(exceptions.SQLError):
    """Exception related to operation with MySQL."""


class Warning(exceptions.SQLWarning):
    """Exception raised for important warnings like data truncations
    while inserting, etc."""


class InterfaceError(exceptions.SQLInterfaceError):
    """Exception raised for errors that are related to the database
    interface rather than the database itself."""


class DatabaseError(exceptions.SQLDatabaseError):
    """Exception raised for errors that are related to the
    database."""


class DataError(exceptions.SQLDataError):
    """Exception raised for errors that are due to problems with the
    processed data like division by zero, numeric value out of range,
    etc."""


class OperationalError(exceptions.SQLOperationalError):
    """Exception raised for errors that are related to the database's
    operation and not necessarily under the control of the programmer,
    e.g. an unexpected disconnect occurs, the data source name is not
    found, a transaction could not be processed, a memory allocation
    error occurred during processing, etc."""


class IntegrityError(exceptions.SQLIntegrityError):
    """Exception raised when the relational integrity of the database
    is affected, e.g. a foreign key check fails, duplicate key,
    etc."""


class InternalError(exceptions.SQLInternalError):
    """Exception raised when the database encounters an internal
    error, e.g. the cursor is not valid anymore, the transaction is
    out of sync, etc."""


class ProgrammingError(exceptions.SQLProgrammingError):
    """Exception raised for programming errors, e.g. table not found
    or already exists, syntax error in the SQL statement, wrong number
    of parameters specified, etc."""


class NotSupportedError(exceptions.SQLNotSupportedError):
    """Exception raised in case a method or database API was used
    which is not supported by the database, e.g. requesting a
    .rollback() on a connection that does not support transaction or
    has transactions turned off."""


class Exceptions(object):
    def _error_handler(self, obj, e, error_map):
        for error_mapping in error_map:
            exception, local = error_mapping
            if isinstance(e, exception):
                local = getattr(obj, local)
                raise local(e) from None
        raise

    class Error(Error):
        """Exception related to operation with MySQL."""

    class Warning(Warning):
        """Exception raised for important warnings like data truncations
        while inserting, etc."""

    class InterfaceError(InterfaceError):
        """Exception raised for errors that are related to the database
        interface rather than the database itself."""

    class DatabaseError(DatabaseError):
        """Exception raised for errors that are related to the
        database."""

    class DataError(DataError):
        """Exception raised for errors that are due to problems with the
        processed data like division by zero, numeric value out of range,
        etc."""

    class OperationalError(OperationalError):
        """Exception raised for errors that are related to the database's
        operation and not necessarily under the control of the programmer,
        e.g. an unexpected disconnect occurs, the data source name is not
        found, a transaction could not be processed, a memory allocation
        error occurred during processing, etc."""

    class IntegrityError(IntegrityError):
        """Exception raised when the relational integrity of the database
        is affected, e.g. a foreign key check fails, duplicate key,
        etc."""

    class InternalError(InternalError):
        """Exception raised when the database encounters an internal
        error, e.g. the cursor is not valid anymore, the transaction is
        out of sync, etc."""

    class ProgrammingError(ProgrammingError):
        """Exception raised for programming errors, e.g. table not found
        or already exists, syntax error in the SQL statement, wrong number
        of parameters specified, etc."""

    class NotSupportedError(NotSupportedError):
        """Exception raised in case a method or database API was used
        which is not supported by the database, e.g. requesting a
        .rollback() on a connection that does not support transaction or
        has transactions turned off."""
