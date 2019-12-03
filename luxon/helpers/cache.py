# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020 Christiaan Frans Rademan <chris@fwiw.co.za>.
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

from luxon.utils.objects import object_name
from luxon.core.cache import Cache
from luxon.utils.hashing import md5sum
from luxon.utils.objects import orderdict
from operator import itemgetter


def cache(expire, func, *args, **kwargs):
    global _cache_engine

    _cache_engine = Cache()

    # mem args used to build reference id for cache.
    mem_args = [object_name(func), ]

    # Handle Kwargs - sort them etc.
    scan_args = list(kwargs.items())
    scan_args = sorted(scan_args, key=itemgetter(0))
    scan_args = list([item for sublist in scan_args for item in sublist])

    # Handle Args
    scan_args += list(args)
    

    # NOTE(cfrademan): This is important, we dont want object address,
    # types etc inside of the cache reference. We cannot memoize based
    # on args, kwargsargs provided to function containing objects other than
    # str, int, float, bytes,
    for arg in scan_args:
        if isinstance(arg, (str, int, float, bytes,)):
            mem_args.append(arg)
        else:
            raise ValueError("Cache 'callable' not possible with" +
                             " args/kwargsargs containing values with types" +
                             " other than 'str', 'int', 'float', 'bytes'")

    # create the actual key / reference id.
    key = md5sum(pickle.dumps(mem_args))

    cached = _cache_engine.load(key)

    if cached is not None:
        return cached

    result = func(*args, **kwargs)
    _cache_engine.store(key, result, expire)

    return result
