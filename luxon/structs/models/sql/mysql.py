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
from luxon import db


class Mysql(object):
    def __init__(self, model):
        self._model = model

    # Backup, Drop, Create, Restore.
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

                try:
                    m = model_fields[field].m
                except AttributeError:
                    m = None

                try:
                    d = model_fields[field].d
                except AttributeError:
                    d = None

                max_length = model_fields[field].max_length
                if isinstance(model_fields[field], self._model.BaseInteger):
                    max_length = len(str(max_length))

                enum = list(model_fields[field].enum)
                null = model_fields[field].null
                signed = model_fields[field].signed

                if isinstance(model_fields[field], self._model.Enum):
                    for no, val in enumerate(enum):
                        enum[no] = "'%s'" % val
                    enum = ','.join(enum)

                    sql_field = " %s enum(%s)" % (column, enum)

                elif isinstance(model_fields[field], self._model.Double):
                    if m is not None and d is not None:
                        sql_field = " %s double(%s,%s)" % (m, d)
                    else:
                        sql_field = " %s double"

                elif isinstance(model_fields[field], self._model.Float):
                    if m is not None and d is not None:
                        sql_field = " %s float(%s,%s)" % (m, d)
                    else:
                        sql_field = " %s float"

                elif isinstance(model_fields[field], self._model.Decimal):
                    if m is not None and d is not None:
                        sql_field = " %s decimal(%s,%s)" % (m, d)
                    else:
                        sql_field = " %s decimal"

                elif isinstance(model_fields[field], self._model.TinyInt):
                    if max_length is None:
                        sql_field = " %s tinyint" % column
                    else:
                        sql_field = " %s tinyint(%s)" % (column, max_length)

                    if signed is False:
                        sql_field += ' UNSIGNED'

                    if (self._model.primary_key and
                            self._model.primary_key.name == field):
                        sql_field += " auto_increment"

                elif isinstance(model_fields[field], self._model.SmallInt):
                    if max_length is None:
                        sql_field = " %s smallint" % column
                    else:
                        sql_field = " %s smallint(%s)" % (column, max_length)

                    if signed is False:
                        sql_field += ' UNSIGNED'

                    if (self._model.primary_key and
                            self._model.primary_key.name == field):
                        sql_field += " auto_increment"

                elif isinstance(model_fields[field], self._model.MediumInt):
                    if max_length is None:
                        sql_field = " %s mediumint" % column
                    else:
                        sql_field = " %s mediumint(%s)" % (column, max_length)

                    if signed is False:
                        sql_field += ' UNSIGNED'

                    if (self._model.primary_key and
                            self._model.primary_key.name == field):
                        sql_field += " auto_increment"

                elif isinstance(model_fields[field], self._model.BigInt):
                    if max_length is None:
                        sql_field = " %s bigint" % column
                    else:
                        sql_field = " %s bigint(%s)" % (column, max_length)

                    if signed is False:
                        sql_field += ' UNSIGNED'

                    if (self._model.primary_key and
                            self._model.primary_key.name == field):
                        sql_field += " auto_increment"

                elif isinstance(model_fields[field], self._model.DateTime):
                    sql_field = " %s datetime" % column

                elif isinstance(model_fields[field], self._model.Blob):
                    sql_field = " %s blob" % column

                elif isinstance(model_fields[field], self._model.TinyBlob):
                    sql_field = " %s TinyBlob" % column

                elif isinstance(model_fields[field], self._model.MediumBlob):
                    sql_field = " %s MediumBlob" % column

                elif isinstance(model_fields[field], self._model.LongBlob):
                    sql_field = " %s LongBlob" % column

                elif isinstance(model_fields[field], self._model.TinyText):
                    sql_field = " %s TinyText" % (column,)

                elif isinstance(model_fields[field], self._model.Text):
                    sql_field = " %s Text" % (column,)

                elif isinstance(model_fields[field], self._model.MediumText):
                    sql_field = " %s MediumText" % (column,)

                elif isinstance(model_fields[field], self._model.LongText):
                    sql_field = " %s LongText" % (column,)

                elif isinstance(model_fields[field], self._model.String):
                    if max_length is None:
                        max_length = '255'
                    sql_field = " %s varchar(%s)" % (column, max_length)

                elif isinstance(model_fields[field], self._model.BaseInteger):
                    if max_length is None:
                        sql_field = " %s integer" % column
                    else:
                        sql_field = " %s integer(%s)" % (column, max_length)

                    if signed is False:
                        sql_field += ' UNSIGNED'

                    if (self._model.primary_key and
                            self._model.primary_key.name == field):
                        sql_field += " auto_increment"

                if null is False:
                    sql_field += ' NOT NULL'

                if sql_field is not None:
                    sql_fields.append(sql_field)

            for field in model_fields:
                sql_field = None
                column = model_fields[field].name
                if isinstance(model_fields[field], self._model.Index):
                    index = 'INDEX'
                    index += ' `%s` (' % column
                    index_fields = []
                    for index_field in model_fields[field]._index:
                        index_fields.append('`%s`' % index_field.name)
                    index += ",".join(index_fields)
                    index += ')'
                    sql_field = index

                elif isinstance(model_fields[field], self._model.UniqueIndex):
                    index = 'UNIQUE KEY'
                    index += ' `%s` (' % column
                    index_fields = []
                    for index_field in model_fields[field]._index:
                        index_fields.append('`%s`' % index_field.name)
                    index += ",".join(index_fields)
                    index += ')'
                    sql_field = index

                elif isinstance(model_fields[field], self._model.ForeignKey):
                    foreign_keys = []
                    references = []
                    ref_name = model_fields[field]._reference_fields[0]._table

                    for fk in model_fields[field]._foreign_keys:
                        foreign_keys.append('`' + fk.name + '`')
                    foreign_keys = ",".join(foreign_keys)

                    for ref in model_fields[field]._reference_fields:
                        references.append('`' + ref.name + '`')
                    references = ",".join(references)

                    index = 'CONSTRAINT `%s`' % column
                    index += ' FOREIGN KEY (%s)' % foreign_keys
                    index += ' REFERENCES `%s`' % ref_name
                    index += ' (%s)' % references
                    index += ' ON DELETE %s' % model_fields[field]._on_delete
                    index += ' ON UPDATE %s' % model_fields[field]._on_update
                    sql_field = index

                if sql_field is not None:
                    sql_fields.append(sql_field)

            create += ",".join(sql_fields)
            create += ' ,PRIMARY KEY (`%s`)' % self._model.primary_key.name
            create += ')'
            create += ' ENGINE=%s CHARSET=%s;' \
                % (self._model.db_engine, self._model.db_charset,)
            conn.execute(create)
