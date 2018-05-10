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
import pickle
import redis


class Redis(object):
    __slots__ = ('_redis', '_expire',)

    def __init__(self, *args, expire=None, **kwargs):
        self._redis = redis.StrictRedis(**kwargs)
        self._expire = expire

    def __setatrr__(self, attr, value):
        value = pickle.dumps(value)
        self._redis.set(attr, value, ex=self._expire)

    def __getattr__(self, attr):
        value = self._redis.get(attr)
        if value is not None:
            return pickle.loads(value)
        else:
            return None

    def __delattr__(self, attr):
        return self._redis.delete(attr)

    def __setitem__(self, key, value):
        value = pickle.dumps(value)
        self._redis.set(key, value, ex=self._expire)

    def __getitem__(self, key):
        value = self._redis.get(key)
        if value is not None:
            return pickle.loads(value)
        else:
            return None

    def __delitem__(self, key):
        return self._redis.delete(key)

    def __contains__(self, key):
        return self._redis.exists(key)

    def __iter__(self):
        raise NotImplemented()
