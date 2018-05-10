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
import uuid
from datetime import datetime as py_datetime
from decimal import Decimal as PyDecimal

import phonenumbers

from luxon.utils.global_counter import global_counter
from luxon.utils.cast import to_tuple
from luxon.utils.encoding import if_bytes_to_unicode
from luxon.exceptions import FieldError
from luxon.utils.timezone import to_utc
from luxon.utils.timezone import TimezoneUTC
from luxon.core.regex import (EMAIL_RE,
                              WORD_RE,
                              USERNAME_RE,
                              URI_RE,
                              FQDN_RE,
                              IP4_RE,
                              IP6_RE,
                              IP4_PREFIX_RE,
                              IP6_PREFIX_RE)


def parse_defaults(value):
    if hasattr(value, '__call__'):
        value = value()

    if isinstance(value, str):
        value = "'" + value + "'"
    elif isinstance(value, bool):
        if value is True or value == 1:
            value = 1
        else:
            value = 0

    return value


def defined_length_check(user_min_length, user_max_length, min_length,
                         max_length):
    """Validate user defined lengths for field.

    Returns:
        Valid minimum length and maximum length as a tuple
    """
    if user_min_length is None:
        user_min_length = min_length

    if user_max_length is None:
        user_max_length = max_length

    if user_min_length < min_length:
        raise ValueError("Define Valid Minimum Lenght")
    if user_max_length > max_length:
        raise ValueError("Define Valid Maximum Lenght")

    return (min_length, max_length)


class BaseField(object):
    """Field Class.

    Provides abstractions for most common database data types.

    Keyword Args:
        length (int): Length of field value.
        min_length (int): Minimum Length of field value.
        max_length (int): Maximum Length of field value others length value.
        signed (bool): If Integer value is signed or un-signed.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Whether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Whether field can be updated.
        prefix (str): Text placed in front of field input.
        suffix (str): Text placed after field input.
        columns (int): Number of columns to display for text field.
        hidden (bool): To hide field from forms.
        enum (list): List of possible values. Only for ENUM.
    """
    __slots__ = ('length', 'min_length', 'max_length', 'null', 'default',
                 'db', 'label', 'placeholder', 'readonly', 'prefix',
                 'suffix', 'columns' ,'hidden', 'enum', '_field_name', '_table',
                 '_value', '_creation_counter', 'm', 'd', 'on_update',
                 'password', 'signed', 'ignore_null')

    def __init__(self, length=None, min_length=None, max_length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False,
                 signed=True, internal=False, ignore_null=False):
        self._creation_counter = global_counter()
        self._value = None

        self.length = length
        self.min_length = min_length
        if max_length is None:
            self.max_length = length
        else:
            self.max_length = max_length
        self.signed = signed
        self.null = null
        self.default = default
        self.on_update = on_update
        self.db = db
        self.label = label
        self.placeholder = placeholder
        self.readonly = readonly
        self.prefix = prefix
        self.suffix = suffix
        self.columns = columns
        self.hidden = hidden
        self.enum = enum
        self.password = password
        self.internal = internal
        self.ignore_null = False

    @property
    def name(self):
        return self._field_name

    def error(self, msg, value=None):
        raise FieldError(self.name, self.label, msg, value)

    def parse(self, value):
        if self.null is False and (value is None or str(value).strip() == ''):
            self.error('Empty field value (required)', value)

        if isinstance(value, (int, float, PyDecimal,)):
            if self.min_length is not None and value < self.min_length:
                self.error("Minimum value '%s'" % self.min_length, value)
            if self.max_length is not None and value > self.max_length:
                self.error("Exceeded max value '%s'" % self.max_length, value)
        elif hasattr(value, '__len__'):
            if self.min_length is not None and len(value) < self.min_length:
                self.error("Minimum length '%s'" % self.min_length, value)
            if self.max_length is not None and len(value) > self.max_length:
                self.error("Exceeded max length '%s'" % self.max_length, value)

        return value

    def _parse(self, value):
        if value is not None:
            return self.parse(value)


class Confirm(BaseField):
    def __init__(self, field):
        self.field = field
        super().__init__()
        self.db = False
        self.min_length = self.field.min_length
        self.max_length = self.field.max_length
        self.length = self.field.length
        self.readonly = self.field.readonly
        self.password = self.field.password

    def parse(self, value):
        return self.field.parse(value)


