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

import sys
import os
import time
import atexit
from signal import SIGTERM


class Daemon(object):
    """Generic Daemon class.

    Usage options:
        1. Use as context with Daemon:
        2. Subclass the Daemon class and override the run() method
        3. Define method to run via keyword arguements.
    """
    def __init__(self, pidfile, run=None, args=[], kwargs={},
                 stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self._run = run
        self._args = args
        self._kwargs = kwargs

    def _daemonize(self):
        """Daemonize Process

        Do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        # Do the first fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit first parent
                sys.exit(0)

        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n"
                             % (e.errno, e.strerror))
            sys.exit(1)

        # Decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # Do the second fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit from second parent
                sys.exit(0)

        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n"
                             % (e.errno, e.strerror))
            sys.exit(1)

        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'wb', 0)
        se = open(self.stderr, 'wb', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        self.write_pid()

    def write_pid(self):
        # Write PID File
        atexit.register(self.delete_pid)
        pid = str(os.getpid())
        open(self.pidfile, 'w+').write("%s\n" % pid)

    def delete_pid(self):
        try:
            os.remove(self.pidfile)
        except FileNotFoundError:
            pass

    def daemonize(self):
        """Start the daemon
        """
        # Check for a Pid File to see if the daemon is already running.
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            try:
                os.kill(pid, 0)
                message = "running pid %s and pidfile %s already exist." +\
                          " Daemon already running?\n"
                sys.stderr.write(message % (pid, self.pidfile))
                sys.exit(1)
                return False
            except OSError:
                pid = None

        # Start the daemon.
        self._daemonize()

    def start(self, fork=True):
        if fork is True:
            self.daemonize()
        else:
            if self.running:
                pid = str(os.getpid())
                message = "running pid %s and pidfile %s already exist." +\
                          " Daemon already running?\n"
                sys.stderr.write(message % (pid, self.pidfile))
                exit()
            self.write_pid()
        self.run()

    def stop(self):
        """Stop the daemon
        """
        # Get the pid from the Pid File.
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return

        # Try killing the daemon process.
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
                else:
                    print(str(err))
                    sys.exit(1)

    @property
    def running(self):
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except (IOError, ValueError):
            return False

        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    @property
    def get_pid(self):
        if self.running:
            try:
                pf = open(self.pidfile, 'r')
                pid = int(pf.read().strip())
                pf.close()
                return pid
            except IOError:
                pass
        return None

    def restart(self):
        """Restart the daemon
        """
        self.stop()
        self.start()

    def __enter__(self):
        self.daemonize()

    def __exit__(self, type, value, traceback):
        self.delete_pid()

    def run(self):
        """Method to run daemonized

        You should override this method when you subclass Daemon.
        It will be called after the process has been
        daemonized by start() or restart().
        """
        if self._run is not None:
            self._run(*self._args, **self._kwargs)
        else:
            raise NotImplementedError('No run method defined or run ' +
                                      ' function provided')
