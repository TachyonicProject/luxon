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
import ssl
import struct
import socket
import select
import pickle
from multiprocessing import Lock


def recv_pickle(sock):
    header = sock.read(8)
    length = struct.unpack('!Q', header)[0]
    payload = sock.read(length)
    return pickle.loads(payload)


def send_pickle(sock, data):
    payload = pickle.dumps(data, 4)
    sock.write(struct.pack('!Q', len(payload)) + payload)
    return True


class Socket(object):
    def __init__(self, sock, addr=None):
        self._sock_lock = Lock()
        self._transaction_lock = Lock()
        self._sock = sock
        self._addr = addr
        self._closed = False

    def _check_closed(self):
        if self._closed:
            raise ConnectionError('Connection closed')

    @property
    def raw_socket(self):
        return self._sock

    @property
    def addr(self):
        return self._addr

    def setblocking(self, value):
        self._check_closed()
        try:
            self._sock_lock.acquire()
            self._sock.setblocking(bool(value))
        finally:
            self._sock_lock.release()

    def settimeout(self, value):
        self._check_closed()
        try:
            self._sock_lock.acquire()
            try:
                self._sock.setblocking(True)
                self._sock.settimeout(float(value))
            except ValueError:
                self._sock.settimeout(None)
        finally:
            self._sock_lock.release()

    def fileno(self):
        self._check_closed()
        try:
            self._sock_lock.acquire()
            return self._sock.fileno()
        finally:
            self._sock_lock.release()

    def read(self, length=2, timeout=None):
        self._check_closed()
        if timeout and float(timeout) < float(0):
            timeout = None
        self._sock_lock.acquire()
        try:
            buf = b''
            while True:
                data = b''
                try:
                    if timeout is not None and timeout <= 0:
                        raise socket.timeout('Socket Read Timeout')
                    # Should be ready to read
                    try:
                        select.select([self._sock], [], [], timeout)
                    except ValueError:
                        return b''
                    data = self._sock.recv(length)
                    if data:
                        buf += data
                        length -= len(data)
                    else:
                        self._close()
                        raise ConnectionError('Connection closed')
                    if length == 0:
                        return buf
                    try:
                        select.select([self._sock], [], [], timeout)
                    except ValueError:
                        return b''
                    if timeout:
                        timeout -= timeout
                except (BlockingIOError, ssl.SSLWantReadError):
                    # Resource temporarily unavailable (errno EWOULDBLOCK)
                    try:
                        select.select([self._sock], [], [], timeout)
                    except ValueError:
                        return b''
                    if timeout:
                        timeout -= timeout
        finally:
            self._sock_lock.release()

    def write(self, data, timeout=None):
        self._check_closed()
        totalsent = 0
        data_size = len(data)
        if timeout and float(timeout) < float(0):
            timeout = None
        try:
            self._sock_lock.acquire()
            while True:
                try:
                    while totalsent < data_size:
                        select.select([], [self._sock], [], timeout)
                        if timeout is not None and timeout <= 0:
                            raise socket.timeout('Socket Write Timeout')
                        sent = self._sock.send(data[totalsent:])
                        if sent == 0:
                            raise RuntimeError("socket connection broken")
                        totalsent += sent
                    return totalsent
                except (BlockingIOError, ssl.SSLWantWriteError):
                    # Resource temporarily unavailable (errno EWOULDBLOCK)
                    select.select([], [self._sock], [], timeout)
                    if timeout:
                        timeout -= timeout
                except BrokenPipeError:
                    self._close()
                    raise ConnectionError('Connection closed')
        finally:
            self._sock_lock.release()

    def recv(self, max_size=64):
        self._check_closed()
        try:
            self._sock_lock.acquire()
            return self._sock.recv(max_size)
        finally:
            self._sock_lock.release()

    def send(self, data):
        self._check_closed()
        try:
            self._sock_lock.acquire()
            return self._sock.send(data)
        finally:
            self._sock_lock.release()

    def sendall(self, data):
        self._check_closed()
        try:
            self._sock_lock.acquire()
            return self._sock.sendall(data)
        finally:
            self._sock_lock.release()

    def _close(self):
        self._closed = True
        try:
            self._sock.send(b'')
        except Exception:
            pass
        try:
            return self._sock.close()
        except Exception:
            pass

    def close(self):
        try:
            self._sock_lock.acquire()
            return self._close()
        finally:
            try:
                self._sock_lock.release()
            except ValueError:
                pass

    def __enter__(self):
        self._check_closed()
        self._transaction_lock.acquire()
        return self

    def __exit__(self, exception, value, traceback):
        self._transaction_lock.release()


def Pipe():
    sock1, sock2 = socket.socketpair()
    sock1.setblocking(False)
    sock2.setblocking(False)
    return (Socket(sock1), Socket(sock2),)
