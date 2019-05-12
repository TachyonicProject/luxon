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
import functools
from queue import Queue
from multiprocessing import current_process

from luxon import g
from luxon.core.logger import GetLogger
from luxon.utils.rmq import Rmq
from luxon.exceptions import MessageBusError
from luxon.utils.multiproc import ProcessManager
from luxon.utils.multithread import ThreadManager

log = GetLogger(__name__)


def rmq():
    kwargs = g.app.config.kwargs('rabbitmq')
    return Rmq(**kwargs)


class MBClient(object):
    def __init__(self, queue):
        self._queue = queue
        self._rmq = None

    def send(self, func, msg):
        if self._rmq is not None:
            msg = {'type': func,
                   'msg': msg}
            self._rmq.distribute(self._queue, **msg)
        else:
            raise MessageBusError('MBClient connection closed' +
                                  '/ use enter context')

    def __enter__(self):
        self._rmq = rmq()
        return self

    def __exit__(self, type, value, traceback):
        self._rmq.close()

    def close(self):
        if self._rmq is not None:
            self._rmq.close()


class MBServer(object):
    def __init__(self, queue, funcs, procs=1, threads=1, process_manager=None):
        self._funcs = funcs
        self._procs = procs
        self._threads = threads
        self._queue = queue
        if process_manager:
            self._pm = process_manager
            self._pmi = False
        else:
            self._pm = ProcessManager()
            self._pmi = True

    def start(self):
        for mp in range(self._procs):
            self._pm.new(self._messagebus_proc,
                         'MB-%s' % (mp+1,),
                         restart=True)

        if self._pmi:
            self._pm.start()

    def _messagebus_proc(self):
        proc_name = current_process().name
        tm = ThreadManager()
        queue = Queue(maxsize=self._threads * 2)

        def ack_message(ch, delivery_tag):
            if ch.is_open:
                ch.basic_ack(delivery_tag=delivery_tag)
            else:
                pass

        def reject_message(ch, delivery_tag, requeue=False):
            if ch.is_open:
                ch.basic_reject(delivery_tag=delivery_tag,
                                requeue=False)
            else:
                pass

        def _messagebus_thread():
            while True:
                connection, ch, method, properties, msg = queue.get()
                msg_type = msg.get('type')
                message = msg.get('msg')
                if msg_type in self._funcs:
                    if message is not None:
                        if self._funcs[msg_type](message):
                            msg_ack = functools.partial(ack_message, ch,
                                                        method.delivery_tag)
                            connection.add_callback_threadsafe(msg_ack)
                        else:
                            msg_ack = functools.partial(reject_message, ch,
                                                        method.delivery_tag,
                                                        False)
                            connection.add_callback_threadsafe(msg_ack)
                    else:
                        msg_ack = functools.partial(reject_message, ch,
                                                    method.delivery_tag,
                                                    False)
                        connection.add_callback_threadsafe(msg_ack)
                        log.critical('Message failed to process' +
                                     ' type %s' % msg_type +
                                     ' with empty body')
                else:
                    msg_ack = functools.partial(reject_message, ch,
                                                method.delivery_tag,
                                                False)
                    connection.add_callback_threadsafe(msg_ack)
                    log.critical('Message failed to process' +
                                 ' unknown func/type %s' % msg_type)

        def _thread_receiver():
            def callback(connection, ch, method, properties, msg):
                queue.put((connection, ch, method, properties, msg))

            with rmq() as mb:
                mb.receiver(self._queue, callback,
                            acks=False, prefetch=self._threads)

        tm.new(_thread_receiver, '%s-Receiver', restart=True)
        for thread in range(self._threads):
            tm.new(_messagebus_thread,
                   '%s-%s' % (proc_name,
                              thread+1,),
                   restart=True)
        tm.start()
