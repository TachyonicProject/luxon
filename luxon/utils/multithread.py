# -*- coding: utf-8 -*-
# Copyright (c) 2019 Christiaan Rademan <christiaan.rademan@gmail.com>
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
# import sys
import os
import ctypes
from time import sleep
import traceback
from threading import Thread as PYThread
from luxon.utils.multiproc import End
from luxon.core.logger import GetLogger
import threading

log = GetLogger(__name__)


class ThreadManager(object):
    __slots__ = ('_threads', '_restart')

    def __init__(self):
        self._threads = {}
        self._restart = []

    def new(self, target, name, restart=False, args=(), kwargs={}):
        if name in self._threads:
            raise ValueError("Duplicate thread '%s'" % name)
        self._threads[name] = Thread(target, name, args=args, kwargs=kwargs)
        if restart:
            self._restart.append(name)

    def _get_thread(self, name):
        try:
            return self._threads[name]
        except KeyError:
            raise ValueError("No such thread '%s'" % name)

    def alive(self, name):
        thread = self._get_thread(name)
        return thread.alive

    def start(self):
        for thread in self._threads:
            log.info("Starting thread '%s'" % self._threads[thread].name)
            self._threads[thread].start()

        try:
            while True:
                if not self._threads:
                    break
                else:
                    for thread_name in self._threads.copy():
                        thread = self._threads[thread_name]
                        if not thread.alive:
                            if thread_name in self._restart:
                                log.info("Restarting thread '%s'"
                                         % thread.name)
                                thread.restart()
                            else:
                                del self._threads[thread_name]
                sleep(1)
        except End:
            log.error('ThreadManager ended (Shutdown)')
        except SystemExit:
            log.error('ThreadManager ended (System Exit)')
        except KeyboardInterrupt:
            log.error('ThreadManager ended (Keyboard Interrupt)')
        except Exception:
            log.critical('Thread ended (Unhandled Exception)'
                         '\n%s' % str(traceback.format_exc()))


class Thread(object):
    __slots__ = ('_target', '_name', '_args', '_kwargs', '_thread', '_exit')

    def __init__(self, target, name, args=(), kwargs={}):
        self._target = target
        self._name = name
        self._args = args
        self._kwargs = kwargs
        self._thread = self._new()
        self._exit = False

    def _new(self):
        def _thread(*args, **kwargs):
            try:
                self._target(*args, **kwargs)
            except End:
                pass
            except SystemExit:
                log.error('Thread ended (System Exit)')
            except KeyboardInterrupt:
                log.error('Thread ended (Keyboard Interrupt)')
            except Exception:
                log.critical('Thread ended (Unhandled Exception)'
                             '\n%s' % str(traceback.format_exc()))

        return PYThread(target=_thread,
                        name=self._name,
                        args=self._args,
                        kwargs=self._kwargs,
                        daemon=True)

    @property
    def name(self):
        return self._name

    @property
    def ident(self):
        return self._thread.ident

    @property
    def alive(self):
        return self._thread.is_alive()

    def terminate(self):
        self._exit = True

    def join(self):
        return self._thread.join()

    def start(self):
        self._thread.start()

    def restart(self):
        self.join()

        self._thread = self._new()
        self.start()
