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
import traceback

import pika

from luxon import js
from luxon.exceptions import MessageBusError
from luxon.core.logger import GetLogger

log = GetLogger(__name__)


class Rmq(object):
    def __init__(self, host='127.0.0.1', port=5672,
                 virtualhost='/', username=None, password=None):

        params = [host, port, virtualhost]

        if username:
            params.append(pika.PlainCredentials(username, password))

        self._params = pika.ConnectionParameters(*params)

        try:
            self.connection = pika.BlockingConnection(self._params)
        except Exception as e:
            raise MessageBusError(e)

        self._channels = {}

    @property
    def channel(self):
        return self.connection.channel

    def close(self):
        try:
            self.connection.close()
        except Exception:
            pass

    def distribute(self, queue, **kwargs):
        retry = 5
        for i in range(retry):
            try:
                message = js.dumps(kwargs)
                channel = self.channel()
                channel.queue_declare(queue=queue, durable=True)
                channel.basic_publish(exchange='',
                                      routing_key=queue,
                                      body=message,
                                      properties=pika.BasicProperties(
                                         delivery_mode=2,  # msg persistent
                                         content_type='application/json',
                                         content_encoding='utf-8'
                                      ))
                return True
            except pika.exceptions.ChannelClosed as e:
                if i == retry - 1:
                    raise MessageBusError(e)
                self.connection = pika.BlockingConnection(self._params)
            except pika.exceptions.ConnectionClosed as e:
                if i == retry - 1:
                    raise MessageBusError(e)
                self.connection = pika.BlockingConnection(self._params)

    def receiver(self, queue, callback, acks=True, prefetch=1):
        def callback_wrapper(ch, method, properties, body):
            message = js.loads(body)
            try:
                if callback(self.connection, ch, method, properties, message):
                    if acks:
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    if acks:
                        ch.basic_reject(delivery_tag=method.delivery_tag,
                                        requeue=False)
            except Exception as e:
                if acks:
                    ch.basic_reject(delivery_tag=method.delivery_tag,
                                    requeue=True)
                log.critical('%s\n%s\n%s' %
                             (str(e),
                              str(message),
                              str(traceback.format_exc(),)))

        try:
            channel = self.channel()
            channel.queue_declare(queue=queue, durable=True)
            channel.basic_qos(prefetch_count=prefetch)
            channel.basic_consume(callback_wrapper,
                                  queue=queue)
            try:
                channel.start_consuming()
            except KeyboardInterrupt:
                channel.stop_consuming()

        except Exception as e:
            raise MessageBusError(e)

    def sleep(self, timeout):
        self.connection.sleep(timeout)

    def receive(self, queue, callback, acks=True):
        def callback_wrapper(ch, method, properties, body):
            def callback_run(*args, **kwargs):
                message = js.loads(body)
                try:
                    if callback(self.connection, ch, method,
                                properties, message,
                                *args, **kwargs):
                        if acks:
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                    else:
                        if acks:
                            ch.basic_reject(delivery_tag=method.delivery_tag,
                                            requeue=False)
                except Exception as e:
                    if acks:
                        ch.basic_reject(delivery_tag=method.delivery_tag,
                                        requeue=True)
                    log.critical('%s\n%s\n%s' %
                                 (str(e),
                                  str(message),
                                  str(traceback.format_exc(),)))
            return callback_run

        try:
            if queue in self._channels:
                channel = self._channels[queue]
            else:
                channel = self._channels[queue] = self.channel()
                channel.queue_declare(queue=queue, durable=True)
                channel.basic_qos(prefetch_count=1)
            try:
                method_frame, header_frame, body = channel.basic_get(queue)
                if method_frame:
                    return callback_wrapper(channel,
                                            method_frame,
                                            header_frame,
                                            body)
                else:
                    return None
            except KeyboardInterrupt:
                pass
        except Exception as e:
            log.critical('%s\n%s' %
                         (str(e),
                          str(traceback.format_exc(),)))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
