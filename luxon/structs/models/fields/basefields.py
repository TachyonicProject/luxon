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
import uuid
from decimal import Decimal as PyDecimal

import phonenumbers

from luxon.utils.global_counter import global_counter
from luxon.utils.encoding import if_bytes_to_unicode
from luxon.exceptions import FieldError
from luxon.utils.timezone import to_utc
from luxon.core.regex import (EMAIL_RE,
                              WORD_RE,
                              USERNAME_RE,
                              PASSWORD_RE,
                              URI_RE,
                              FQDN_RE,
                              DATETIME_RE)
from luxon import js


class BaseFields(object):
    """Base Fields outer class"""
    __slots__ = ()

    class BaseField(object):
        """Field Class.

        Provides abstractions for most common database data types.

        Keyword Args:
            length (int): Length of field value.
            min_length (int): Minimum Length of field value.
            max_length (int): Maximum Length of field value.
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
            callback (list): Function to populate value and/or options.
        """
        __slots__ = ('length', 'min_length', 'max_length', 'null', 'default',
                     'db', '_label', 'placeholder', 'readonly', 'prefix',
                     'suffix', 'columns', 'hidden', 'enum', '_field_name',
                     '_table', '_value', '_creation_counter', 'm', 'd',
                     'on_update', 'password', 'signed', 'ignore_null',
                     'callback')

        def __init__(self, length=None, min_length=None, max_length=None,
                     null=True, default=None, db=True, label=None,
                     placeholder=None, readonly=False, prefix=None,
                     suffix=None, columns=None, hidden=False,
                     enum=[], on_update=None, password=False,
                     signed=True, internal=False, ignore_null=False,
                     lower=False, upper=False, data_url=None,
                     data_endpoint=None, callback=None,
                     regex=None, regex_ignore_case=True):

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
            self._label = label
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
            self.lower = lower
            self.upper = upper
            self.data_url = data_url
            self.data_endpoint = data_endpoint
            self.callback = callback
            self.regex = regex
            self.regex_ignore_case = regex_ignore_case

        @property
        def name(self):
            return self._field_name

        @property
        def label(self):
            if self._label:
                return self._label
            else:
                return self.name.title().replace('_', ' ')

        def error(self, msg, value=None):
            raise FieldError(self.name, self.label, msg, value)

        def parse(self, value):
            if (self.null is False and
                    (value is None or str(value).strip() == '')):
                self.error('Empty field value (required)', value)

            if isinstance(value, (int, float, PyDecimal,)):
                if (self.min_length is not None and
                        value < self.min_length):
                    self.error("Minimum value '%s'" % self.min_length, value)
                if (self.max_length is not None and
                        value > self.max_length):
                    self.error("Exceeded max value '%s'"
                               % self.max_length, value)
            elif hasattr(value, '__len__'):
                if (self.min_length is not None and
                        len(value) < self.min_length):
                    self.error("Minimum length '%s'"
                               % self.min_length, value)
                if (self.max_length is not None and
                        len(value) > self.max_length):
                    self.error("Exceeded max length '%s'"
                               % self.max_length, value)

            if self.regex:
                if self.regex_ignore_case:
                    regex = re.compile(self.regex, re.IGNORECASE)
                else:
                    regex = re.compile(self.regex)

                if not regex.match(value):
                    self.error("Invalid value", value)

            return value

        def _parse(self, value):
            if value is not None:
                return self.parse(value)

    class String(BaseField):
        """String Field.

        Keyword Args:
            length (int): Length of field value.
            min_length (int): Minimum Length of field value.
            max_length (int): Maximum Length of field value.
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
            if self.lower:
                value = value.lower()
            if self.upper:
                value = value.upper()
            return value

    class Password(String):
        def parse(self, value):
            value = super().parse(value)
            if not PASSWORD_RE.match(value):
                self.error("invalid")
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
        def __init__(self, m, d, default=None, null=True):
            self.m = m
            self.d = d
            super().__init__()
            self.default = default
            self.null = null

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
        def __init__(self, m, d, default=None, null=True):
            self.m = m
            self.d = d
            super().__init__()
            self.default = default
            self.null = null

        def parse(self, value):
            try:
                value = PyDecimal(value)
            except ValueError:
                self.error('Decimal value required', value)
            value = super().parse(value)
            return value

    class DateTime(BaseField):
        """DateTime Field.

        Accepts datetime values from strings and datetime objects.

        Supports timezones and naive, however all datetimes are converted to
        UTC/GMT +00:00.
        """
        def parse(self, value):
            if value:
                if isinstance(value, str) and not DATETIME_RE.match(value):
                    self.error('DateTime value error (%s)' % value , value)
                try:
                    value = to_utc(value)
                except ValueError as e:
                    self.error('DateTime value error (%s)' % e, value)
            elif not self.null:
                self.error('DateTime value required'. value)
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

    class Json(String):
        """Json Field.

        When provided with a dict or list, the parser will convert to str
        in JSON format (eg. for writing into database).
        When provided with a str, the parser will attempt to load as dict/list
        to return. (eg. for when reading from database).
        """
        def parse(self, value):
            if isinstance(value, (dict, list)):
                return js.dumps(value, indent=0).replace('\n','')
            if isinstance(value, str):
                try:
                    return js.loads(value)
                except Exception:
                    self.error("Invalid json in '%s'" % value, value)

    class Enum(String):
        """Enum Field.

        An ENUM is a string object with a value chosen from a list of permitted
        values that are enumerated explicitly in the column specification at table
        creation time.

        Provide arguements as individual permitted values.
        """
        def __init__(self, *args, **kwargs):
            super().__init__(**kwargs)
            self.enum = []
            for arg in args:
                self.enum.append(str(arg))

        def parse(self, value):
            value = str(value)
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
            if not self.regex and not EMAIL_RE.match(value):
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
            if not self.regex and not WORD_RE.match(value):
                self.error("Invalid Word '%s'" % value, value)

            return value

    class Username(String):
        """Username Field.
        """
        def parse(self, value):
            value = super().parse(value)

            if not self.regex:
                if not USERNAME_RE.match(value):
                    self.error("Invalid Username '%s'" % value, value)

            return value

    class Uri(String):
        """URI Field.
        """
        def parse(self, value):
            value = super().parse(value)
            if not self.regex and not URI_RE.match(value):
                self.error("Invalid URI '%s'" % value, value)

            return value

    class Fqdn(String):
        """FQDN Field.
        """
        def parse(self, value):
            value = super().parse(value)
            if not self.regex and not FQDN_RE.match(value):
                self.error("Invalid Domain '%s'" % value, value)

            return value
