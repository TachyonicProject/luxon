# -*- coding: utf-8 -*-
# Copyright (c) 2018 Christiaan Rademan, Dave Kruger.
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
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import queue
import atexit

from luxon import GetLogger
from luxon.exceptions import PoolExhausted
from luxon.utils.objects import object_name

log = GetLogger(__name__)


def _log(msg, obj, pool):
    log.info('%s: %s (COUNT: %s, MAX_POOL_SIZE: %s, MAX_OVERFLOW %s' %
             (msg, object_name(obj), pool._count,
              pool._pool_size, pool._max_overflow))


class ProxyObject(object):
    """ Class ProxyObject

    Class that creates objects with same attributes as
    the original, but is also aware of object pool.

    When the close() method is called on the Proxy object,
    it will not really be closed, and instead simply returned
    to the pool.

    Unless the pool limit has been reached, in which case the real
    close() method will be called on the object.

    Args:
        obj (obj): original (proxied) object.
        pool (Pool): queue.Queue object which is the pool associated with this object.
    """

    def __init__(self, obj, pool):
        self._obj = obj
        self._pool = pool

    def __getattr__(self, attr):
        if self._obj is None:
            raise ReferenceError('Object already returned to pool %s'
                                 % self._pool)

        if attr[0] == '_':
            return self.__dict__[attr]
        else:
            return getattr(self._obj, attr)

    def __setattr__(self, attr, value):
        if attr[0] == '_':
            self.__dict__[attr] = value
        else:
            setattr(self._obj, attr, value)

    def _close_or_return(self):
        """ Method _close_or_return().

        Internal Method that either returns the object to the pool,
        or closes the proxied object in the case where the pool_size has been reached.
        """
        if self._pool._count <= self._pool._pool_size:
            _log('Returning object to pool', self._obj, self._pool)
            try:
                self._obj.clean_up()
            except AttributeError:
                pass
            self._pool._queue.put(self._obj)
        else:
            try:
                self._obj.close()
            except AttributeError:
                pass
            # Since we have closed the connection,
            # we can now decrease spawn count to allow
            # for one more instance.
            self._pool._count -= 1

        # In order to prevent the use of the connector object after
        # its returned, the proxied object is deleted.
        self._obj = None

    def close(self):
        """ Method close()

        Put back in queue this proxy object.
        But only if we have not exceeded pool_size.
        """
        self._close_or_return()

    def __enter__(self):
        # Used when entering the with statement.
        return self

    def __exit__(self, type, value, traceback):
        # When exiting the with statement.
        self._close_or_return()


class Pool(object):
    """ Class Pool.

    Pool manager for any objects such as db connections.

    Specify pool_size and max_overflow when creating the pool object.
    Call it to obtain a connector object. If one is available in the pool,
    it will be returned, otherwise a new object will be created and returned.

    Args:
        get_obj_func (obj): The function that creates and returns the connector object.
        pool_size (int): Length of the queue. At any given time no more than this many objects will
                         exist in the queue.
        max_overflow (int): How many objects can be created over an
                            above the pool size. The maximum
                            number of objects that will exist at any given time equals the sum of pool_size
                            and max_overflow. When the number of created objects exceed the pool_size, the next object
                            to be closed will really be closed and not returned to the pool.

    Example:
        .. code:: python

            def someFunc():
                return some_connector_object

            pool = Pool(someFunc, pool_size=10, max_overflow=10)

            conn = pool()
            conn.someMethod()
            conn.close()

        or

        .. code:: python

            with pool() as conn:
                conn.someMethod()
    """

    def __init__(self, get_obj_func, pool_size=10, max_overflow=10):
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._queue = queue.Queue(maxsize=pool_size)
        self._get_obj_func = get_obj_func
        self._count = 0

    def __call__(self):
        count = self._count
        pool_size = self._pool_size
        max_pool_size = pool_size + self._max_overflow
        if count < max_pool_size:
            q = self._queue

            # First trying to get object from the pool
            # (connector obj returned from from get_obj_func)
            try:
                # if in queue, grab it there
                _get_obj = q.get(False)
                try:
                    _get_obj.ping()
                except AttributeError:
                    pass
                _log('Using object from pool', _get_obj, self)
            except queue.Empty:
                # If not in queue
                # create new conn object.
                _get_obj = self._get_obj_func()
                self._count += 1
                _log('Created new object', _get_obj, self)
                try:
                    atexit.register(_get_obj.close)
                except AttributeError:
                    pass

            return ProxyObject(_get_obj, self)
        else:
            raise PoolExhausted(self._get_obj_func.__name__, self._count)
