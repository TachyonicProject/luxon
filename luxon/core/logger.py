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
import logging
import logging.handlers
import multiprocessing
import traceback

from luxon import g
from luxon.exceptions import NoContextError
from luxon.utils.singleton import NamedSingleton
from luxon.utils.formatting import format_seconds
from luxon.utils.files import is_socket
from luxon.utils.split import list_of_lines, split_by_n
from luxon.utils.encoding import if_bytes_to_unicode
from luxon.utils.unique import string_id


log_format = logging.Formatter('%(asctime)s%(app_name)s' +
                               ' %(name)s' +
                               '[%(process)d][%(threadName)s]' +
                               ' <%(levelname)s>: %(message)s',
                               datefmt='%b %d %H:%M:%S')

simple_format = logging.Formatter('%(name)s' +
                                  '[%(process)d]' +
                                  ' <%(levelname)s>: %(message)s')


def log_formatted(logger_facility, message, prepend=None, append=None,
                  timer=None, log_id=None):
    """Using logger log formatted content

    Args:
        logger_facility (object): Python logger. (log.debug for example)
        content (str): Message to log.
    """
    try:
        log_items = list(g.current_request.log.items())
        log_items.append(('REQUEST-ID', g.current_request.id))
        request = " ".join(['(%s: %s)' % (key, value)
                           for (key, value) in log_items])
    except NoContextError:
        request = ''

    message = str(if_bytes_to_unicode(message)).strip()

    if message != '':
        if timer is not None:
            message += ' (DURATION: %s)' % format_seconds(timer)

        _message = list_of_lines(message)
        message = []
        for line in _message:
            # Safe Limit per message...
            # There is resrictions on message sizes.
            # https://tools.ietf.org/html/rfc3164
            # https://tools.ietf.org/html/rfc5426
            message += split_by_n(line, 300)

        if len(message) > 1:
            if log_id is None:
                log_id = string_id(6)

            if prepend is not None:
                logger_facility("(%s) #0 %s" % (log_id, prepend,))

            for line, p in enumerate(message):
                msg = '(%s) %s# %s' % (log_id, line+1, p)
                logger_facility(msg)

            if append is not None:
                logger_facility("(%s) #%s %s" % (log_id, line+2, append))
        else:
            if log_id is not None:
                msg = '(%s) ' % log_id
            else:
                msg = ''
            if prepend is not None:
                msg += '%s %s' % (prepend, message[0])
            else:
                msg += '%s' % message[0]

            if append is not None:
                msg = '%s %s' % (msg, append)

            msg = '%s %s' % (msg, request)

            logger_facility(msg)


class _TachyonFilter(logging.Filter):
    def __init__(self, app_name=None):
        logging.Filter.__init__(self)
        self.app_name = app_name

    def filter(self, record):
        try:
            record.app_name = ' ' + g.app.config.get('application',
                                                     'name',
                                                     fallback='')
            return True
        except NoContextError:
            pass

        if self.app_name:
            record.app_name = ' ' + self.app_name

        return True


def set_level(logger, level):
        try:
            level = int(level)
            logger.setLevel(level)
        except ValueError:
            level = level.upper().strip()
            if level in ['CRITICAL',
                         'ERROR',
                         'WARNING',
                         'INFO',
                         'DEBUG']:
                logger.setLevel(getattr(logging, level))
            else:
                raise ValueError("Invalid logging level '%s'" % level +
                                 " for logger" +
                                 " '%s'" % logger.name) from None


def configure(config, config_section, logger):
    if (config_section == 'application' and
            config_section not in config):

        # Clean/Remove Handlers
        for handler in logger.handlers:
            logger.removeHandler(handler)

        # DEFAULT Set Stdout
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.addFilter(_TachyonFilter())
        logger.addHandler(handler)
        handler.setFormatter(simple_format)

    if config_section in config:
        # Config Section
        section = config[config_section]

        # Giving out-of-context apps the opportunity to
        # specify a name
        if config_section == 'application' and 'name' in section:
            _tachyonfilter = _TachyonFilter(section['name'])
        else:
            _tachyonfilter = _TachyonFilter()

        # Clean/Remove Handlers
        for handler in logger.handlers:
            logger.removeHandler(handler)

        # Set Logger Level
        set_level(logger,
                  section.get('log_level',
                              fallback='WARNING'))

        # Set Stdout
        if section.getboolean('log_stdout', fallback=False):
            handler = logging.StreamHandler(stream=sys.stdout)
            handler.setFormatter(log_format)
            handler.addFilter(_tachyonfilter)
            logger.addHandler(handler)

        # Set Syslog
        host = section.get('log_server', fallback=None)
        if host is not None:
            port = section.get('log_server_port', fallback=514)
            if host == '127.0.0.1' or host.lower() == 'localhost':
                if is_socket('/dev/log'):
                    handler = logging.handlers.SysLogHandler(
                        address='/dev/log')
                elif is_socket('/var/run/syslog'):
                    handler = logging.handlers.SysLogHandler(
                        address='/var/run/syslog')
                else:
                    handler = logging.handlers.SysLogHandler(
                        address=(host, port))
            else:
                handler = logging.handlers.SysLogHandler(address=(host, port))

            handler.setFormatter(log_format)
            handler.addFilter(_tachyonfilter)
            logger.addHandler(handler)

        # ENABLE FILE LOG FOR GLOBAL OR MODULE
        log_file = section.get('log_file', fallback=None)
        if log_file is not None:
            handler = logging.FileHandler(log_file)

            handler.setFormatter(log_format)
            handler.addFilter(_tachyonfilter)
            logger.addHandler(handler)


