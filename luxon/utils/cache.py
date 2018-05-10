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

from luxon.utils.decorator import decorator
from luxon.utils.objects import object_name
from luxon.core.cache import Cache
from luxon.utils.hashing import md5sum
from luxon.utils.objects import orderdict

_cache_engine = None


def cache(expiry_time, func, *args, **kw):
    global _cache_engine

    if _cache_engine is None:
        _cache_engine = Cache()

    # mem args used to build reference id for cache.
    mem_args = [object_name(func), ]

    # NOTE(cfrademan): This is important, we dont wantobject address,
    # types etc inside of the cache reference. So using actual names
    # to build cache. When using redis for cache, the object type,
    # id/address will not be the same on different threads/
    # processes/hosts.
    args = list(args) + list(orderdict(kw).values())
    for arg in args:
        if not isinstance(arg, (str, int, float, bytes,)):
            mem_args.append(object_name(arg))
        else:
            mem_args.append(arg)

    # create the actual key / reference id.
    key = md5sum(pickle.dumps(mem_args))

    cached = _cache_engine.load(key)

    if cached is not None:
        return cached

    result = func(*args, **kw)
    _cache_engine.store(key, result, expiry_time)

    return result


def memoize(expiry_time=3600):
    def _memoize(func, *args, **kw):
        return cache(expiry_time, func, *args, **kw)[0]
    return decorator(_memoize)
