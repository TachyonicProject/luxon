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
from luxon import db


class Sqlite3(object):
    def __init__(self, model):
        self._model = model

    # Create Tables
    def create(self):
        name = self._model.model_name
        model_fields = self._model.fields

        with db() as conn:
            if conn.has_table(name):
                # NOTE(cfrademan): Drop exisiting name..
                conn.execute("DROP TABLE %s" % name)

            # NOTE(cfrademan): We need to create the name..
            create = 'CREATE TABLE `%s` (' % name
            sql_fields = []
            for field in model_fields:
                sql_field = None

                column = model_fields[field].name
                null = model_fields[field].null
                signed = model_fields[field].signed

                if isinstance(model_fields[field], self._model.BaseText):
                    sql_field = " %s TEXT" % column

                elif isinstance(model_fields[field], self._model.Float):
                    sql_field = " %s REAL" % column

                elif isinstance(model_fields[field], self._model.Decimal):
                    sql_field = " %s REAL" % column

                elif isinstance(model_fields[field], self._model.Enum):
                    sql_field = " %s TEXT" % column

                elif isinstance(model_fields[field], self._model.String):
                    sql_field = " %s TEXT" % column

                elif isinstance(model_fields[field], self._model.BaseInteger):
                    sql_field = " %s INTEGER" % column

                    if signed is False:
                        sql_field += ' UNSIGNED'

                elif isinstance(model_fields[field], self._model.DateTime):
                    sql_field = " %s TIMESTAMP" % column

                elif isinstance(model_fields[field], self._model.BaseBlob):
                    sql_field = " %s BLOB" % column

                if null is False:
                    sql_field += ' NOT NULL'

                if (self._model.primary_key and
                        self._model.primary_key.name == column):
                    sql_field += ' PRIMARY KEY'

                if sql_field is not None:
                    sql_fields.append(sql_field)

            for field in model_fields:
                sql_field = None

                column = model_fields[field].name

                if isinstance(model_fields[field], self._model.ForeignKey):
                    foreign_keys = []
                    references = []
                    ref_name = model_fields[field]._reference_fields[0]._table

                    for fk in model_fields[field]._foreign_keys:
                        foreign_keys.append('`' + fk.name + '`')
                    foreign_keys = ",".join(foreign_keys)

                    for ref in model_fields[field]._reference_fields:
                        references.append('`' + ref.name + '`')
                    references = ",".join(references)

                    index = ' FOREIGN KEY (%s)' % foreign_keys
                    index += ' REFERENCES %s' % ref_name
                    index += '(%s)' % references
                    index += ' ON DELETE %s' % model_fields[field]._on_delete
                    index += ' ON UPDATE %s' % model_fields[field]._on_update
                    sql_field = index

                if sql_field is not None:
                    sql_fields.append(sql_field)

            create += ",".join(sql_fields)
            create += ')'
            conn.execute(create)
            conn.commit()

            for field in model_fields:
                if isinstance(model_fields[field], self._model.UniqueIndex):
                    index = 'CREATE UNIQUE INDEX'
                    index += ' %s on %s (' % (field, name,)
                    index_fields = []
                    for index_field in model_fields[field]._index:
                        index_fields.append('%s' % index_field.name)
                    index += ",".join(index_fields)
                    index += ')'
                    conn.execute(index)
                    conn.commit()