class String(BaseField):
    """String Field.

    Keyword Args:
        length (int): Length of field value.
        min_length (int): Minimum Length of field value.
        max_length (int): Maximum Length of field value others length value.
        columns (int): Number of columns to display for text field.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Whether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Whether field can be updated.
        prefix (str): Text placed in front of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """
    def parse(self, value):
        value = if_bytes_to_unicode(value)
        if not isinstance(value, str):
            self.error('Text/String value required) %s' % value, value)
        value = super().parse(value)
        return value


class Integer(BaseField):
    """Integer Field.

    4 Octet Integer
    Minimum value -2147483648
    Maximum value 2147483647

    Keyword Args:
        length (int): Length of field value.
        min_length (int): Minimum Length of field value.
        max_length (int): Maximum Length of field value others length value.
        signed (bool): If Integer value is signed or un-signed.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Whether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Whether field can be updated.
        prefix (str): Text placed in front of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """

    def __init__(self, length=None, min_length=None, max_length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False,
                 signed=True):

        try:
            min_length, max_length = defined_length_check(min_length,
                                                          max_length,
                                                          -2147483648,
                                                          2147483647)
        except ValueError as e:
            self.error(e)

        super().__init__(length=None,
                         min_length=min_length, max_length=max_length,
                         null=True, default=None, db=True, label=None,
                         placeholder=None, readonly=False, prefix=None,
                         suffix=None, columns=None, hidden=False,
                         enum=[], on_update=None, password=False)

    def parse(self, value):
        try:
            value = int(value)
        except ValueError:
            self.error('Integer value required)', value)
        value = super().parse(value)
        return value


class Float(BaseField):
    """Float Field.

    The FLOAT type represent approximate numeric data values. MySQL uses four
    bytes for single-precision values. Keep in mind SQLLite uses REAL numbers
    with double floating points.

    For values which are more artefacts of nature which can't really be measured
    exactly anyway, float/double are more appropriate. For example, scientific data
    would usually be represented in this form. Here, the original values won't be
    "decimally accurate" to start with, so it's not important for the expected
    results to maintain the "decimal accuracy". Floating binary point types are
    much faster to work with than decimals.

    Keyword Args:
        m (int): Values can be stored with up to M digits in total.
        d (int): Digits that may be after the decimal point.
    """
    def __init__(self, m, d):
        self.m = m
        self.d = d
        super().__init__()

    def parse(self, value):
        try:
            value = float(value)
        except ValueError:
            self.error('Float value required', value)
        value = super().parse(value)
        return value


class Double(Float):
    """Double Field.

    The DOUBLE type represent approximate numeric data values. MySQL
    uses eight bytes for double-precision values. Keep in mind SQLLite uses
    REAL numbers with double floating points.

    For values which are more artefacts of nature which can't really be measured
    exactly anyway, float/double are more appropriate. For example, scientific data
    would usually be represented in this form. Here, the original values won't be
    "decimally accurate" to start with, so it's not important for the expected
    results to maintain the "decimal accuracy". Floating binary point types are
    much faster to work with than decimals.

    Doubles provide more accuracy vs floats. However in Python floats are
    doubles.

    Keyword Args:
        m (int): Values can be stored with up to M digits in total.
        d (int): Digits that may be after the decimal point.
    """
    def parse(self, value):
        try:
            value = float(value)
        except ValueError:
            self.error('Float/Double value required', value)
        value = super().parse(value)
        return value


class Decimal(BaseField):
    """Decimal Field.

    For values which are "naturally exact decimals" it's good to use decimal.
    This is usually suitable for any concepts invented by humans: financial
    values are the most obvious example, but there are others too. Consider the
    score given to divers or ice skaters, for example.

    Keep in mind in SQLite this is REAL numbers with double floating points.

    Keyword Args:
        m (int): Values can be stored with up to M digits in total.
        d (int): Digits that may be after the decimal point.
    """
    def __init__(self, m, d):
        super().__init__()

    def parse(self, value):
        try:
            value = PyDecimal(value)
        except ValueError:
            self.error('Decimal value required', value)
        value = super().parse(value)
        return value


class TinyInt(Integer):
    """Tiny Integer Field.

    1 Octet Integer
    Minimum value -128
    Maximum value 127

    Keyword Args:
        length (int): Length of field value.
        signed (bool): If Integer value is signed or un-signed.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Whether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Whether field can be updated.
        prefix (str): Text placed in front of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """
    def __init__(self, length=None, min_length=None, max_length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False,
                 signed=True):

        try:
            min_length, max_length = defined_length_check(min_length,
                                                          max_length,
                                                          -128,
                                                          -127)
        except ValueError as e:
            self.error(e)

        super().__init__(length=None,
                         min_length=min_length, max_length=max_length,
                         null=True, default=None, db=True, label=None,
                         placeholder=None, readonly=False, prefix=None,
                         suffix=None, columns=None, hidden=False,
                         enum=[], on_update=None, password=False)


