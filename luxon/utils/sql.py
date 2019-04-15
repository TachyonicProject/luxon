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
import re

from luxon.utils.text import join
from luxon.utils.cast import to_list

AS_FIELD = re.compile(r'^(?P<orig>.+) AS[ ]+(?P<field>[a-z0-9_]+)$',
                      re.IGNORECASE)
P_FIELD = re.compile(r'^.+\(+(?P<field>[a-z0-9_\.]+)\)+$')


def get_field(value):
    value = str(value)
    as_field = AS_FIELD.match(value)
    if as_field:
        return as_field.group('orig'), as_field.group('field')

    p_field = P_FIELD.match(value)
    if p_field:
        field = p_field.group('field')
        if '.' in field:
            field = field.split('.')[1]
    else:
        if '.' in value:
            field = value.split('.')[1]
        else:
            field = None

    return value, field


class BaseQuery(object):
    OR = 'OR'
    AND = 'AND'

    def __init__(self):
        self._prefix = ()
        self._query = []
        self._query_order = []
        self._suffix = ()
        self._append = []
        self._values = []

    def __str__(self):
        return self.query

    def __repr__(self):
        return repr(self.query)

    def __iter__(self):
        if self._query:
            return iter((*self._prefix, *self._query, *self._suffix,
                         *self._append,))
        elif self._append:
            return iter((*self._append,))

        return iter(())

    @property
    def query(self):
        return join(self)

    @property
    def values(self):
        return self._values


class And(BaseQuery):
    def __init__(self, *conditions):
        if len(conditions) == 0:
            raise ValueError('sql And requires conditions')
        super().__init__()
        for condition in conditions:
            if self._append:
                self._append += [condition.AND, *condition]
                self._query_order += [',', *condition._query_order]
            else:
                self._append += condition
                self._query_order += condition._query_order

            self._values += condition._values


class Or(BaseQuery):
    def __init__(self, *conditions):
        if len(conditions) == 0:
            raise ValueError('sql Or requires conditions')
        super().__init__()
        for condition in conditions:
            if self._append:
                self._append += [condition.OR, *condition]
            else:
                self._append += condition

            self._values += condition._values


class BaseCompare(BaseQuery):
    class Condition(BaseQuery):
        def __init__(self, query, values=[]):
            super().__init__()
            self._query = query
            self._values = values

    def __eq__(self, other):
        if isinstance(other, Value) and other._values[0] is None:
            query = self._query + ['IS NULL']
            return BaseCompare.Condition(query)
        else:
            query = self._query[:1] + ['='] + other._query[:1]
            if isinstance(other, Value):
                values = other._values[:1]
                return BaseCompare.Condition(query, values)
            elif isinstance(self, Value):
                values = self._values[:1]
                return BaseCompare.Condition(query, values)
            else:
                return BaseCompare.Condition(query)

    def __ne__(self, other):
        if isinstance(other, Value) and other._values[0] is None:
            query = self._query + ['IS NULL']
            return BaseCompare.Condition(query)
        else:
            query = self._query[:1] + ['!='] + other._query[:1]
            if isinstance(other, Value):
                values = other._values[:1]
                return BaseCompare.Condition(query, values)
            elif isinstance(self, Value):
                values = self._values[:1]
                return BaseCompare.Condition(query, values)
            else:
                return BaseCompare.Condition(query)

    def __gt__(self, other):
        if isinstance(other, Value) and other._values[0] is None:
            query = self._query + ['IS NULL']
            return BaseCompare.Condition(query)
        else:
            query = self._query[:1] + ['>'] + other._query[:1]
            if isinstance(other, Value):
                values = other._values[:1]
                return BaseCompare.Condition(query, values)
            elif isinstance(self, Value):
                values = self._values[:1]
                return BaseCompare.Condition(query, values)
            else:
                return BaseCompare.Condition(query)

    def __ge__(self, other):
        if isinstance(other, Value) and other._values[0] is None:
            query = self._query + ['IS NULL']
            return BaseCompare.Condition(query)
        else:
            query = self._query[:1] + ['>='] + other._query[:1]
            if isinstance(other, Value):
                values = other._values[:1]
                return BaseCompare.Condition(query, values)
            elif isinstance(self, Value):
                values = self._values[:1]
                return BaseCompare.Condition(query, values)
            else:
                return BaseCompare.Condition(query)

    def __lt__(self, other):
        if isinstance(other, Value) and other._values[0] is None:
            query = self._query + ['IS NULL']
            return BaseCompare.Condition(query)
        else:
            query = self._query[:1] + ['<'] + other._query[:1]
            if isinstance(other, Value):
                values = other._values[:1]
                return BaseCompare.Condition(query, values)
            elif isinstance(self, Value):
                values = self._values[:1]
                return BaseCompare.Condition(query, values)
            else:
                return BaseCompare.Condition(query)

    def __le__(self, other):
        if isinstance(other, Value) and other._values[0] is None:
            query = self._query + ['IS NULL']
            return BaseCompare.Condition(query)
        else:
            query = self._query[:1] + ['<='] + other._query[:1]
            if isinstance(other, Value):
                values = other._values[:1]
                return BaseCompare.Condition(query, values)
            elif isinstance(self, Value):
                values = self._values[:1]
                return BaseCompare.Condition(query, values)
            else:
                return BaseCompare.Condition(query)

    def __xor__(self, other):
        if isinstance(other, Value) and other._values[0] is None:
            query = self._query + ['IS NULL']
            return BaseCompare.Condition(query)
        elif isinstance(other, Value):
            query = self._query[:1] + ['LIKE'] + other._query[:1]
            try:
                values = [other._values[0] + '%']
            except (ValueError, TypeError):
                values = [other._values[0]]
            return BaseCompare.Condition(query, values)
        else:
            raise ValueError('sql select invalid like condition')


