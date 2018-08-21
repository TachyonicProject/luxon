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
import hashlib

from luxon.utils.encoding import if_unicode_to_bytes
from luxon.exceptions import NotFoundError
from luxon.utils import js


PARTITIONS = 256


def shard(string):
    hashed = 0
    for h in hashlib.md5(string).digest():
        hashed += h

    return hashed % PARTITIONS


class Partition(object):
    def __init__(self, nodes, replicas=1):
        if len(nodes) == 0:
            raise NotFoundError('No nodes found')

        self._nodes = nodes
        self._replicas = replicas
        self._partitions = []
        number_of_nodes = len(nodes)
        counter = 0

        for partition in range(PARTITIONS):
            partition_nodes = []

            for replicate in range(replicas):
                node = counter % number_of_nodes
                partition_nodes.append(nodes[node])
                counter += 1

            self._partitions.append(partition_nodes)

    @property
    def json(self):
        return js.dumps(self._partitions)

    def select(self, string):
        string = if_unicode_to_bytes(string)
        return self._partitions[shard(string)]

    def __str__(self):
        return str(self._partitions)

    def __repr__(self):
        return repr(self._partitions)

