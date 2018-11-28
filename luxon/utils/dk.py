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
import docker
from luxon.utils.pkg import Module

client = docker.from_env()

def start(name, image, volumes=None, ports=None, links=None, hostname=None, **env):
    try:
        container = client.containers.get(name)
        if container.status in ('running', 'restarting'):
            pass
        elif container.status == 'paused':
            container.unpause()
        elif container.status == 'exited':
            container.start()

    except docker.errors.NotFound:
        parsed_links = {}
        if links:
            for link in links:
                parsed_links[link] = link

        parsed_volumes = {}
        if volumes:
            for volume in volumes:
                parsed_volumes[volume] = {'bind': volumes[volume], 'mode': 'rw'}
            
        client.containers.run(image, name=name,
                              ports=ports,
                              environment=env,
                              detach=True,
                              links=parsed_links,
                              volumes=parsed_volumes,
                              hostname=hostname)

def restart(name):
    container = client.containers.get(name)
    container.restart()

def stop(name):
    container = client.containers.get(name)
    container.stop()

def build(name, fileobj):
    return client.images.build(tag=name, fileobj=fileobj, forcerm=True)

def remove_image(name):
    client.images.remove(image=name)

def remove_container(name):
    container = client.containers.get(name)
    container.remove()

def exec(name, command):
    container = client.containers.get(name)
    return container.exec_run(command, detach=False)
