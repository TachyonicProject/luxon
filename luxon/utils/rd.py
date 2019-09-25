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
import pickle
import redlock
from logging import getLogger

log = getLogger(__name__)


class Redis(object):
    """Generic Redis object to use redis

    Args:
        connection: redis connection

    """
    __slots__ = ('_redis')

    def __init__(self, connection):
        self._redis = connection

    def lock(self, name, validity, retry_count=-1,
             retry_delay=200):
        if retry_count < 0:
            retry_count = 0
            is_blocking = True
        else:
            is_blocking = False

        while True:
            dlm = redlock.Redlock([self._redis],
                                  retry_count=retry_count+1,
                                  retry_delay=retry_delay / 1000.0)
            lock = dlm.lock(name, validity)

            if lock:
                return lock

            if is_blocking:
                # redlock already slept for retry-delay
                continue

    def unlock(self, lock):
        dlm = redlock.Redlock([self._redis])
        lock = redlock.Lock(0, lock.resource, lock.key)
        dlm.unlock(lock)

    def set(self, attr, value, expire=None):
        value = pickle.dumps(value)
        self._redis.set(attr, value, ex=expire)

    def delete(self, attr, value):
        return self._redis.delete(attr)

    def get(self, attr):
        value = self._redis.get(attr)
        if value is not None:
            return pickle.loads(value)
        else:
            return None

    def __setatrr__(self, attr, value):
        return self.set(attr, value)

    def __getattr__(self, attr):
        return self.get(attr)

    def __delattr__(self, attr):
        return self.delete(attr)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def __getitem__(self, key):
        return self.get(key)

    def __delitem__(self, key):
        return self.delete(key)

    def __contains__(self, key):
        return self._redis.exists(key)

    def __iter__(self):
        raise NotImplementedError()
