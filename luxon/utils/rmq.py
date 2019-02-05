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
import pika

from luxon import js


class Rmq(object):
    def __init__(self, host='127.0.0.1', port=5672,
                 virtualhost='/', username=None, password=None):

        params = [host, port, virtualhost]

        if username:
            params.append(pika.PlainCredentials(username, password))

        params = pika.ConnectionParameters(*params)

        self.connection = pika.BlockingConnection(params)

    @property
    def channel(self):
        return self.connection.channel

    def close(self):
        self.connection.close()

    def distribute(self, queue, **kwargs):
        message = js.dumps(kwargs)
        channel = self.channel()
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_publish(exchange='',
                              routing_key=queue,
                              body=message,
                              properties=pika.BasicProperties(
                                 delivery_mode=2,  # makes message persistent
                                 content_type='application/json',
                                 content_encoding='utf-8'
                              ))

    def receiver(self, queue, callback):
        def callback_wrapper(ch, method, properties, body):
            message = js.loads(body)
            callback(ch, method, properties, message)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel = self.channel()
        channel.queue_declare(queue=queue, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(callback_wrapper,
                              queue=queue)
        channel.start_consuming()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