class LeftJoin(BaseQuery):
    def __init__(self, table, *on):
        if len(on) == 0:
            raise ValueError('sql Left Join requires condition')
        super().__init__()
        self._query = ["LEFT JOIN", table, 'ON']
        for condition in on:
            self._query += [*condition]
            self._values += condition.values


class RightJoin(BaseQuery):
    def __init__(self, table, *on):
        if len(on) == 0:
            raise ValueError('sql Right Join requires condition')
        super().__init__()
        self._query = ["RIGHT JOIN", table, 'ON']
        for condition in on:
            self._query += [*condition]
            self._values += condition.values


class InnerJoin(BaseQuery):
    def __init__(self, table, *on):
        if len(on) == 0:
            raise ValueError('sql Inner Join requires condition')
        super().__init__()
        self._query = ["INNER JOIN", table, 'ON']
        for condition in on:
            self._query += [*condition]
            self._values += condition.values


def _parse_sort(sort):
    if sort == '>':
        return 'desc'
    elif sort == '<':
        return 'asc'
    else:
        raise ValueError("sql Invalid sort '%s' for select" % sort)


class Field(BaseCompare):
    def __init__(self, column, sort='>'):
        super().__init__()
        self._column = column
        self._query.append(column)
        sort = _parse_sort(sort)
        field, as_field = get_field(column)
        if as_field:
            self._name = as_field
        else:
            self._name = field

        self._query_order = [field, sort]

    def __call__(self, sort='>'):
        sort = _parse_sort(sort)
        field, as_field = get_field(self._column)
        self._query_order = [field, sort]
        return self

    @property
    def name(self):
        return self._name


class Value(BaseCompare):
    def __init__(self, value):
        super().__init__()
        self._query.append('%s')
        self._values.append(value)


class Group(BaseQuery):
    def __init__(self, grouped=None):
        super().__init__()
        if isinstance(grouped, (Or,
                                And,
                                BaseCompare.Condition,)):
            self._prefix = ['(']
            if grouped:
                self._query = [grouped]
                self._values += grouped.values
            self._suffix = [')']
        else:
            raise ValueError('sql Group expects condition')


class Limit(BaseQuery):
    def __init__(self, start, limit):
        super().__init__()
        self._query = ('LIMIT', "%s,%s" % (start, limit,),)


