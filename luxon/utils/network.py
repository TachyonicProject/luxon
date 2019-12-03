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
import select
import socket
import ssl
from multiprocessing import Lock


def get_addr_info(addr):
    """Use getaddrinfo to lookup all addresses for each address.

    Returns a list of tuples or an empty list:
      [(family, address)]
    """
    results = set()
    try:
        tmp = socket.getaddrinfo(addr, 'www')
    except socket.gaierror:
        return []

    for el in tmp:
        results.add((el[0], el[4][0]))

    return results


class SocketIO(object):
    def __init__(self, sock):
        self._lock = Lock()
        self._sock = sock

    def fileno(self):
        return self._sock.fileno()

    def read(self, length=2):
        while True:
            buf = b''
            try:
                self._lock.acquire()
                # Should be ready to read
                data = self._sock.recv(length)
                if data:
                    buf += data
                    length -= len(data)
                else:
                    raise socket.error('Peer closed')
                if length == 0:
                    return buf
                select.select([self._sock], [], [])
            except (BlockingIOError, ssl.SSLWantReadError):
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                select.select([self._sock], [], [])
            finally:
                self._lock.release()

    def write(self, bytes):
        while True:
            try:
                self._lock.acquire()
                return self._sock.sendall(bytes)
            except (BlockingIOError, ssl.SSLWantWriteError):
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                select.select([], [self._sock], [])
            finally:
                self._lock.release()


class Socket(object):
    def __init__(self, sock, addr):
        self._lock = Lock()
        self._sock = sock
        self._addr = addr

    @property
    def addr(self):
        return self._addr

    def fileno(self):
        return self._sock.fileno()

    def __enter__(self):
        self._lock.acquire()
        return SocketIO(self._sock)

    def __exit__(self, exception, value, traceback):
        self._lock.release()


def ssl_handshake(sock):
    while True:
        try:
            sock.do_handshake()
            break
        except ssl.SSLWantReadError:
            select.select([sock], [], [])
        except ssl.SSLWantWriteError:
            select.select([], [sock], [])


class ClientSocket(Socket):
    def startssl(self, cert=None, verify=True):
        context = ssl.create_default_context()
        context.check_hostname = False
        if verify is False:
            context.verify_mode = ssl.CERT_NONE
        else:
            if cert:
                context.load_verify_locations(cert)
            else:
                raise Exception('Require SSL Certificate')
        try:
            self._sock = context.wrap_socket(self._sock,
                                             do_handshake_on_connect=False)
            ssl_handshake(self._sock)
        except ssl.SSLError as err:
            print(err)


class ServerSocket(Socket):
    def startssl(self, cert, key):
        context = ssl.create_default_context()
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert, key)
        try:
            self._sock = context.wrap_socket(self._sock,
                                             server_side=True,
                                             do_handshake_on_connect=False)
            ssl_handshake(self._sock)
        except ssl.SSLError as err:
            print(err)


class TCPClient(object):
    def __init__(self, host, port):
        self._host = host
        self._port = port

    def connect(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.connect((self._host, self._port))
            return ClientSocket(self._sock, None)
        except Exception:
            self._sock.close()
            raise

    def close(self):
        self._sock.close()

    def __enter__(self):
        return self.connect()

    def __exit__(self, exception, value, traceback):
        self.close()


class UDPClient(object):
    def __init__(self, host, port, blocking=True):
        self._host = host
        self._port = port
        self._blocking = blocking

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.connect((self._host, self._port))
        self._sock.setblocking(self._blocking)
        return ClientSocket(self._sock, None)

    def close(self):
        self._sock.close()

    def __enter__(self):
        return self.connect()

    def __exit__(self, exception, value, traceback):
        self.close()


class Server(object):
    def __init__(self):
        self._sockets = {}
        self._lock = Lock()

    def bind4_tcp(self, addr, port, callback=None, backlog=65536):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((addr, port))
        sock.setblocking(False)
        sock.listen(backlog)
        self._sockets[sock] = (callback, addr, port, 0)

    def bind4_udp(self, addr, port, callback=None, blocking=True):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((addr, port))
        sock.setblocking(False)
        self._sockets[sock] = (callback, addr, port, 1)

    def _run_until_complete(self, timeout=None):
        read, write, exc = select.select(self._sockets.keys(),
                                         [],
                                         [],
                                         timeout)
        for sock in read:
            callback, addr, port, typ = self._sockets[sock]
            if typ == 0:
                # Requires ACCEPT for example TCP
                sock, addr = sock.accept()
                if callback:
                    callback(ServerSocket(sock, addr))
                else:
                    return ServerSocket(sock, addr)
            elif typ == 1:
                # No Session for example UDP
                if callback:
                    callback(ServerSocket(sock, None))
                else:
                    return ServerSocket(sock, addr)

    def ioloop(self, timeout=None):
        try:
            self._lock.acquire()
            self._running = True
            while self._running:
                socket = self._run_until_complete(timeout=timeout)
                if socket:
                    return socket
                if timeout is not None:
                    break
        finally:
            self._running = False
            self._lock.release()

    def stop(self):
        self._running = False
        try:
            self._lock.acquire()
            for sock in self._sockets.keys():
                sock.close()
            self._sockets = {}
        finally:
            self._lock.release()
