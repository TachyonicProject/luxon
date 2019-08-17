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
from luxon.core.handlers.request import RequestBase


class Request(RequestBase):
    """Represents a cmd request.

    Args:
        method (str): Command action argument.
        route (str): Path to indicate resource location.
    """

    __slots__ = (
        'tag',
        'method',
        'route',
        'route_kwargs',
        'response',
        'log',
    )

    def __init__(self, method, route):
        super().__init__()
        # Response Object for Request
        self.response = None

        # Set HTTP Request Method - Router uses this.
        self.method = method

        self.route = route or '/'

        self.log = {}

    @property
    def stream(self):
        """Returns sys.stdin"""
        return sys.stdin

    @property
    def id(self):
        raise NotImplementedError('CMD has no request-id')

    @property
    def raw(self):
        """Returns sys.stdin"""
        return sys.stdin

    def read(self, size=None):
        """Read at most size, returned as a str object.

        Keyword Args:
            size (int): Size to read.

        Returns:
            str: str within the request payload.
        """
        return self.stream.read(size)
