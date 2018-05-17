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
from luxon import db
from luxon.structs.models.model import Model
from luxon.structs.models.fields.sqlfields import SQLFields
from luxon import exceptions
from luxon.utils.imports import get_class


class SQLModel(Model, SQLFields):
    db_engine = 'innodb'
    db_charset = 'UTF8'
    db_default_rows = []
    filter_fields = (SQLFields.ForeignKey, SQLFields.Index,
                     SQLFields.UniqueIndex, )

    __slots__ = ()

    def _sql_parse(self, result):
        if len(result) > 0:
            if len(result) > 1:
                muerr = "Multiple rows for model"
                muerr += " '%s' returned" % self.model_name
                raise exceptions.MultipleOblectsReturned(muerr)
            row = result[0]
            for field in row.keys():
                if row[field] is not None:
                    val = self.fields[field]._parse(row[field])
                    self._current[field] = val
            self._created = False
            self._updated = False
            self._new.clear()

    def sql_query(self, query, values=None):
        with db() as conn:
            crsr = conn.execute(query, values)
            result = crsr.fetchall()
            crsr.commit()
            self._sql_parse(result)

    def sql_id(self, primary_id):
        with db() as conn:
            if self.primary_key is None:
                raise KeyError("Model %s:" % self.model_name +
                               " No primary key") from None

            crsr = conn.execute("SELECT * FROM %s" % self.model_name +
                                " WHERE %s" % self.primary_key.name +
                                " = %s",
                                primary_id)
            result = crsr.fetchall()
            crsr.commit()
            self._sql_parse(result)

    def commit(self):
        name = self.model_name

        if self.primary_key is None:
            raise KeyError("Model %s:" % name +
                           " No primary key") from None

        key_id = self.primary_key.name

        transaction = self._pre_commit()[1]

        try:
            conn = db()
            for field in self.fields:
                if isinstance(self.fields[field], SQLModel.UniqueIndex):
                    index_fields = []
                    index_values = []
                    query = "SELECT count(*) as no FROM %s WHERE " % name
                    if key_id in self._transaction:
                        query += " %s != " % key_id
                        query += "%s AND "
                        index_values.append(self._transaction[key_id])
                    for index_field in self.fields[field]._index:
                        if index_field.name in self._transaction:
                            index_fields.append(index_field.name + ' = %s')
                            index_values.append(
                                self._transaction[index_field.name])
                    query += ' AND '.join(index_fields)
                    crsr = conn.execute(query, index_values)
                    res = crsr.fetchone()
                    if res['no'] > 0:
                        raise exceptions.ValidationError(
                            "Model %s:" % name +
                            " Duplicate Entry") from None
                if isinstance(self.fields[field], SQLModel.ForeignKey):
                    fk = self.fields[field]
                    if (fk._on_update == 'NO ACTION' or
                            fk._on_update == 'RESTRICT'):
                        for no, fk_field in enumerate(
                                self.fields[field]._foreign_keys):
                            if fk_field.name in self._transaction:
                                ref = fk_field._reference_fields[no]
                                index_fields.append(ref.name + ' = %s')
                                index_values.append(
                                    self._transaction[fk_field.name])
                                table = self._transaction[fk_field._table]

                        query = "SELECT count(*) as no FROM %s WHERE " % table
                        query += ' AND '.join(index_fields)
                        crsr = conn.execute(query, index_values)
                        if res['no'] > 0:
                            raise exceptions.ValidationError(
                                "Model %s:" % name +
                                " Object referenced.") from None

            if self._created:
                query = "INSERT INTO %s (" % name
                query += ','.join(transaction.keys())
                query += ')'
                query += ' VALUES'
                query += ' ('
                placeholders = []
                for ph in range(len(transaction)):
                    placeholders.append('%s')
                query += ','.join(placeholders)
                query += ')'
                conn.execute(query, list(transaction.values()))
                if isinstance(self.primary_key, SQLModel.Integer):
                    self[self.primary_key.name] = conn.last_row_id()
                conn.commit()

            elif self._updated:
                update_id = transaction[key_id]
                sets = []
                args = []
                for field in self._new:
                    if self.primary_key.name != field:
                        if self.fields[field].readonly:
                            self._new[field].error('readonly value')
                        if self.fields[field].db:
                            sets.append('%s' % field +
                                        ' = %s')
                            args.append(self._new[field])

                if len(sets) > 0:
                    sets = ", ".join(sets)
                    conn.execute('UPDATE %s' % name +
                                 ' SET %s' % sets +
                                 ' WHERE %s' % key_id +
                                 ' = %s',
                                 args + [update_id, ])
        finally:
            conn.commit()
            conn.close()

        self._current = self._transaction
        self._new.clear()
        self._created = False
        self._updated = False

    @classmethod
    def create_table(cls):
        if cls.primary_key is None:
            raise KeyError("Model %s:" % cls.name +
                           " No primary key") from None

        api = g.app.config.get('database', 'type')
        driver_cls = api.title()
        driver = get_class('luxon.structs.models.sql.%s:%s' %
                           (api, driver_cls,))(cls)
        driver.create()