class SmallInt(Integer):
    """Small Integer Field.

    2 Octet Integer
    Minimum value -32768
    Maximum value 32767

    Keyword Args:
        length (int): Length of field value.
        signed (bool): If Integer value is signed or un-signed.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Whether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Whether field can be updated.
        prefix (str): Text placed in front of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """
    def __init__(self, length=None, min_length=None, max_length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False,
                 signed=True):

        try:
            min_length, max_length = defined_length_check(min_length,
                                                          max_length,
                                                          -32768,
                                                          32767)
        except ValueError as e:
            self.error(e)

        super().__init__(length=None,
                         min_length=min_length, max_length=max_length,
                         null=True, default=None, db=True, label=None,
                         placeholder=None, readonly=False, prefix=None,
                         suffix=None, columns=None, hidden=False,
                         enum=[], on_update=None, password=False)


class MediumInt(Integer):
    """Medium Integer Field.

    3 Octet Integer
    Minimum value -8388608
    Maximum value 8388607

    Keyword Args:
        length (int): Length of field value.
        signed (bool): If Integer value is signed or un-signed.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Whether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Whether field can be updated.
        prefix (str): Text placed in front of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """
    def __init__(self, length=None, min_length=None, max_length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False,
                 signed=True):

        try:
            min_length, max_length = defined_length_check(min_length,
                                                          max_length,
                                                          -8388608,
                                                          8388607)
        except ValueError as e:
            self.error(e)

        super().__init__(length=length,
                         min_length=min_length, max_length=max_length,
                         null=null, default=None, db=True, label=None,
                         placeholder=None, readonly=False, prefix=None,
                         suffix=None, columns=None, hidden=False,
                         enum=[], on_update=None, password=False)


class BigInt(Integer):
    """Big Integer Field.

    4 Octet Integer
    Minimum value -9223372036854775808
    Maximum value 9223372036854775807

    Keyword Args:
        length (int): Length of field value.
        min_length (int): Minimum Length of field value.
        max_length (int): Maximum Length of field value others length value.
        signed (bool): If Integer value is signed or un-signed.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Whether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Whether field can be updated.
        prefix (str): Text placed in front of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """
    def __init__(self, length=None, min_length=None, max_length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False,
                 signed=True):

        try:
            min_length, max_length = defined_length_check(min_length,
                                                          max_length,
                                                          -9223372036854775808,
                                                          9223372036854775807)
        except ValueError as e:
            self.error(e)

        super().__init__(length=None,
                         min_length=min_length, max_length=max_length,
                         null=True, default=None, db=True, label=None,
                         placeholder=None, readonly=False, prefix=None,
                         suffix=None, columns=None, hidden=False,
                         enum=[], on_update=None, password=False)


class DateTime(BaseField):
    """DateTime Field.

    Accepts datetime values from strings and datetime objects.

    Supports timezones and naive, however all datetimes are converted to
    UTC/GMT +00:00.
    """
    def parse(self, value):
        try:
            if isinstance(value, py_datetime):
                if value.tzinfo is not None:
                    value = to_utc(value)
                else:
                    value = to_utc(value, src=TimezoneUTC())
            else:
                value = to_utc(value, src=TimezoneUTC())

        except ValueError as e:
            self.error('DateTime value required (%s)' % e, value)
        return value


class PyObject(BaseField):
    """Python Object Field.

    This object cannot be stored in database, however can be any object within
    python.
    """
    def __init__(self):
        super().__init__()
        self.db = False

    def parse(self, value):
        return value


class Blob(BaseField):
    """Blob Field.

    64 KB field
    65535 Octets

    Keyword Args:
        length (int): Length of field value.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Whether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Whether field can be updated.
        prefix (str): Text placed in front of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """

    def __init__(self, length=None, min_length=None, max_length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False):

        try:
            min_length, max_length = defined_length_check(min_length,
                                                          max_length,
                                                          0,
                                                          65535)
        except ValueError as e:
            self.error(e)

        super().__init__(length=None,
                         min_length=min_length, max_length=max_length,
                         null=True, default=None, db=True, label=None,
                         placeholder=None, readonly=False, prefix=None,
                         suffix=None, columns=None, hidden=False,
                         enum=[], on_update=None, password=False)

    def parse(self, value):
        if value is None:
            return value

        value = super().parse(value)
        return value


