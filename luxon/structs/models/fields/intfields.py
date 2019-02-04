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
from luxon.utils.encoding import if_bytes_to_unicode
from luxon.structs.models.fields.basefields import BaseFields


class IntFields(object):
    """Int Fields outer class"""
    __slots__ = ()

    class BaseInteger(BaseFields.BaseField):
        """Integer Field.

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
            hidden (bool): To hide field from forms.
        """

        def __init__(self, length=None, min_length=None, max_length=None,
                     null=True, default=None, db=True, label=None,
                     placeholder=None, readonly=False, prefix=None,
                     suffix=None, columns=None, hidden=False,
                     enum=[], on_update=None, password=False,
                     signed=True):

            super().__init__(length=length,
                             min_length=min_length, max_length=max_length,
                             null=null, default=default, db=db, label=label,
                             placeholder=placeholder, readonly=readonly,
                             prefix=prefix, suffix=suffix, columns=columns,
                             hidden=hidden, enum=[], on_update=on_update,
                             password=password, signed=signed)

        def parse(self, value):
            try:
                value = int(value)
            except ValueError:
                self.error('Integer value required)', value)
            value = super().parse(value)
            return value

    class Integer(BaseInteger):
        """Integer Field.

        4 Octet Integer
        Minimum value -2147483648
        Maximum value 2147483647

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

            if signed is True:
                if min_length is None:
                    min_length = -2147483648
                if max_length is None:
                    max_length = 2147483647
            else:
                if min_length is None:
                    min_length = 0
                if max_length is None:
                    max_length = 4294967295

            super().__init__(length=length,
                             min_length=min_length, max_length=max_length,
                             null=null, default=default, db=db, label=label,
                             placeholder=placeholder, readonly=readonly,
                             prefix=prefix, suffix=suffix, columns=columns,
                             hidden=hidden, enum=[], on_update=on_update,
                             password=password, signed=signed)

    class TinyInt(BaseInteger):
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

            if signed is True:
                if min_length is None:
                    min_length = -128
                if max_length is None:
                    max_length = 127
            else:
                if min_length is None:
                    min_length = 0
                if max_length is None:
                    max_length = 255

            super().__init__(length=length,
                             min_length=min_length, max_length=max_length,
                             null=null, default=default, db=db, label=label,
                             placeholder=placeholder, readonly=readonly,
                             prefix=prefix, suffix=suffix, columns=columns,
                             hidden=hidden, enum=[], on_update=on_update,
                             password=password, signed=signed)

    class SmallInt(BaseInteger):
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

            if signed is True:
                if min_length is None:
                    min_length = -32768
                if max_length is None:
                    max_length = 32767
            else:
                if min_length is None:
                    min_length = 0
                if max_length is None:
                    max_length = 65535

            super().__init__(length=length,
                             min_length=min_length, max_length=max_length,
                             null=null, default=default, db=db, label=label,
                             placeholder=placeholder, readonly=readonly,
                             prefix=prefix, suffix=suffix, columns=columns,
                             hidden=hidden, enum=[], on_update=on_update,
                             password=password, signed=signed)

    class MediumInt(BaseInteger):
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

            if signed is True:
                if min_length is None:
                    min_length = -8388608
                if max_length is None:
                    max_length = 8388607
            else:
                if min_length is None:
                    min_length = 0
                if max_length is None:
                    max_length = 16777215

            super().__init__(length=length,
                             min_length=min_length, max_length=max_length,
                             null=null, default=default, db=db, label=label,
                             placeholder=placeholder, readonly=readonly,
                             prefix=prefix, suffix=suffix, columns=columns,
                             hidden=hidden, enum=[], on_update=on_update,
                             password=password, signed=signed)

    class BigInt(BaseInteger):
        """Big Integer Field.

        4 Octet Integer
        Minimum value -9223372036854775808
        Maximum value 9223372036854775807

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
            hidden (bool): To hide field from forms.
        """
        def __init__(self, length=None, min_length=None, max_length=None,
                     null=True, default=None, db=True, label=None,
                     placeholder=None, readonly=False, prefix=None,
                     suffix=None, columns=None, hidden=False,
                     enum=[], on_update=None, password=False,
                     signed=True):

            if signed is True:
                if min_length is None:
                    min_length = -9223372036854775808
                if max_length is None:
                    max_length = 9223372036854775807
            else:
                if min_length is None:
                    min_length = 0
                if max_length is None:
                    max_length = 18446744073709551615

            super().__init__(length=length,
                             min_length=min_length, max_length=max_length,
                             null=null, default=default, db=db, label=label,
                             placeholder=placeholder, readonly=readonly,
                             prefix=prefix, suffix=suffix, columns=columns,
                             hidden=hidden, enum=[], on_update=on_update,
                             password=password, signed=signed)

    class Boolean(TinyInt):
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
