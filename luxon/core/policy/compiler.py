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

import re

from luxon.utils.timer import Timer
from luxon.core.logger import GetLogger
from luxon.utils.singleton import Singleton

log = GetLogger(__name__)

def compiler(dict_rule_set):
    """Policy Rules Compiler.

    Compiles rule set into python executable machine code for enhanced
    performance during conditional matching.

    Example of rule_set in dict format:
        { 'role:admin': '"admin" in role_kwarg',
          'user:login': '"login_kwarg" is True',
          'match:both': '$role:admin or $system:login' }

        The syntax for the rule is exactly as per python conditional
        statements. Note these statements can be nested using braces ().

    Args:
        dict_rule_set (dict): Rule Set loaded from JSON file for example.
    """

    with Timer() as elapsed:
        # MATCH : expression used within rule statements.
        interpolation_match = re.compile(r"\$[a-z_\-:]+", re.IGNORECASE)

        # Build Rules - Need todo this before compiling.
        # Some rules reference others.
        rule_set = '_validate_result = False\n'
        rule_set += '_rules = {}\n\n'

        for rule in dict_rule_set:
            # Validate Rules.
            if ' ' in rule:
                log.error("Error in rule name '" + rule +
                          "' skipping. (expected value with no spaces)" )
                continue

            log.info('Build rule %s = %s' % (rule, dict_rule_set[rule]))
            condition = dict_rule_set[rule]

            build_rule = ('def ' + rule.replace(':','_') +
                          '():\n    return ' +
                          condition + '\n')

            # Correct build_rule for interpolation.
            # Any string with '$value' is an expression.
            for expr in interpolation_match.findall(build_rule):
                if expr[1:] not in dict_rule_set:
                    log.error("Missing rule for interpolation of '" + expr +
                              "' in rule '" + rule + "' skipping.")
                    build_rule = build_rule.replace(expr, 'False')
                    continue

                build_rule = build_rule.replace(expr, expr.replace(':',
                                                                   '_')[1:] +
                                                '()')

            # Add Rule to _rules dictionary for validation to select rule.
            build_rule += "_rules['" + rule + "'] = " + rule.replace(':','_')
            build_rule += '\n\n'

            rule_set += build_rule

        rule_set += '_validate_result = _rules[_validate_rule]()\n'

        # Compile Rules
        try:
            compiled = compile(rule_set, 'policy.json.compiled', 'exec')
            log.info('%s Rules compile completed.' % len(dict_rule_set),
                      timer=elapsed())

            return (compiled, dict_rule_set)
        except Exception:
            raise ValueError("Failed compiling rule_set")

