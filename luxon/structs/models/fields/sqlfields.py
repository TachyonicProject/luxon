# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Christiaan Frans Rademan.
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
from luxon.structs.models.fields.basefields import BaseFields
from luxon.utils.cast import to_tuple


class SQLFields(object):
    """SQL Fields outer class"""
    __slots__ = ()

    class UniqueIndex(BaseFields.BaseField):
        """Unique Index.

        UNIQUE refers to an index where all rows of the index must be unique. That
        is, the same row may not have identical non-NULL values for all columns in
        this index as another row. As well as being used to speed up queries,
        UNIQUE indexes can be used to enforce restraints on data, because the
        database system does not allow this distinct values rule to be broken when
        inserting or updating data.

        Provide arguements as individual permitted fields. These should be
        reference to another model field.

        SQLLite3 + MySQL support this functionality.
        """
        def __init__(self, *args):
            self._index = args
            super().__init__()
            self.internal = True

    class Index(BaseFields.BaseField):
        """Index.

        Indexes are used to find rows with specific column values quickly. Without
        an index, SQL must begin with the first row and then read through the
        entire table to find the relevant rows. The larger the table, the more this
        costs. If the table has an index for the columns in question, SQL can
        quickly determine the position to seek to in the middle of the data file
        without having to look at all the data. This is much faster than reading
        every row sequentially.

        Provide arguements as individual permitted fields. These should be
        reference to another model field.

        SQLLite3 + MySQL support this functionality.
        """
        def __init__(self, *args):
            self._index = args
            super().__init__()
            self.internal = True

    class ForeignKey(BaseFields.BaseField):
        """Foreign Key.

        Foreign Keys let you cross-reference related data across tables, and
        foreign key constraints, which help keep this spread-out data consistent.

        SQLLite3 + MySQL support this functionality.

        Args:
            forgein_keys (list): List values should be reference to fields within
                this model.

            reference_fields (list): List values should be reference to fields
                within the remote table in same order as per foreign_keys.

            on_delete (str): Delete action affecting foreign key row.
                default 'cascade'

            on_update (str): Update action affecting foreign key row.
                default 'cascade'

        Valid values for actions:
            * NO ACTION: Configuring "NO ACTION" means just that: when a parent key
                is modified or deleted from the database, no action is taken.
            * RESTRICT: The "RESTRICT" action means that the application is
                prohibited from deleting (for ON DELETE RESTRICT) or modifying (for
                ON UPDATE RESTRICT) a parent key if there exists one or more child
                keys mapped to it. The difference between the effect of a RESTRICT
                action and normal foreign key constraint enforcement is that the
                RESTRICT action processing happens as soon as the field is updated
                - not at the end of the current statement as it would with an
                immediate constraint, or at the end of the current transaction as
                it would with a deferred Even if the foreign key constraint it is
                attached to is deferred, configuring a RESTRICT action causes
                to return an error immediately if a parent key with dependent child
                keys is deleted or modified.
            * SET NULL: If the configured action is "SET NULL", then when a parent
                key is deleted (for ON DELETE SET NULL) or modified (for ON UPDATE
                SET NULL), the child key columns of all rows in the child table
                that mapped to the parent key are set to contain SQL NULL values.
            * SET DEFAULT: The "SET DEFAULT" actions are similar to "SET NULL",
                except that each of the child key columns is set to contain the
                columns default value instead of NULL.
            * CASCADE: A "CASCADE" action propagates the delete or update operation
                on the parent key to each dependent child key. For an "ON DELETE
                CASCADE" action, this means that each row in the child table that
                was associated with the deleted parent row is also deleted. For an
                "ON UPDATE CASCADE" action, it means that the values stored in each
                dependent child key are modified to match the new parent values.
        """
        def __init__(self, foreign_keys, reference_fields,
                     on_delete='CASCADE', on_update='CASCADE'):

            on = ['NO ACTION', 'RESTRICT', 'SET NULL', 'SET DEFAULT', 'CASCADE']
            on_delete = on_delete.upper()
            on_update = on_update.upper()

            if on_delete not in on:
                raise ValueError("Invalid on delete option" +
                                 " table '%s'" % self._table)

            if on_update not in on:
                raise ValueError("Invalid on delete option" +
                                 " table '%s'" % self._table)

            self._foreign_keys = to_tuple(foreign_keys)
            self._reference_fields = to_tuple(reference_fields)
            self._on_delete = on_delete
            self._on_update = on_update
            super().__init__()
            self.internal = True