class Select(object):
    def __init__(self, table, distinct=False):
        super().__init__()
        self._table = table
        self._joins = []
        self._where = []
        self._limit = ()
        self._group = []
        self._order = []
        self._fields = []
        self._dupfields = []
        if distinct:
            self._distinct = ('DISTINCT',)
        else:
            self._distinct = ()

    def left_join(self, table, *on):
        join = LeftJoin(table, *on)
        self._joins.append(join)
        return join

    def right_join(self, table, *on):
        join = RightJoin(table, *on)
        self._joins.append(join)
        return join

    def inner_join(self, table, *on):
        join = InnerJoin(table, *on)
        self._joins.append(join)
        return join

    def limit(self, start, limit):
        self._limit = Limit(start, limit)

    @property
    def fields(self):
        if self._fields:
            return self._fields
        else:
            return ['*']

    @fields.setter
    def fields(self, fields):
        parsed = []

        def add_field(field):
            field, as_field = get_field(field)

            value = ''
            if self._fields or parsed:
                value += ', '
            if as_field:
                value += field + ' AS ' + as_field
                name = as_field
            else:
                name = field
                value += field

            if name not in self._dupfields:
                self._dupfields.append(name)
                return value
            else:
                return None

        fields = to_list(fields)
        for field in fields:
            field = add_field(field)
            if field:
                parsed.append(field)

        self._fields += parsed

    @property
    def group_by(self):
        if self._group:
            return tuple(['GROUP BY'] + self._group)
        else:
            return ()

    @group_by.setter
    def group_by(self, fields):
        parsed = []

        if isinstance(fields, (tuple, list,)):
            for field in fields:
                if self._group or parsed:
                    parsed.append(',')
                parsed.append(field)
        else:
            if self._group:
                parsed.append(',')
            parsed.append(fields)

        self._group += parsed

    @property
    def order_by(self):
        if self._order:
            return tuple(['ORDER BY'] + self._order)
        else:
            return ()

    @order_by.setter
    def order_by(self, fields):
        parsed = []

        if isinstance(fields, (tuple, list,)):
            for field in fields:
                if self._order or parsed:
                    parsed.append(',')
                parsed += field._query_order
        else:
            if self._order:
                parsed.append(',')
            parsed += fields._query_order

        self._order += parsed

    @property
    def where(self):
        if self._where:
            return tuple(['WHERE'] + self._where)
        else:
            return ()

    @where.setter
    def where(self, conditions):
        parsed = []

        if isinstance(conditions, (tuple, list,)):
            for condition in conditions:
                if ((self._where or parsed) and condition._query):
                    parsed.append('AND')
                parsed += [condition]
        else:
            if (self._where and conditions._query):
                parsed.append('AND')
            parsed += [conditions]

        self._where += parsed

    @property
    def query(self):
        query = ("SELECT",
                 *self._distinct,
                 *self.fields,
                 "FROM",
                 self._table,
                 *self._joins,
                 *self.where,
                 *self.group_by,
                 *self.order_by,
                 *self._limit,)
        return join(query)

    @property
    def values(self):
        values = []
        for table_join in self._joins:
            values += [*table_join._values]
        for conditions in self._where:
            if isinstance(conditions, (Group, BaseCompare.Condition, Or, And)):
                values += conditions._values
        return values

    def __str__(self):
        return self.query

    def __repr__(self):
        return repr(" ".join(self.query))


def build_where(operator='AND', **kwargs):
    """Generates an SQL WHERE string.

    Will replace None's with IS NULL's.

    Keyword Args:
       Containing SQL search string
       Eg: ``{"foo": 1, "bar": None}``

    Returns:
        Tuple containing string that can
        be used after WHERE in SQL statement,
        along with a list of the values.
        Eg. ("foo=? AND bar IS NULL", [ 1 ])

    """
    vals = []
    query = []
    for k in kwargs:
        if kwargs[k] is None:
            query.append(k + " IS NULL")
        else:
            query.append(k + " = ?")
            vals.append(kwargs[k])

    if query:
        return ((" %s " % operator).join(query), vals)
    else:
        return (None, [])


def build_like(operator="AND", **kwargs):
    """Generates an SQL WHERE string.

    Will replace None's with IS NULL's.

    Keyword Args:
       Containing SQL search string
       Eg: ``{"foo": "x", "bar": None}``

    Returns:
        Tuple containing string that can
        be used after LIKE in SQL statement,
        along with a list of the values.
        Eg. ("foo like ? AND bar IS NULL", [ "x%" ])

    """
    vals = []
    query = []
    for k in kwargs:
        if kwargs[k] is None:
            query.append(k + " IS NULL")
        else:
            query.append(k + " LIKE ?")
            vals.append(kwargs[k] + '%')

    if query:
        return ((" %s " % operator).join(query), vals)
    else:
        return (None, [])