class TinyBlob(Blob):
    """Tiny Blob Field.

    255 Octets

    Keyword Args:
        length (int): Length of field value.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Whether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Whether field can be updated.
        prefix (str): Text placed in front of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """

    def __init__(self, length=None, min_length=None, max_length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False):

        try:
            min_length, max_length = defined_length_check(min_length,
                                                          max_length,
                                                          0,
                                                          255)
        except ValueError as e:
            self.error(e)

        super().__init__(length=None,
                         min_length=min_length, max_length=max_length,
                         null=True, default=None, db=True, label=None,
                         placeholder=None, readonly=False, prefix=None,
                         suffix=None, columns=None, hidden=False,
                         enum=[], on_update=None, password=False)


class MediumBlob(Blob):
    """Medium Blob Field.

    16 MB field
    16777215 Octets

    Keyword Args:
        length (int): Length of field value.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Whether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Whether field can be updated.
        prefix (str): Text placed in front of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """

    def __init__(self, length=None, min_length=None, max_length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False):

        try:
            min_length, max_length = defined_length_check(min_length,
                                                          max_length,
                                                          0,
                                                          16777215)
        except ValueError as e:
            self.error(e)

        super().__init__(length=None,
                         min_length=min_length, max_length=max_length,
                         null=True, default=None, db=True, label=None,
                         placeholder=None, readonly=False, prefix=None,
                         suffix=None, columns=None, hidden=False,
                         enum=[], on_update=None, password=False)


class LongBlob(Blob):
    """Long Blob Field.

    4 GB field
    4294967295 Octets

    Keyword Args:
        length (int): Length of field value.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Whether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Whether field can be updated.
        prefix (str): Text placed in front of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """

    def __init__(self, length=None, min_length=None, max_length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False):

        try:
            min_length, max_length = defined_length_check(min_length,
                                                          max_length,
                                                          0,
                                                          4294967295)
        except ValueError as e:
            self.error(e)

        super().__init__(length=None,
                         min_length=min_length, max_length=max_length,
                         null=True, default=None, db=True, label=None,
                         placeholder=None, readonly=False, prefix=None,
                         suffix=None, columns=None, hidden=False,
                         enum=[], on_update=None, password=False)


class Text(String):
    """Text Field.

    64 KB field
    65535 Octets

    Keyword Args:
        length (int): Length of field value.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Whether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Whether field can be updated.
        prefix (str): Text placed in front of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """

    def __init__(self, length=None, min_length=None, max_length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False):

        try:
            min_length, max_length = defined_length_check(min_length,
                                                          max_length,
                                                          0,
                                                          65535)
        except ValueError as e:
            self.error(e)

        super().__init__(length=None,
                         min_length=min_length, max_length=max_length,
                         null=True, default=None, db=True, label=None,
                         placeholder=None, readonly=False, prefix=None,
                         suffix=None, columns=None, hidden=False,
                         enum=[], on_update=None, password=False)


class TinyText(String):
    """Tiny Text Field.

    255 Octets

    Keyword Args:
        length (int): Length of field value.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Whether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Whether field can be updated.
        prefix (str): Text placed in front of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """

    def __init__(self, length=None,
                 min_length=None, max_length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False):

        try:
            min_length, max_length = defined_length_check(min_length,
                                                          max_length,
                                                          0,
                                                          255)
        except ValueError as e:
            self.error(e)

        super().__init__(length=None,
                         min_length=min_length, max_length=max_length,
                         null=True, default=None, db=True, label=None,
                         placeholder=None, readonly=False, prefix=None,
                         suffix=None, columns=None, hidden=False,
                         enum=[], on_update=None, password=False)


class MediumText(String):
    """Medium Text Field.

    16 MB field
    16777215 Octets

    Keyword Args:
        length (int): Length of field value.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Whether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Whether field can be updated.
        prefix (str): Text placed in front of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """

    def __init__(self, length=None, min_length=None, max_length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False):

        try:
            min_length, max_length = defined_length_check(min_length,
                                                          max_length,
                                                          0,
                                                          16777215)
        except ValueError as e:
            self.error(e)

        super().__init__(length=None,
                         min_length=min_length, max_length=max_length,
                         null=True, default=None, db=True, label=None,
                         placeholder=None, readonly=False, prefix=None,
                         suffix=None, columns=None, hidden=False,
                         enum=[], on_update=None, password=False)


