# -*- coding: utf-8 -*-
# Copyright (c) 2019 Christiaan Frans Rademan.
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
import json
import asyncio
import struct
import pickle
from logging import getLogger

from bidict import bidict

from luxon.core.networking.pipe import Pipe

log = getLogger(__name__)


def connection_closed(peer, extra=None):
    if extra:
        log.debug('Connction closed / failed %s ## %s ##' % (str(peer),
                                                             extra,))
    else:
        log.debug('Connction closed / failed %s' % str(peer))


def channel_closed(peer, channel):
    log.debug("Channel '%s' closed / failed %s" % (str(channel),
                                                   str(peer),))


def ch_dumps_pkt_h(pkt_type, channel, length=0):
    return struct.pack('!HQQ',
                       pkt_type,
                       channel,
                       length)


def ch_load_pkt_h(raw_data):
    return struct.unpack('!HQQ', raw_data)


async def async_recv_pickle(reader):
    header = await reader.readexactly(8)
    length = struct.unpack('!Q', header)[0]
    payload = await reader.readexactly(length)
    return pickle.loads(payload)


async def async_send_pickle(writer, data):
    payload = pickle.dumps(data, 4)
    writer.write(struct.pack('!Q', len(payload)) + payload)
    await writer.drain()
    return True


async def async_recv_json(reader):
    return json.loads(await reader.readline())


async def async_send_json(writer, data):
    writer.write(json.dumps(data).encode('UTF-8') + b'\n')
    await writer.drain()
    return True


async def start_client(callback, host='127.0.0.1', port=1983, ssl=None,
                       **kwargs):
    async def connect():
        while True:
            try:
                log.info("Connecting to '%s:%s'" % (host, port))
                reader, writer = await asyncio.open_connection(
                    host, port, ssl=ssl)
                return asyncio.ensure_future(callback(reader,
                                                      writer,
                                                      **kwargs))
            except Exception as err:
                log.critical(err)
                await asyncio.sleep(10)

    async def reconnect(coro):
        while True:
            if coro.done():
                coro = await connect()
            await asyncio.sleep(1)

    coro = await connect()
    asyncio.ensure_future(reconnect(coro))

    return coro


class MultiplexConnection(object):
    def __init__(self, cb, loop, reader, writer):
        self._cb = cb
        self._loop = loop
        self._reader = reader
        self._writer = writer
        self._peer = writer.get_extra_info('peername')
        self._id_counter = 0
        self._id_lock = asyncio.Lock()
        self._remote_ch_req = asyncio.Lock()
        self._write_lock = asyncio.Lock()
        self._read_lock = asyncio.Lock()
        self._closed = False

        # Used for Matching local channel with remote.
        self._channels = bidict()

        # Channel Sockets.
        self._channel_sockets = {}

        # Queue for new channel request.
        self._channel_requests = asyncio.Queue()

    async def _write(self, data):
        async with self._write_lock:
            self._writer.write(data)
            await self._writer.drain()

    async def _read(self, length):
        async with self._read_lock:
            return await self._reader.readexactly(length)

    async def _ping(self):
        while not self._closed:
            try:
                await self._write(ch_dumps_pkt_h(2, 0))
                await asyncio.sleep(25)
            except Exception:
                connection_closed(self.peer)
                self.close()
                break

    @property
    def peer(self):
        return self._peer

    async def _new_channel_id(self):
        async with self._id_lock:
            self._id_counter += 1
            return self._id_counter

    async def _remote_channel(self, remote_id):
        async with self._remote_ch_req:
            # Remote request new RPC channel
            server = None
            try:
                server, channel = Pipe()
            except OSError:
                await self._write(ch_dumps_pkt_h(3, remote_id))
                log.critical('Local server out of file descriptors')

            if server:
                local_id = await self._new_channel_id()
                self._channels[local_id] = remote_id

                ch_reader, ch_writer = await asyncio.open_connection(
                    sock=server)
                self._channel_sockets[local_id] = (ch_writer, channel,)

                asyncio.ensure_future(
                    self._channel_proxy(local_id,
                                        ch_reader,
                                        ch_writer))
                asyncio.ensure_future(
                    self._cb(* await asyncio.open_connection(sock=channel)))

    async def _run(self):
        read = self._read

        asyncio.ensure_future(self._ping())

        while not self._closed:
            try:
                data = await read(18)
            except (asyncio.IncompleteReadError,
                    ConnectionResetError,
                    BrokenPipeError):
                self.close()
                connection_closed(self.peer)
                break
            pkt, remote_id, length = struct.unpack('!HQQ', data)
            if pkt == 0:
                # Proxy Data to channel
                data = await read(length)
                try:
                    # Already Exisiting Channel get local_id
                    local_id = self._channels.inverse[remote_id]
                except KeyError:
                    # If Channel Requested get local_id
                    local_id = await self._channel_requests.get()
                    self._channels[local_id] = remote_id
                try:
                    self._channel_sockets[local_id][0].write(data)
                    await self._channel_sockets[local_id][0].drain()
                except Exception as err:
                    print('ch err', err)
                    channel_closed(self.peer, local_id)
            elif pkt == 1:
                await self._remote_channel(remote_id)
            elif pkt == 2:
                log.debug('Ping Received %s' % str(self.peer))
            elif pkt == 3:
                # Close Socket request from remote.
                log.critical('Remote server out of file descriptors')
                try:
                    del self._channels[remote_id]
                except KeyError:
                    pass
                self._channel_sockets[remote_id][0].close()

    async def _channel_proxy(self, local_id, ch_reader, ch_writer):
        while True:
            try:
                data = await ch_reader.read(1024)
            except Exception:
                data = None

            if not data:
                try:
                    try:
                        self._channel_sockets[local_id][0].close()
                    except Exception:
                        pass
                    del self._channel_sockets[local_id]
                except KeyError:
                    pass

                ch_writer.close()
                break

            header = ch_dumps_pkt_h(0, local_id, len(data))
            try:
                await self._write(header + data)
            except Exception:
                connection_closed(self.peer)
                self.close()

    async def _channel_request(self, local_id):
        try:
            await self._write(ch_dumps_pkt_h(1, local_id))
        except Exception:
            connection_closed(self.peer)
            self.close()

    def __str__(self):
        return str('MultiplexConnection' + str(self._peer))

    def __repr__(self):
        return repr('MultiplexConnection' + str(self._peer))

    async def channel(self):
        # Request new channel.
        local_id = await self._new_channel_id()
        await self._channel_requests.put(local_id)
        try:
            server, channel = Pipe()
        except OSError:
            raise ConnectionError('Local server out' +
                                  ' of file descriptors') from None

        ch_reader, ch_writer = await asyncio.open_connection(sock=server)
        self._channel_sockets[local_id] = (ch_writer, channel,)
        asyncio.ensure_future(
            self._channel_proxy(local_id,
                                ch_reader,
                                ch_writer),
            loop=self._loop)
        await self._channel_request(local_id)
        return await asyncio.open_connection(sock=channel)

    def close(self):
        self._closed = True
        for sock in self._channel_sockets.values():
            sock[0].close()
        self._channel_sockets = {}
        self._writer.close()
