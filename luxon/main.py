#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2018 Christiaan Frans Rademan, Dave Kruger
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
import sys
import argparse
import site
from datetime import timedelta

from luxon import metadata
from luxon.core.servers.web import server as web_server
from luxon import db
from luxon.utils.rsa import RSAKey
from luxon.utils.crypto import Crypto
from luxon.utils.files import mkdir
from luxon.utils.pkg import Module
from luxon.core.utils import models
from luxon.utils.files import Open, chmod, exists, ls, rm, joinpath
from luxon.core.config import Config
from luxon.utils.timezone import now


def setup(args):
    """Setup Tachyonic Package with Luxon

    Creates relevant directories and copies relevant files

    Called when **-i** is used

    Args:
        args (parse_args object): arguments gathered from terminal
    """
    path = args.path.rstrip('/')
    module = Module(args.pkg)

    no_install = ['luxon', 'psychokinetic']

    if args.pkg in no_install:
        print("Your suppose to install luxon applications not '%s'" % args.pkg)
        exit()

    def copy(name, new_extension=None):
        if module.exists(name):
            print("Install files %s" % path + '/' + name)
            module.copy(name,
                        path + '/' + name,
                        new_extension=new_extension)

    mkdir(path)
    mkdir(joinpath(path, 'tmp'))
    copy('policy.json', 'default')
    copy('settings.ini', 'default')
    try:
        if exists(path + '/settings.ini'):
            chmod(path + '/settings.ini', 640)
    except PermissionError:
        pass
    copy('wsgi.py', 'default')
    copy('static')
    mkdir('%s/templates/%s' % (path, args.pkg), recursive=True)


def rsa(args):
    """Generates a new RSA *private.pem* and *public.pem*"""
    print("Generating new RSA private.pem and public.pem")
    rsakey = RSAKey()
    pk = rsakey.generate_private_key(password=args.password)
    with Open(args.path.rstrip('/') + '/private.pem', 'w') as f:
        f.write(pk)
    with Open(args.path.rstrip('/') + '/public.pem', 'w') as f:
        f.write(rsakey.public_key)

def gen_key(args):
    """Generates a new AES symmetrical key and iv in *credentials.key*"""
    print("Generating new AES key and initialization "
          "vector in credentials.key")
    crypto = Crypto()
    key_loc = args.path.rstrip('/') + '/credentials.key'
    if not os.path.isfile(key_loc):
        key = crypto.generate_key()
        iv = crypto.generate_iv()
        with open(key_loc, 'wb') as f:
            f.write(key + iv)
    else:
        print("Key already exists, not overwriting")

def clean_sessions(args):
    """Removes all expired session files"""
    path = args.path.rstrip('/')
    tmp_path = os.path.join(path, 'tmp')
    config = Config()
    config.load(path + '/settings.ini')
    expire = config.getint('sessions', 'expire', fallback=86400)
    if exists(tmp_path):
        files = ls(tmp_path)
        for file in files:
            if file[2].startswith('session_'):
                modified = file[8]
                expired = now() - timedelta(seconds=expire)
                if modified <= expired:
                    rm(file[1])


def server(args):
    """Start Internal Testing Server

    | Called when **-s** is used
    | Requires Gunicorn

    Args:
        args (parse_args object): arguments gathered from terminal
    """
    web_server(app_root=args.path, ip=args.ip, port=args.port)


def db_crud(args):
    """Create/Update Database for given package

    Called when **-d** is used

    Args:
        args (parse_args object): arguments gathered from terminal
    """
    with open(args.path.rstrip('/') + '/wsgi.py', 'r') as wsgi_file:
        exec_g = {}
        exec(wsgi_file.read(), exec_g, exec_g)

    # Backup Database model tables.
    backups = {}
    with db() as conn:
        # Backup Tables.
        backups = models.backup_tables(conn)

        # Drop Tables.
        models.drop_tables(conn)

        # Create Tables.
        models.create_tables()

        # Restore data.
        models.restore_tables(conn, backups)


def main(argv):
    description = metadata.description + ' ' + metadata.version
    print("%s\n" % description)

    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group(required=True)

    parser.add_argument('path',
                        help='Application root path')

    group.add_argument('-d',
                       dest='funcs',
                       action='append_const',
                       const=db_crud,
                       help='Create/Update Database')

    group.add_argument('-i',
                       dest='pkg',
                       help='Install/Update application in path specified')

    group.add_argument('-s',
                       dest='funcs',
                       action='append_const',
                       const=server,
                       help='Start Internal Testing Server (requires gunicorn)')

    group.add_argument('-c',
                       dest='funcs',
                       action='append_const',
                       const=clean_sessions,
                       help='Clean Sessions')

    group.add_argument('-r',
                       dest='funcs',
                       action='append_const',
                       const=rsa,
                       help='Generate RSA Private/Public Key pairs')

    group.add_argument('-k',
                       dest='funcs',
                       action='append_const',
                       const=gen_key,
                       help='Generate Symmetrical Encryption Key')

    parser.add_argument('--password',
                       help='RSA Private Key Password',
                       default=None)

    parser.add_argument('--ip',
                       help='Binding IP Address (127.0.0.1)',
                       default='127.0.0.1')

    parser.add_argument('--port',
                        help='Binding Port (8080)',
                        default='8080')

    args = parser.parse_args()
    args.path = os.path.abspath(args.path)

    # NOTE(cfrademan): Only add this path to sites. If someone is trying
    # to start server from path using the sources/package instead of the install path
    # then we don't want it to work... (BECAREFUL)
    site.addsitedir(os.path.abspath(args.path))
    sys.path.insert(0, os.path.abspath(args.path))
    os.chdir(args.path)

    if args.funcs is not None:
        for func in args.funcs:
            func(args)

    if args.pkg is not None:
        setup(args)

def entry_point():
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
