# -*- coding: utf-8 -*-
# Copyright (c) 2018 Christiaan Frans Rademan.
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

from luxon import g
from luxon.exceptions import NoContextError
from luxon.core.cls.singleton import NamedSingleton
from luxon.utils.formatting import format_seconds
from luxon.utils.files import is_socket
from luxon.utils.split import list_of_lines, split_by_n
from luxon.utils.encoding import if_bytes_to_unicode
from luxon.utils.unique import string_id


log_format = logging.Formatter('%(asctime)s%(app_name)s' +
                               ' %(name)s' +
                               '[%(process)d]' +
                               ' <%(levelname)s>: %(message)s',
                               datefmt='%b %d %H:%M:%S')


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
    if timer is not None:
        message += ' (DURATION: %s)' % format_seconds(timer)

    _message = list_of_lines(message)
    message = []
    for line in _message:
        # Safe Limit per message...
        # There is resrictions on message sizes.
        # https://tools.ietf.org/html/rfc3164
        # https://tools.ietf.org/html/rfc5426
        message += split_by_n(line, 500)

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
    def __init__(self):
        logging.Filter.__init__(self)

    def filter(self, record):
        try:
            record.app_name = ' ' + g.config.get('application',
                                                 'name',
                                                 fallback='')
        except NoContextError:
            record.app_name = ''

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


def configure(config_section, logger):
    if config_section in g.config:
        # Config Section
        section = g.config[config_section]

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
            handler.addFilter(_TachyonFilter())
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
            handler.addFilter(_TachyonFilter())
            logger.addHandler(handler)

        # ENABLE FILE LOG FOR GLOBAL OR MODULE
        log_file = section.get('log_file', fallback=None)
        if log_file is not None:
            handler = logging.FileHandler(log_file)

            handler.setFormatter(log_format)
            handler.addFilter(_TachyonFilter())
            logger.addHandler(handler)


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

    @property
    def level(self):
        return self.logger.getEffectiveLevel()

    @level.setter
    def level(self, level):
        set_level(self.logger, level)

    def configure(self):
        # Configure Root
        configure('application', logging.getLogger())

        # Configure Sub-Loggers
        for logger in logging.Logger.manager.loggerDict:
            sub_logger = logging.Logger.manager.loggerDict[logger]
            if isinstance(sub_logger, logging.Logger):
                configure(logger, sub_logger)

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
