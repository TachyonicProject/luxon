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
File Queue Interface.
"""
import os
import pickle
from logging import getLogger
from time import sleep
from multiprocessing import Lock
from base64 import b64encode, b64decode


log = getLogger(__name__)


class BaseQueue(object):
    """FileQueue.

    LIFO Queue - Last in first out.
    """
    def __init__(self, path):
        self._file_path = path
        self._file = open(path, 'ab+', buffering=0)
        self._file_lock = Lock()
        self._get_lock = Lock()

    def fileno(self):
        return self._file.fileno()

    def __str__(self):
        return "FileQueue('%s')" % self._file_path

    def __repr__(self):
        return repr("FileQueue('%s')" % self._file_path)

    def reverse_readline(self, buf_size=262144):
        """A generator that returns the lines of a file in reverse order"""
        segment = None
        offset = 0
        self._file.seek(0, os.SEEK_END)
        file_size = remaining_size = self._file.tell()
        while remaining_size > 0:
            offset = min(file_size, offset + buf_size)
            self._file.seek(file_size - offset)
            buffer = self._file.read(min(remaining_size, buf_size))
            remaining_size -= buf_size
            lines = buffer.split(b'\n')
            # The first line of the buffer is probably not a complete line so
            # we'll save it and append it to the last line of the next buffer
            # we read
            if segment is not None:
                # If the previous chunk starts right from the beginning of line
                # do not concat the segment to the last line of new chunk.
                # Instead, yield the segment first
                if buffer[-1] != b'\n':
                    lines[-1] += segment
                else:
                    yield segment + b'\n'
            segment = lines[0]
            for index in range(len(lines) - 1, 0, -1):
                if lines[index]:
                    yield lines[index] + b'\n'
        # Don't yield None if the file was empty
        if segment is not None:
            yield segment + b'\n'

    def put(self, msg):
        try:
            self._file_lock.acquire()
            self._file.write(self._encode(msg))
            self._file.flush()
        except Exception:
            log.critical("Unable to put '%s' to %s" % (msg,
                                                       self))
        finally:
            self._file_lock.release()

    def _get(self, file_size, batch=None):
        batched = []
        read = 0
        for line in self.reverse_readline():
            read += len(line)
            if batch is None:
                self._file.truncate(file_size - read)
                self._file.flush()
                return self._decode(line)
            else:
                val = self._decode(line)
                if val:
                    batched.append(val)

                if len(batched) == batch:
                    self._file.truncate(file_size - read)
                    self._file.flush()
                    return batched
        if batch:
            self._file.truncate(file_size - read)
            self._file.flush()
            return batched
        else:
            return None

    def get(self, batch=None):
        while True:
            self._file.seek(0, os.SEEK_END)
            if self._file.tell() > 0:
                try:
                    self._file_lock.acquire()
                    self._file.seek(0, os.SEEK_END)
                    file_size = self._file.tell()
                    val = self._get(file_size, batch=batch)
                    if val:
                        return val
                finally:
                    self._file_lock.release()
            sleep(0.01)

    def get_nowait(self, batch=None):
        try:
            self._get_lock.acquire()
            self._file_lock.acquire()
            self._file.seek(0, os.SEEK_END)
            file_size = self._file.tell()
            if file_size > 0:
                return self._get(file_size, batch=batch)
        finally:
            self._file_lock.release()
            self._get_lock.release()


class PickleQueue(BaseQueue):
    def _encode(self, msg):
        return b64encode(pickle.dumps(msg, 4)) + b'\n'

    def _decode(self, line):
        try:
            return pickle.loads(b64decode(line))
        except Exception:
            log.critical("Unable to process '%s' in %s" % (line,
                                                           self))


class BytesQueue(BaseQueue):
    def _encode(self, msg):
        return b64encode(msg) + b'\n'

    def _decode(self, line):
        try:
            return b64decode(line)
        except Exception:
            log.critical("Unable to process '%s' in %s" % (line,
                                                           self))
