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
import os
import ssl
import select
import socket
import asyncio
from multiprocessing import (Process,
                             cpu_count,
                             Lock)

from luxon import GetLogger
from luxon.core.networking.sock import Socket

log = GetLogger(__name__)


class SSLInterface(object):
    def __init__(self, server):
        self._unix_sock = server._unix_sock
        self._local_server_sock = server._local_server_sock
        self._blocking = False
        self._timeout = 120

    def settimeout(self, value):
        try:
            self._blocking = True
            self._timeout = float(value)
        except ValueError:
            self._timeout = None

    def setblocking(self, value):
        self._blocking = bool(value)

    def fileno(self):
        if self._local_server_sock:
            return self._local_server_sock.fileno()
        else:
            raise Exception('Not Server')

    def accept(self):
        if self._local_server_sock:
            while True:
                read, write, ex = select.select([self._local_server_sock],
                                                [], [], 1)
                if read:
                    break
            sock, addr = self._local_server_sock.accept()
            sock.setblocking(self._blocking)
            if self._timeout:
                sock.settimeout(self._timeout)
            return (Socket(sock, addr), addr)
        else:
            raise Exception('Not Server')

    def connect(self):
        if self._local_server_sock:
            raise Exception('Not client')
        else:
            sock = socket.socket(socket.AF_UNIX,
                                 socket.SOCK_STREAM)
            sock.connect(self._unix_sock)
            sock.setblocking(self._blocking)
            if self._timeout:
                sock.settimeout(self._timeout)
            return Socket(sock, None)


class SSLServer(object):
    def __init__(self,
                 unix_socket,
                 host,
                 server=False,
                 cert=None,
                 key=None,
                 procs=cpu_count()):
        self._host = host
        self._cert = cert
        self._key = key
        self._server = server
        self._listen_sock = None
        self._unix_sock = unix_socket
        self._local_server_sock = None
        self._lock = Lock()

        self._procs_count = procs
        self._procs = []

        if self._server and (key is None or cert is None):
            raise Exception('Require key and cert for Server')

        try:
            os.unlink(unix_socket)
        except OSError:
            if os.path.exists(unix_socket):
                raise

    async def _remote_to_local(self, remote_reader, local_writer):
        try:
            while True:
                data = await remote_reader.read(65535)
                if not data:
                    break
                local_writer.write(data)
                await local_writer.drain()
        except Exception as err:
            log.critical(err)
        finally:
            local_writer.close()

    async def _local_to_remote(self, local_reader, remote_writer):
        try:
            while True:
                data = await local_reader.read(65535)
                if not data:
                    break
                remote_writer.write(data)
                await remote_writer.drain()
        except Exception as err:
            log.critical(err)
        finally:
            remote_writer.close()

    async def _handle_remote_connection(self, remote_reader, remote_writer):
        log.info("Client connected %s" %
                 str(remote_writer.get_extra_info('peername')))
        try:
            loop = asyncio.get_running_loop()
            local_reader, local_writer = await asyncio.open_unix_connection(
                self._unix_sock, loop=loop)

            lr_task = asyncio.create_task(self._local_to_remote(local_reader,
                                                                remote_writer))
            rl_task = asyncio.create_task(self._remote_to_local(remote_reader,
                                                                local_writer))
            await lr_task
            await rl_task
        except ssl.SSLError as err:
            log.critical('Connection from %s failed %s' % (self._host,
                                                           err,))
        except ConnectionError:
            log.critical('Connection from %s failed' % self._host)
        except Exception as err:
            log.critical(err)
        finally:
            remote_writer.close()

    async def _handle_local_connection(self, local_reader, local_writer):
        log.info("Client connected %s" % self._unix_sock)

        try:
            sc = ssl.create_default_context()
            sc.check_hostname = False
            if self._cert:
                sc.load_verify_locations(self._cert)
            else:
                sc.verify_mode = ssl.CERT_NONE

            loop = asyncio.get_running_loop()
            remote_reader, remote_writer = await asyncio.open_connection(
                self._host, 1983, ssl=sc, loop=loop)
            lr_task = asyncio.create_task(self._local_to_remote(local_reader,
                                                                remote_writer))
            rl_task = asyncio.create_task(self._remote_to_local(remote_reader,
                                                                local_writer))
            log.info("Connected to %s:1983" % self._host)
            await lr_task
            await rl_task
        except ssl.SSLError as err:
            log.critical('Connection to %s:1983 failed %s' % (self._host,
                                                              err,))
        except ConnectionError:
            log.critical('Connection to %s:1983 failed' % self._host)
        except Exception as err:
            log.critical(err)
        finally:
            local_writer.close()

    def _proc(self):
        log.info('Started Process')
        loop = asyncio.get_event_loop()
        if self._server:
            sc = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            sc.check_hostname = False
            sc.load_cert_chain(self._cert, self._key)
            coro = asyncio.start_server(self._handle_remote_connection,
                                        sock=self._listen_sock,
                                        ssl=sc, loop=loop)
            loop.run_until_complete(coro)
            loop.run_forever()
        else:
            coro = asyncio.start_server(self._handle_local_connection,
                                        sock=self._listen_sock,
                                        loop=loop)
            loop.run_until_complete(coro)
            loop.run_forever()

    def __enter__(self):
        self._lock.acquire()
        if self._server:
            log.info('Starting SSLServer')
            self._listen_sock = socket.socket(socket.AF_INET,
                                              socket.SOCK_STREAM)
            self._listen_sock.setsockopt(socket.SOL_SOCKET,
                                         socket.SO_REUSEADDR, 1)
            self._listen_sock.bind((self._host, 1983))
            self._listen_sock.setblocking(False)
            self._listen_sock.listen(65536)
            log.info('Serving on {}'.format(self._listen_sock.getsockname()))

            self._local_server_sock = socket.socket(socket.AF_UNIX,
                                                    socket.SOCK_STREAM)
            self._local_server_sock.bind(self._unix_sock)
            self._local_server_sock.setblocking(False)
            self._local_server_sock.listen(65536)
            log.info('Serving on {}'.format(
                self._local_server_sock.getsockname()))
        else:
            self._listen_sock = socket.socket(socket.AF_UNIX,
                                              socket.SOCK_STREAM)
            self._listen_sock.bind(self._unix_sock)
            self._listen_sock.listen(65536)
            log.info('Serving on {}'.format(self._listen_sock.getsockname()))

        for proc in range(self._procs_count):
            self._procs.append(Process(target=self._proc,
                                       name="SSLServer-%s" % proc,
                                       daemon=True))

        for proc in self._procs:
            proc.start()

        log.info('Started SSLServer')
        return SSLInterface(self)

    def __exit__(self, exception, message, traceback):
        log.info('SSLServer Shutdown')
        try:
            for proc in self._procs:
                log.info("Terminating Process '%s'" % proc.name)
                proc.terminate()
                proc.join()
                log.info("Terminated Process '%s'" % proc.name)
            self._procs.clear()

            if self._server:
                self._local_server_sock.close()
                self._local_server_sock = None
            self._listen_sock.close()
            self._listen_sock = None

            try:
                os.unlink(self._unix_sock)
            except OSError:
                if os.path.exists(self._unix_sock):
                    raise
        finally:
            log.info('SSLServer Shutdown Completed')
            self._lock.release()
