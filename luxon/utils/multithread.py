# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Dave Kruger.
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

import threading

from luxon import GetLogger
from luxon.utils.objects import object_name

log = GetLogger(__name__)


def thread_balance(per_thread, func, items):
    if isinstance(items, dict):
        items = list(items.keys())

    name = object_name(func)

    log.info("Balancing '%s' items to '%s'." % (len(items), name,))

    total_items = len(items)
    threads = []
    try:
        for thread in range(0, total_items, per_thread):
            end = thread + per_thread
            t = threading.Thread(target=func, args=(items[thread:end],))
            threads.append(t)
            t.start()

        log.info("Balanced '%s' items to '%s'. Total threads '%s'" %
                 (len(items), name, len(threads),))

        for thread in threads:
            thread.join()

    except KeyboardInterrupt:
        for thread in threads:
            thread.join()
