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

from luxon.utils import js
from luxon.utils.strings import try_lower
from luxon.utils.objects import object_name

class Container(object):
    """Property dictionary.

    Object behaves like dictionary but also have property names equal to
    dictionary keys.

    Provides conveniant clean interface for access and iterating over container
    items.

    Keys / Properties are also not case senstive.
    """
    __slots__ = ('__dict__')

    def __call__(self):
        return self.to_dict()

    def to_dict(self):
        return dict((value[0], value[1]) for (key, value) in self.__dict__.items())

    def clear(self):
        """Clear container keys/values.
        """
        self.__dict__.clear()

        return self

    def __setattr__(self, key, value):
        self[key] = value

    def __getattribute__(self, attr):
        if hasattr(Container, attr):
            return super().__getattribute__(attr)

        try:
            return self.__getitem__(attr)
        except KeyError as e:
            raise AttributeError(e) from None

    def __setitem__(self, key, value):
        """Set key to value.
        """
        d_key = try_lower(key)
        self.__dict__[d_key] = (key, value)

    def __getitem__(self, key):
        """Get key value
        """
        d_key = try_lower(key)

        try:
            return self.__dict__.get(d_key)[1]
        except KeyError:
            raise KeyError(key)
        except TypeError:
            raise KeyError(key)

    def keys(self):
        """Get keys.
        """
        return list(self.__dict__.keys())

    def __delitem__(self, key):
        """Delete key/value.
        """
        d_key = try_lower(key)
        del self.__dict__[d_key]

    def __contains__(self, key):
        """True if has a key, else False.
        """
        d_key = try_lower(key)
        return d_key in self.__dict__

    def __iter__(self):
        """Return iterable of dictionary.
        """
        return iter(self())

    def items(self):
        """Return items in dictionary.
        """
        return list((value[0], value[1]) for (key, value) in self.__dict__.items())

    def has_key(self, key):
        return self.__contains__(key)

    def __len__(self):
        """Return int length of container.
        """
        return len(self.__dict__)

    def __repr__(self):
        """Return representation of dictionary.
        """
        return repr(object_name(self) + str(self()))

    def __str__(self):
        """Return string of dictionary.
        """
        return str(object_name(self) + str(self()))

    def update(self, dictionary):
        """Update dictionary.

        This method adds dictionary  key-values pairs in to
        dict. This function does not return anything.

        Args:
            dictionary (dict): This is the dictionary to be added into dict.
        """
        for item in dictionary:
            self[item] = dictionary[item]

    def values(self):
        return list((value[1]) for (key, value) in self.__dict__.items())

    def get(self, key, default=None):
        """Get key value.

        The method returns a value for the given key. If key is not
        available then returns default value None.

        Args:
            key (str): Unique key for value.
            default (obj): Default Value (optional)

        Returns a value for the given key. If key is not available,
        then returns default value None.
        """
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    @property
    def json(self):
        """Return JSON Object of container"""
        return js.dumps(self())

    def copy(self):
        """Create a shallow copy of container.
        """
        new = Container()
        new.__dict__.update(self.__dict__)

        return new
