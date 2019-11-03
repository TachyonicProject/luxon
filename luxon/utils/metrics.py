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

BYTES_AVAILABLE_UNITS = ['Bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']


def bytes_metric(byte_amount):
    for index, unit in enumerate(BYTES_AVAILABLE_UNITS):
        lower_threshold = 0 if index == 0 else 1024 ** (index - 1)
        upper_threshold = 1024 ** index
        if lower_threshold <= byte_amount < upper_threshold:
            if lower_threshold == 0:
                val = str(round(byte_amount, 2))
                return val + unit
            else:
                val = str(round(byte_amount / lower_threshold, 2))
                return val + BYTES_AVAILABLE_UNITS[index - 1]
    # Default to the maximum
    max_index = len(BYTES_AVAILABLE_UNITS) - 1
    val = str(round(byte_amount / (1024 ** max_index), 2))
    return val + BYTES_AVAILABLE_UNITS[max_index]


AVAILABLE_UNITS = ['', 'K', 'M', 'B', 'T', 'Q']


def unit_metric(amount):
    for index, unit in enumerate(AVAILABLE_UNITS):
        lower_threshold = 0 if index == 0 else 1000 ** (index - 1)
        upper_threshold = 1000 ** index
        if lower_threshold <= amount < upper_threshold:
            if lower_threshold == 0:
                val = str(round(amount, 2))
                return val + unit
            else:
                val = str(round(amount / lower_threshold, 2))
                return val + AVAILABLE_UNITS[index - 1]
    # Default to the maximum
    max_index = len(AVAILABLE_UNITS) - 1
    val = str(round(amount / (1000 ** max_index), 2))
    return val + AVAILABLE_UNITS[max_index]
