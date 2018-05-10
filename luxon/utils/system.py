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
import os
import pwd
import grp
import subprocess
import socket
from tempfile import TemporaryFile

from luxon.exceptions import ExecuteError
from luxon.utils.encoding import if_bytes_to_unicode


def get_current_uid():
    """Get current uid"""
    return os.getuid()


def get_current_gid():
    """Get current uid gid"""
    return os.getgid()


def get_login_uid(login):
    """Get Login for UID"""
    return pwd.getpwnam(login).pw_uid


def get_group_gid(group):
    """Get Group for GID"""
    return grp.getgrnam(group).gr_gid


def get_uid_gid(uid):
    """Get defined uid gid"""
    return pwd.getpwuid(uid)[2]


def get_uid_login(uid):
    """Get defined uid username"""
    return pwd.getpwuid(uid)[0]


def get_gid_group(gid):
    """Get defined gid group name"""
    return grp.getgrgid(gid)[0]


def get_current_group():
    """Get current login uid group name"""
    return get_gid_group(get_current_gid())


def get_current_login():
    """Get current login uid username"""
    return get_uid_login(get_current_uid())


def get_uid_name(uid):
    """Get defined login uid fullname"""
    return pwd.getpwuid(uid)[4]


def get_current_name():
    """Get current login uid fullname"""
    return get_uid_name(get_current_uid())


def get_uid_home(uid):
    """Get defined uid home path"""
    return pwd.getpwuid(uid)[5]


def get_current_home():
    """Get current login uid home path"""
    return get_uid_home(get_current_uid())


def get_all_groups():
    """Get All Unix Groups

    Returns list of tuples [(name, gid, members,),]
    """
    groups = []
    for group in grp.getgrall():
        name = group[0]
        gid = group[2]
        members = group[3]
        groups.append((name, gid, members,))

    return groups


def get_login_groups(login):
    """Get Assigned Groups for Login specified.

    Returns list of [group1, group2,]
    """
    groups = []
    for group in get_all_groups():
        if login in group[2]:
            groups.append(group[0])

    return groups


def get_uid_groups(uid):
    """Get Assigned Groups for UID specified.

    Returns list of [group1, group2,]
    """
    login = get_uid_login(uid)
    return get_login_groups(login)


def get_current_groups():
    """Get Assigned Groups for UID specified.

    Returns list of tuples [(name, gid, members,),]
    """
    uid = get_current_uid()
    return get_uid_groups(uid)


def get_current_pid():
    """Get Current Process ID"""
    return os.getpid()


def get_load_avg():
    """Return average recent system load information.

    Return the number of processes in the system run queue averaged over
    the last 1, 5, and 15 minutes as a tuple of three floats.
    Raises OSError if the load average was unobtainable.
    """
    return os.getloadavg()


def execute(*args, check=True):
    from luxon import GetLogger
    log = GetLogger(__name__)

    loginfo = TemporaryFile()
    logerr = TemporaryFile()

    try:
        log.info("Execute '%s'" % " ".join(args[0]))
        subprocess.run(*args, stdout=loginfo,
                       stderr=logerr,
                       check=True)
        return if_bytes_to_unicode(loginfo.read())
    except subprocess.CalledProcessError as e:
        logerr.seek(0)
        if check is True:
            cmd = " ".join(*args)
            raise ExecuteError(cmd,
                               if_bytes_to_unicode(logerr.read())) from None
        return if_bytes_to_unicode(logerr.read())
    finally:
        loginfo.seek(0)
        logerr.seek(0)
        log.info(if_bytes_to_unicode(loginfo.read()))
        log.error(if_bytes_to_unicode(logerr.read()))
        loginfo.close()
        logerr.close()


def get_uptime():
    # NOTE(cfrademan): Only works on linux.
    with open('/proc/uptime', 'r') as f:
        seconds = float(f.readline().split()[0])

    return seconds


def get_hostname():
    return socket.gethostname()