class LongText(String):
    """Long Text Field.

    4 GB field
    4294967295 Octets

    Keyword Args:
        length (int): Length of field value.
        null (bool): If value is allowed to NULL.
        default: Default value for field.
        on_update: Default value for field on update..
        db (bool): Whether to store value in db column.
        label (str): Human friendly name for field.
        placeholder (str): Example to display in field.
        readonly (bool): Whether field can be updated.
        prefix (str): Text placed in front of field input.
        suffix (str): Text placed after field input.
        hidden (bool): To hide field from forms.
    """

    def __init__(self, length=None, min_length=None, max_length=None,
                 null=True, default=None, db=True, label=None,
                 placeholder=None, readonly=False, prefix=None,
                 suffix=None, columns=None, hidden=False,
                 enum=[], on_update=None, password=False):

        try:
            min_length, max_length = defined_length_check(min_length,
                                                          max_length,
                                                          0,
                                                          4294967295)
        except ValueError as e:
            self.error(e)

        super().__init__(length=None,
                         min_length=min_length, max_length=max_length,
                         null=True, default=None, db=True, label=None,
                         placeholder=None, readonly=False, prefix=None,
                         suffix=None, columns=None, hidden=False,
                         enum=[], on_update=None, password=False)


class Enum(String):
    """Enum Field.

    An ENUM is a string object with a value chosen from a list of permitted
    values that are enumerated explicitly in the column specification at table
    creation time.

    Provide arguements as individual permitted values.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.enum = args

    def parse(self, value):
        value = super().parse(value)
        if value not in self.enum:
            self.error('Invalid option', value)
        return value


class Uuid(String):
    """UUID Field.

    For example: 827C7CCC-F9BD-47AC-A674-ABBBED665008
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.length = 36
        self.min_length = 36
        self.max_length = 36

    def parse(self, value):
        if isinstance(value, uuid.UUID):
            value = str(value)
        return value


class Email(String):
    """Email Field.
    """
    def parse(self, value):
        value = super().parse(value)
        if not EMAIL_RE.match(value):
            self.error("Invalid email '%s'" % value, value)

        return value


class Phone(String):
    """Phone Number Field.
    """
    def parse(self, value):
        value = value.strip()

        try:
            if value[0] != '+':
                self.error("Invalid phone number '%s'" % value, value)
        except IndexError:
            self.error("Invalid phone number '%s'" % value, value)

        try:
            phone_no = phonenumbers.parse(value, None)
        except Exception:
            self.error("Invalid phone number '%s'" % value, value)

        if not phonenumbers.is_valid_number(phone_no):
            self.error("Invalid phone number '%s'" % value, value)

        phone_no = phonenumbers.format_number(
            phone_no,
            phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )

        return phone_no


class Word(String):
    def parse(self, value):
        value = super().parse(value)
        if not WORD_RE.match(value):
            self.error("Invalid Word '%s'" % value, value)

        return value


class Username(String):
    """Username Field.
    """
    def parse(self, value):
        value = super().parse(value)
        if not USERNAME_RE.match(value):
            self.error("Invalid Username '%s'" % value, value)

        return value


class Uri(String):
    """URI Field.
    """
    def parse(self, value):
        value = super().parse(value)
        if not URI_RE.match(value):
            self.error("Invalid URI '%s'" % value, value)

        return value


class Fqdn(String):
    """FQDN Field.
    """
    def parse(self, value):
        value = super().parse(value)
        if not FQDN_RE.match(value):
            self.error("Invalid Domain '%s'" % value, value)

        return value


class Boolean(SmallInt):
    """Boolean Field.
    """
    def parse(self, value):
        if value is None:
            value = False

        elif isinstance(value, int):
            if value == 0:
                value = False
            else:
                value = True
        elif isinstance(value, (str, bytes,)):
            value = if_bytes_to_unicode(value).lower()
            if value == "1" or value == "on" or value == 'true':
                value = True
            else:
                value = False

        if not isinstance(value, bool):
            self.error('Invalid True/False Boolean value', value)
        return value


class UniqueIndex(BaseField):
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


class Index(BaseField):
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


class ForeignKey(BaseField):
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
        self._on_delete = on_delete.upper()
        self._on_update = on_update.upper()
        super().__init__()
        self.internal = True
