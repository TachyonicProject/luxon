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
from luxon.structs.models.fields.basefields import BaseFields
from luxon.structs.models.utils import defined_length_check


class BlobFields(object):
    """Blob Fields outer class"""
    __slots__ = ()


    class BaseBlob(BaseFields.BaseField):
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

            super().__init__(length=None,
                             min_length=min_length, max_length=max_length,
                             null=True, default=None, db=True, label=None,
                             placeholder=None, readonly=False, prefix=None,
                             suffix=None, columns=None, hidden=False,
                             enum=[], on_update=None, password=False)

    class Blob(BaseBlob):
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


    class TinyBlob(BaseBlob):
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


    class MediumBlob(BaseBlob):
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


    class LongBlob(BaseBlob):
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
