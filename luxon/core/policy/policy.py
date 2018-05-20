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

from luxon.utils.timer import Timer
from luxon.core.logger import GetLogger
from luxon.core.policy import compiler
from luxon.exceptions import AccessDeniedError

log = GetLogger(__name__)


class Policy(object):
    """Policy Rule Engine interface.

    Used to validate rules against environmental arguements provided as kwargs.

    rule_set can be provided which will be compiled for better performance.

    Example of rule_set in dict format:
        { 'role:admin': '"admin" in role_kwarg',
          'user:login': '"login_kwarg" is True',
          'match:both': 'role:admin or system:login' }

        The syntax for the rule is exactly as per python conditional
        statements. Note these statements can be nested using braces ().

        By default following kwargs are given to policy runtime in wsgi:
            * req being equel to the Request Object for the request.

    Keyword Args:
        rule_set (dict): Rule Set in dict loaded from JSON file for example.
    """
    __slots__ = ('_kwargs',
                 '_compiled',
                 '_rule_set')

    def __init__(self, rule_set=None, **kwargs):
        self._kwargs = kwargs
        if isinstance(rule_set, dict):
            self._compiled, self._rule_set = compiler(rule_set)
        else:
            self._compiled, self._rule_set = rule_set

    def validate(self, rule):
        """Validate Access to view.

        Args:
            view (str): View Name
        """
        # Default Value
        val = False

        if rule not in self._rule_set:
            log.error("No such rule '%s'" % rule)
            return val

        # Import bit, ensures save environment...
        exec_globals = { '__builtins__': {} }
        exec_globals = { '_validate_rule': rule }

        # Add Policy environment Kwargs to be referenced in rule_set.
        exec_globals.update(self._kwargs)

        try:
            with Timer() as elapsed:
                # Execute compiled rule_set code.
                exec(self._compiled, exec_globals, exec_globals)
                # Value from compiled code.
                val = exec_globals['_validate_result']
            log.info('Rule %s validated to %s.' % (rule, val),
                      timer=elapsed())
        except AccessDeniedError:
            raise
        except Exception as e:
            log.error("Failed validating '%s' %s:%s" %
                              (rule, e.__class__.__name__, e))
        return val
