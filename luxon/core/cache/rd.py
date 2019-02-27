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
import sys
import pickle

from luxon.helpers.rd import Redis as RedisHelper
from luxon.core.logger import GetLogger

log = GetLogger(__name__)


class Redis(object):
    """Caches objects in Redis object store"""
    def __init__(self, max_objs=None, max_obj_size=50):
        self._max_obj_size = 1024 * max_obj_size
        log.info('Redis Cache Initialized' +
                 ' max_obj_size=%sKbytes' % (max_obj_size,))

    def load(self, key):
        """Loads cached data from key

        Args:
            key (str): key for required data
        """
        with RedisHelper() as redis:
            return redis.get('cache:' + key)

    def store(self, key, value, expire):
        """Stores data

        Args:
            key (str): key associated with cached data
            value (obj): data to be cached
            expire (int): time to expire (s)
        """
        if sys.getsizeof(value, 0) <= self._max_obj_size:
            with RedisHelper() as redis:
                redis.set('cache:' + key,
                          pickle.dumps(value),
                          ex=expire)
