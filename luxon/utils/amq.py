# -*- coding: utf-8 -*-
# Copyright (c) 2019-2020 Christiaan Frans Rademan <chris@fwiw.co.za>.
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
"""
RabbitMQ/AMQ Interface.
"""
import json
import pika
import traceback
from random import shuffle
from threading import Lock, RLock
from logging import getLogger

from luxon.exceptions import (MessageBusError,
                              MessageBusBlocked)
from luxon.utils.cast import to_tuple

log = getLogger(__name__)


class Channel(object):
    def __init__(self, amq, ch):
        self._amq = amq
        self.__ch = ch
        self._event_lock = amq._event_lock
        self._sync_lock = amq._sync_lock

    @property
    def close(self):
        return self._amq.close

    @property
    def running(self):
        return self._amq._running

    @property
    def shutdown(self):
        return self._amq._shutdown

    @property
    def _events(self):
        return self._amq._event_count

    @_events.setter
    def _events(self, value):
        self._amq._event_count = value

    @property
    def _ch(self):
        if self.shutdown:
            raise MessageBusError('Connection closed by client')
        return self.__ch

    def _event_set(self):
        try:
            self._event_lock.acquire()
            if self.running:
                self._events += 1
        finally:
            self._event_lock.release()

    def _event_clear(self):
        try:
            self._event_lock.acquire()
            if self._events > 0:
                self._events -= 1
        finally:
            self._event_lock.release()

    def _threadsafe(self, callback, *args, **kwargs):
        self._event_set()

        try:
            self._sync_lock.acquire()
            if callback == "basic_publish" and self._blocked:
                raise MessageBusBlocked('Connection blocked by broker')

            return getattr(self._ch, callback)(*args, **kwargs)
        except (SystemExit, KeyboardInterrupt):
            self.close()
            raise
        except Exception as err:
            raise MessageBusError(err) from None
        finally:
            self._sync_lock.release()

    def exchange_declare(self, name, exchange_type='direct',
                         passive=False, durable=False,
                         auto_delete=False, internal=True):
        return self._threadsafe('exchange_declare',
                                exchange=name,
                                exchange_type=exchange_type,
                                passive=passive,
                                durable=durable,
                                auto_delete=auto_delete,
                                internal=False)

    def exchange_delete(self, exchange, if_unused=False):
        return self._threadsafe('exchange_delete',
                                exchange=exchange,
                                if_unused=if_unused)

    def exchange_bind(self, destination, source, routing_key=''):
        return self._threadsafe('exchange_unbind',
                                destination,
                                source,
                                routing_key=routing_key)

    def exchange_unbind(self, destination=None, source=None,
                        routing_key=''):
        return self._threadsafe('exchange_unbind',
                                destination=destination,
                                source=source,
                                routing_key=routing_key)

    def queue_declare(self, name, passive=False, durable=False,
                      exclusive=False, auto_delete=False):
        return self._threadsafe('queue_declare',
                                name,
                                passive=passive,
                                durable=durable,
                                exclusive=False,
                                auto_delete=False)

    def queue_delete(self, queue, if_unused=False, if_empty=False):
        return self._threadsafe('queue_delete',
                                queue,
                                if_unused=if_unused,
                                if_empty=if_empty)

    def queue_purge(self, queue):
        return self._threadsafe('queue_unbind',
                                queue)

    def queue_bind(self, queue, exchange, routing_key=None):
        return self._threadsafe('queue_bind',
                                queue,
                                exchange,
                                routing_key=routing_key)

    def queue_unbind(self, queue, exchange=None, routing_key=None):
        return self._threadsafe('queue_unbind',
                                queue,
                                exchange,
                                routing_key=routing_key)

    def prefetch(self, count):
        return self._threadsafe('basic_qos', prefetch_count=count)

    def ack_msg(self, delivery_tag):
        return self._threadsafe('basic_ack', delivery_tag=delivery_tag)

    def nack_msg(self, delivery_tag, requeue=False):
        return self._threadsafe('basic_reject',
                                delivery_tag=delivery_tag,
                                requeue=False)

    def publish(self, exchange, routing_key,
                msg, properties=None, mandatory=False):
        self._threadsafe('basic_publish',
                         exchange,
                         routing_key,
                         self.SERIALIZER.dumps(msg),
                         properties=properties,
                         mandatory=mandatory)

    def consume(self, queue, callback, auto_ack=False,
                exclusive=False, consumer_tag=None):
        def cb_wrapper(ch, method, properties, body):
            msg = self.SERIALIZER.loads(body)
            try:
                callback(Channel(self, ch),
                         method.delivery_tag,
                         properties,
                         msg)
            except Exception:
                log.critical('%s\n%s' %
                             (str(msg),
                              str(traceback.format_exc(),)))

        return self._threadsafe('basic_consume',
                                on_message_callback=cb_wrapper,
                                queue=queue,
                                auto_ack=auto_ack,
                                exclusive=exclusive,
                                consumer_tag=consumer_tag)


