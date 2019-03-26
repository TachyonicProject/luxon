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
from multiprocessing import Process, current_process
import threading

from luxon import g
from luxon.core.logger import GetLogger
from luxon.core.logger import MPLogger
from luxon.utils.rmq import Rmq
from luxon.exceptions import MessageBusError

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
            raise MessageBusError('MBClient connection closed')

    def __enter__(self):
        self._rmq = rmq()
        return self

    def __exit__(self, type, value, traceback):
        self._rmq.close()

    def close(self):
        if self._rmq is not None:
            self._rmq.close()


class MBServer(object):
    def __init__(self, queue, funcs, procs=1, threads=1):
        self._funcs = funcs
        self._procs = procs
        self._threads = threads
        self._queue = queue
        self._mb_procs = []

    def start(self):
        for mp in range(self._procs):
            self._mb_procs.append(Process(target=self._messagebus_proc,
                                          name='MB-%s' % (mp+1,)))

        for proc in self._mb_procs:
            proc.start()

    def check(self):
        for proc in self._mb_procs:
            if not proc.is_alive():
                self._mb_procs.remove(proc)
                new = Process(target=self._messagebus_proc,
                              name=proc.name)
                log.critical('Restarting process %s' % proc.name)
                self._mb_procs.append(new)
                new.start()

    def stop(self):
        for proc in self._mb_procs:
            proc.terminate()

    def _messagebus_proc(self):
        proc_name = current_process().name
        MPLogger(__name__)
        threads = []
        for thread in range(self._threads):
            threads.append(None)

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

        def action(connection, ch, method, properties, msg):
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
                    raise MessageBusError('Message failed to process' +
                                          ' type %s' % msg_type +
                                          ' with empty body')
            else:
                msg_ack = functools.partial(reject_message, ch,
                                            method.delivery_tag,
                                            True)
                connection.add_callback_threadsafe(msg_ack)
                raise MessageBusError('Message failed to process' +
                                      ' unknown func/type %s' % msg_type)

        def callback(connection, ch, method, properties, msg):
            # Clean up threads.
            for th, thread in enumerate(threads):
                if thread and not thread.is_alive():
                    threads[th] = None
                    thread.join()

            # Find first availible thread.
            for th, thread in enumerate(threads):
                if thread is None:
                    thread_slot = th
                    break
                else:
                    thread_slot = -1

            if thread_slot > -1:
                thread = threading.Thread(
                    target=action,
                    name='%s-%s' % (proc_name,
                                    thread_slot+1,),
                    args=(connection, ch, method, properties, msg,))
                thread.start()
                threads[thread_slot] = thread
            else:
                log.critical('Process overload, message set for requeue')
                msg_ack = functools.partial(reject_message, ch,
                                            method.delivery_tag,
                                            True)
                connection.add_callback_threadsafe(msg_ack)

        with rmq() as mb:
            mb.receiver(self._queue, callback,
                        acks=False, prefetch=self._threads)
