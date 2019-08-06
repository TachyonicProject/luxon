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
import os
import time
import traceback
import threading
from time import sleep
from multiprocessing import Process as PYProcess

from luxon.core.logger import GetLogger
from luxon.core.logger import MPLogger
from luxon.utils.daemon import GracefulKiller

log = GetLogger(__name__)


def dead(procs):
    for proc in procs.copy():
        if not proc.is_alive():
            if isinstance(proc, threading.Thread):
                log.error("Thread '%s' died" % proc.name)
            else:
                log.error("Process '%s' died" % proc.name)
            procs.remove(proc)


def join(procs):
    while procs:
        for proc in procs.copy():
            if proc.is_alive():
                if isinstance(proc, threading.Thread):
                    log.error("Waiting for thread '%s' to end" % proc.name)
                else:
                    log.error("Waiting for process '%s' to end" % proc.name)
            else:
                if isinstance(proc, threading.Thread):
                    log.error("Thread '%s' ended" % proc.name)
                else:
                    log.error("Process '%s' ended" % proc.name)
                procs.remove(proc)
            if procs:
                time.sleep(1)


class End(Exception):
    pass


class ProcessManager(object):
    # __slots__ = ('_procs', '_restart', '_mplogger', '_manager_pid')

    def __init__(self):
        self._dead = False
        self._manager_pid = os.getpid()
        self._procs = {}
        self._restart = []
        self._mplogger = MPLogger('__main__')

    def new(self, target, name, restart=False, args=(), kwargs={}):
        if name in self._procs:
            raise ValueError("Duplicate Process '%s'" % name)
        self._procs[name] = Process(target,
                                    name,
                                    self._mplogger.queue,
                                    args=args,
                                    kwargs=kwargs)
        if restart:
            self._restart.append(name)

    def _get_proc(self, name):
        try:
            return self._procs[name]
        except KeyError:
            raise ValueError("No such process '%s'" % name)

    def terminate(self, name):
        proc = self._get_proc(name)
        if proc.alive:
            log.info("Terminating process '%s'" % proc.name)
            proc.terminate()
        del self._procs[name]
        if name in self._restart:
            self._restart.remove(name)

    def alive(self, name):
        proc = self._get_proc(name)
        return proc.alive

    def join(self, name):
        proc = self._get_proc(name)
        return proc.join()

    def start(self):
        def end(signal):
            if self._manager_pid != os.getpid():
                if (threading.current_thread() is
                        threading.main_thread()):
                    raise SystemExit()

        sig = GracefulKiller(end)

        for proc in self._procs:
            log.info("Starting process '%s'" % self._procs[proc].name)
            self._procs[proc].start()

        self._mplogger.receive()

        try:
            while True:
                if sig.killed or not self._procs:
                    break
                else:
                    for proc_name in self._procs.copy():
                        proc = self._procs[proc_name]
                        if not proc.alive:
                            if proc_name in self._restart:
                                log.info("Restarting process '%s'" % proc.name)
                                self._mplogger.close()
                                proc.restart()
                                self._mplogger.receive()
                            else:
                                self.terminate(proc_name)
                sleep(1)

            for proc in self._procs:
                self._procs[proc]._proc.terminate()

            self._mplogger.close()
        except (SystemExit, KeyboardInterrupt):
            for proc in self._procs:
                self._procs[proc].terminate()

            self._mplogger.close()


class Process(object):
    __slots__ = ('_target', '_name', '_args', '_kwargs', '_proc')

    def __init__(self, target, name, log_queue, args=(), kwargs={}):

        self._target = target
        self._name = name
        self._args = (log_queue,) + args
        self._kwargs = kwargs
        self._proc = self._new()

    def _new(self):
        def _process(log_queue, *args, **kwargs):
            MPLogger(self._name, log_queue)

            try:
                self._target(*args, **kwargs)
            except SystemExit:
                log.error('Process ended (System Exit)')
            except KeyboardInterrupt:
                log.error('Process ended (Keyboard Interrupt)')
            except Exception:
                log.critical('Process ended (Unhandled Exception)'
                             '\n%s' % str(traceback.format_exc()))

        return PYProcess(target=_process,
                         name=self._name,
                         args=self._args,
                         kwargs=self._kwargs,
                         daemon=False)

    @property
    def name(self):
        return self._name

    @property
    def alive(self):
        return self._proc.is_alive()

    def join(self):
        return self._proc.join()

    def terminate(self):
        if self.alive:
            self._proc.terminate()
        else:
            self._proc.join()

    def start(self):
        self._proc.start()

    def restart(self):
        if not self.alive:
            self.join()
        else:
            self.terminate()
            self.join()

        self._proc = self._new()
        self.start()