class Amq(Channel):
    SERIALIZER = json

    def __init__(self, hosts='127.0.0.1', port=5672,
                 virtualhost='/', username=None, password=None,
                 channel_callback=None, block_callback=None,
                 unblock_callback=None, heartbeat=15):

        amq_params = {'port': port,
                      'virtual_host': virtualhost,
                      'heartbeat': heartbeat,
                      'blocked_connection_timeout': 1}

        self._ch_callback = channel_callback
        self._unblock_callback = unblock_callback
        self._block_callback = block_callback
        self._sync_lock = RLock()
        self._event_count = 0
        self._event_lock = RLock()
        self._ioloop_lock = Lock()
        self._connect_lock = Lock()
        self._blocked = False

        if username:
            amq_params = {**amq_params,
                          'credentials': pika.PlainCredentials(username,
                                                               password)}
        self._conn_params = []
        for host in to_tuple(hosts):
            self._conn_params.append(pika.ConnectionParameters(host=host,
                                                               **amq_params))

        self.connect()

    def connect(self):
        self.__conn = None
        self.__ch = None
        self._shutdown = False
        self._events = 0
        self._running = False
        self._connect()

    @property
    def running(self):
        return self._running

    @property
    def shutdown(self):
        return self._shutdown

    @property
    def _events(self):
        return self._event_count

    @_events.setter
    def _events(self, value):
        self._event_count = value

    @property
    def channel(self):
        return Channel(self, self.__ch)

    def _threadsafe(self, callback, *args, **kwargs):
        self._event_set()

        while True:
            try:
                self._sync_lock.acquire()
                if callback == "basic_publish" and self._blocked:
                    raise MessageBusBlocked('Connection blocked by broker')

                return getattr(self._ch, callback)(*args, **kwargs)
            except (SystemExit, KeyboardInterrupt):
                self.close()
                raise
            except pika.exceptions.ConnectionClosedByBroker as err:
                log.warning(err)
                self._connect()
                continue
            except pika.exceptions.AMQPChannelError as err:
                log.warning(err)
                self._connect()
                continue
            except pika.exceptions.AMQPConnectionError as err:
                log.warning(err)
                self._connect()
                continue
            except Exception as err:
                raise MessageBusError(err) from None
            finally:
                self._sync_lock.release()

    def _blocked_cb(self, conn, method):
        self._blocked = True
        if self._block_callback:
            self._block_callback()

    def _unblocked_cb(self, conn, method):
        self._blocked = False
        if self._unblock_callback:
            self._unblock_callback()

    def _connect(self):
        if self._connect_lock.acquire(False):
            if self.shutdown:
                raise MessageBusError('Connection closed by client')
            # If not locked, meaning nobody other calls to connect()
            try:
                # Shuffle the connections.
                shuffle(self._conn_params)
                self.__conn = pika.BlockingConnection(self._conn_params)
                self.__ch = self._conn.channel()
                self.__conn.add_on_connection_blocked_callback(
                    self._blocked_cb)
                self.__conn.add_on_connection_unblocked_callback(
                    self._unblocked_cb)
                if self._ch_callback:
                    self._ch_callback(self)
            finally:
                self._connect_lock.release()
        else:
            # If other call to connect()... lock and wait...
            self._connect_lock.acquire()
            self._connect_lock.release()

    @property
    def _conn(self):
        if self.shutdown:
            raise MessageBusError('Connection closed by client')
        return self.__conn

    @property
    def _ch(self):
        if self.shutdown:
            raise MessageBusError('Connection closed by client')
        return self.__ch

    def start(self):
        self._running = True

        while self.running:
            try:
                self._ioloop_lock.acquire()
                self._sync_lock.acquire()
                with self._conn._acquire_event_dispatch() as dis_acq:
                    # Check if we can actually process pending events
                    self._conn._flush_output(
                        lambda: bool(self._events),
                        lambda: bool(self.shutdown),
                        lambda: bool(not self.running),
                        lambda: bool(
                            dis_acq and
                            (self._conn._channels_pending_dispatch or
                             self._conn._ready_events)))
                self._event_clear()

                if self._conn._ready_events:
                    self._conn._dispatch_connection_events()

                if self._conn._channels_pending_dispatch:
                    self._conn._dispatch_channel_events()
            except (SystemExit, KeyboardInterrupt):
                self.close()
                raise
            except pika.exceptions.ConnectionClosedByBroker as err:
                log.warning(err)
                self._connect()
                continue
            except pika.exceptions.AMQPChannelError as err:
                log.warning(err)
                self._connect()
                continue
            except pika.exceptions.AMQPConnectionError as err:
                log.warning(err)
                self._connect()
                continue
            except Exception as err:
                raise MessageBusError(err) from None
            finally:
                try:
                    self._ioloop_lock.release()
                except RuntimeError:
                    pass
                try:
                    self._sync_lock.release()
                except RuntimeError:
                    pass

    def stop(self):
        self._running = False

    def close(self):
        if self._shutdown:
            return False
        try:
            self._shutdown = True
            self.stop()
            self._sync_lock.acquire()
            self._blocked = False

            try:
                self.__ch.close()
            except Exception as err:
                log.warning(err)

            try:
                self.__conn.close()
            except Exception as err:
                log.warning(err)

            self._events = 0
            return True
        finally:
            self._sync_lock.release()