class MPLogger(object):
    _queue = multiprocessing.Queue(-1)

    def __init__(self, name):
        self._log_proc = None
        self._name = name
        if self._name == "__main__":
            self._logger = logging.getLogger(name)
        else:
            root = logging.getLogger()
            root.handlers = [logging.handlers.QueueHandler(MPLogger._queue)]

            for logger in logging.Logger.manager.loggerDict:
                sub_logger = logging.Logger.manager.loggerDict[logger]
                if isinstance(sub_logger, logging.Logger):
                    sub_logger.handlers = []

            self._logger = logging.getLogger(name)

    def receive(self):
        def receiver(queue):
            try:
                while True:
                    record = queue.get()
                    # Get Logger
                    logger = logging.getLogger(record.name)

                    # No level or filter logic applied - just do it!
                    logger.handle(record)
            except Exception:
                print('Whoops! Problem:', file=sys.stderr)
                traceback.print_exc(file=sys.stderr)

        if self._name == "__main__":
            self._log_proc = multiprocessing.Process(target=receiver,
                                                     name='Logger',
                                                     args=(MPLogger._queue,))
            self._log_proc.start()

    def close(self):
        if self._name == "__main__":
            if self._log_proc is not None:
                self._log_proc.terminate()

    def critical(self, msg):
        self._logger.critical(msg)

    def error(self, msg):
        self._logger.error(msg)

    def warning(self, msg):
        self._logger.warning(msg)

    def info(self, msg):
        self._logger.info(msg)

    def debug(self, msg):
        self._logger.debug(msg)


class GetLogger(metaclass=NamedSingleton):
    """Wrapper Class for convienance.

    Args:
        name (str): Typical Module Name, sub-logger name, (optional)

    Ensures all log output is formatted correctly.
    """
    __slots__ = ('name',
                 'logger',)

    def __init__(self, name=None):
        self.logger = logging.getLogger(name)

        if not name:
            # DEFAULT Set Stdout
            handler = logging.StreamHandler(stream=sys.stdout)
            handler.addFilter(_TachyonFilter())
            self.logger.addHandler(handler)
            handler.setFormatter(simple_format)

    @property
    def level(self):
        return self.logger.getEffectiveLevel()

    @level.setter
    def level(self, level):
        set_level(self.logger, level)

    def configure(self, config):
        # Configure Root
        configure(config, 'application', logging.getLogger())

        # Configure Sub-Loggers
        for logger in logging.Logger.manager.loggerDict:
            sub_logger = logging.Logger.manager.loggerDict[logger]
            if isinstance(sub_logger, logging.Logger):
                configure(config, logger, sub_logger)

    def critical(self, msg, prepend=None, append=None, timer=None,
                 log_id=None):
        """Log Critical Message.

        Args:
            msg (str): Log Message.
            prepend (str): Prepend Message (optional)
            append (str): Append Message (optional)

            timer (int): Integer value in ms.
                Usually from :class:`luxon.utils.timer.Timer`
                Adds (DURATION: time) to log entry.

        """
        if self.level <= logging.CRITICAL:
            log_formatted(self.logger.critical, msg, prepend, append, timer,
                          log_id)

    def error(self, msg, prepend=None, append=None, timer=None, log_id=None):
        """Log Error Message.

        Args:
            msg (str): Log Message.
            prepend (str): Prepend Message (optional)
            append (str): Append Message (optional)

            timer (int): Integer value in ms.
                Usually from :class:`luxon.utils.timer.Timer`
                Adds (DURATION: time) to log entry.

        """
        if self.level <= logging.ERROR:
            log_formatted(self.logger.error, msg, prepend, append, timer,
                          log_id)

    def warning(self, msg, prepend=None, append=None, timer=None, log_id=None):
        """Log Warning Message.

        Args:
            msg (str): Log Message.
            prepend (str): Prepend Message (optional)
            append (str): Append Message (optional)

            timer (int): Integer value in ms.
                Usually from :class:`luxon.utils.timer.Timer`
                Adds (DURATION: time) to log entry.

        """
        if self.level <= logging.WARNING:
            log_formatted(self.logger.warning, msg, prepend, append, timer,
                          log_id)

    def info(self, msg, prepend=None, append=None, timer=None, log_id=None):
        """Log Info Message.

        Args:
            msg (str): Log Message.
            prepend (str): Prepend Message (optional)
            append (str): Append Message (optional)

            timer (int): Integer value in ms.
                Usually from :class:`luxon.utils.timer.Timer`
                Adds (DURATION: time) to log entry.

        """
        if self.level <= logging.INFO:
            log_formatted(self.logger.info, msg, prepend, append, timer,
                          log_id)

    def debug(self, msg, prepend=None, append=None, timer=None, log_id=None):
        """Log Debug Message.

        Args:
            msg (str): Log Message.
            prepend (str): Prepend Message (optional)
            append (str): Appener value returned using

            timer (int): Integer value in ms.
                Usually from :class:`luxon.utils.timer.Timer`
                Adds (DURATION: time) to log entry.

        """
        if self.level <= logging.DEBUG:
            log_formatted(self.logger.debug, msg, prepend, append, timer,
                          log_id)
