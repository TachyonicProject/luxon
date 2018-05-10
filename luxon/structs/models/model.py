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
from collections import OrderedDict

from luxon import g
from luxon.exceptions import ValidationError
from luxon import db
from luxon import js
from luxon.utils.imports import get_class
from luxon.utils.classproperty import classproperty
from luxon.structs.models.fields import (BaseField,
                                         Integer,
                                         parse_defaults,
                                         ForeignKey,
                                         Index,
                                         UniqueIndex,
                                         Confirm,)
from luxon.utils.cast import to_tuple

class Model(object):
    _fields = None
    primary_key = None
    filter_fields = ( ForeignKey, Index, UniqueIndex, )

    __slots__ = ( '_current', '_new', '_updated', '_created', '_hide' )

    def __init__(self, model=list, hide=None):
        if model != list and model != dict:
            raise ValueError("Invalid model type '%s'" % model)

        self._current = model()
        self._new = model()
        self._updated = False
        self._created = True
        self._hide = to_tuple(hide)

        if isinstance(self._current, dict):
            # NOTE(cfrademan): Set default values for model object.
            for field in self.fields:
                default = self.fields[field].default
                if default is not None:
                    default = parse_defaults(default)
                    default = self.fields[field]._parse(default)
                    if (field not in self._transaction or
                            self._transaction[field] is None):
                        self._current[field] = default
                elif field in ('domain', 'tenant_id',):
                    self._new[field] = getattr(g.current_request.token, field)
                elif not isinstance(self.fields[field], Model.filter_fields):
                    self._current[field] = None

    def __getitem__(self, key):
        if isinstance(self._current, dict):
            if key not in self.fields:
                raise KeyError("Model %s:" % self.model_name +
                               " No such field '%s'" % key) from None
        try:
            return self._transaction[key]
        except KeyError:
            return None
        except IndexError:
            raise IndexError("Model %s:" % self.model_name +
                             " No such key '%s'" % key) from None

    def __setitem__(self, key, value):
        if isinstance(self._current, dict):
            try:
                if (self.fields[key].readonly is True and
                        self._transaction[key] is not None):
                    raise ValidationError("Model %s:" % self.model_name +
                                   " readonly field '%s'" % key) from None
            except KeyError:
                raise ValidationError("Model %s:" % self.model_name +
                               " No such field '%s'" % key) from None

            if key in ('domain_id', 'tenant_id',):
                raise ValidationError("Model %s:" % self.model_name +
                               " readonly field '%s'" % key) from None
            if self.fields[key].internal is True:
                raise ValidationError("Model %s:" % self.model_name +
                               " Internal only field '%s'" % key) from None

            if (self.primary_key is not None and
                        self[key] is not None and
                        key == self.primary_key.name):
                    raise ValueError("Model %s:" % self.model_name +
                                     " Cannot alter primary key '%s'"
                                     % key) from None

            if ((value is None and self.fields[key].ignore_null is not True) or
                    value is not None):
                self._new[key] = self.fields[key]._parse(value)
            self._updated = True
        else:
            raise NotImplementedError()

    def __delitem__(self, key):
        raise NotImplementedError()

    def __iter__(self):
        return iter(self.transaction)

    def __str__(self):
        return str(self.transaction)

    def __repr__(self):
        return repr(self.transaction)

    def __len__(self):
        return len(self._transaction)

    @property
    def transaction(self):
        """Return current state.
        """
        if isinstance(self._current, list):
            return self._current + self._new
        elif isinstance(self._current, dict):
            transaction = {**self._current, **self._new}
            for field in transaction.copy():
                if isinstance(self.fields[field], Confirm):
                    del transaction[field]
                if field in self._hide:
                    del transaction[field]
            return transaction

    @property
    def _transaction(self):
        """Return current state.
        """
        if isinstance(self._current, list):
            return self._current + self._new
        elif isinstance(self._current, dict):
            return {**self._current, **self._new}

    @classproperty
    def model_name(cls):
        return cls.__name__.split('.')[-1]

    @classproperty
    def fields(cls):
        if cls._fields is None:
            ignore = ('primary_key', 'fields')
            current_fields = []

            for name in dir(cls):
                if name not in ignore:
                    # NOTE(cfrademan): Hack, dir() shows '__slots__', so it breaks if
                    # attribue is not there while doing getattr. once again, its faster
                    # to ask for forgiveness than permission.
                    try:
                        prop = getattr(cls, name)
                    except AttributeError:
                        prop = None

                    if isinstance(prop, BaseField):
                        current_fields.append((name, prop))
                        prop._table = cls.model_name
                        prop._field_name = name

            current_fields.sort(key=lambda x: x[1]._creation_counter)

            cls._fields = OrderedDict(current_fields)

        return cls._fields

    @property
    def json(self):
        """Return as serialized JSON.
        """
        return js.dumps(self.transaction)

    @property
    def dict(self):
        """Return as raw dict.
        """
        return self._transaction.copy()

    def rollback(self):
        """Rollback.

        Rollback to previous state before commit.
        """
        self._new.clear()

        if isinstance(self._current, list):
            for model in self._transaction:
                model.rollback()

        self._created = False
        self._updated = False

    def _pre_commit(self):
        transaction = {}

        for field in self.fields:
            if field not in self._new:
                on_update = self.fields[field].on_update

                if on_update is not None and self._updated:
                    on_update = parse_defaults(on_update)
                    on_update = self.fields[field]._parse(on_update)
                    self._new[field] = on_update

            if (self.fields[field].null is False and
                    (field not in self._transaction or
                     self._transaction[field] is None)):
                self.fields[field].error('required')

            if isinstance(self.fields[field], Confirm):
                confirm_field = self.fields[field].field.name
                value1 = self._transaction.get(confirm_field)
                value2 = self._transaction.get(field)
                if value1 != value2:
                    raise Exception('boom')

            elif (field in self._transaction and
                    self.fields[field].db):
                transaction[field] = self._transaction[field]

        return (self._transaction, transaction,)

    def commit(self):
        """Commit transaction.
        """
        if (isinstance(self._current, dict)):
            self._current = self._pre_commit()[0]
        else:
            self._current = self._transaction

        self._created = False
        self._updated = False

        if isinstance(self._current, list):
            for model in self._transaction:
                model.commit()

    def new(self):
        """Create new row.

        Creates a new row and returns row model.
        """
        if isinstance(self._current, list):
            NewModel = type(self.model_name, (self.__class__,), {})
            NewModel._sql = self._sql
            NewModel.primary_key = self.primary_key
            NewModel._fields = self.fields
            model = NewModel(model=dict, hide=self._hide)
            self._new.append(model)
            self._created = True
            return model
        else:
            raise NotImplementedError()

    def update(self, obj):
        """Update Models.

        Append (list) or Update (obj) object to columns.

        Args:
            obj (list/dict): List / Dict Object.
        """
        if isinstance(self._current, list):
            for row in obj:
                new = self.new()
                for column in row:
                    new[column] = row[column]
        else:
            for column in obj:
                self[column] = obj[column]
