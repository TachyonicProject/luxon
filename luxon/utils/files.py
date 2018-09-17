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
import stat
import fcntl
import shutil
from io import BytesIO

from luxon.utils.encoding import if_bytes_to_unicode
from luxon.utils.timezone import to_timezone, TimezoneSystem, TimezoneUTC
from luxon.utils.singleton import NamedSingleton
from luxon.utils.system import (get_login_uid, get_group_gid,
                                get_uid_login, get_gid_group)


class TrackFile(metaclass=NamedSingleton):
    """Tracks a given file

    Args:
        file(file): file to be tracked

    """

    def __init__(self, file):
        self._file = file
        if os.path.isfile(self._file):
            self._modified = os.stat(self._file).st_mtime
        else:
            self._modified = None

    def __call__(self):
        return self.is_modified()

    def is_modified(self):
        """Checks if file was modified since tracking started

        returns:
            True if modified
        """
        # NOTE(Rony): might not be working check the unit test

        # If there was never file... check for new file...
        if self._modified is None:
            # If there is now a file...
            if os.path.isfile(self._file):
                self._modified = os.stat(self._file).st_mtime
                return True

        # If there is a file from start...
        if os.path.isfile(self._file):
            # get the modified time of file...
            mtime = os.stat(self._file).st_mtime
            # if modified.
            if mtime != self._modified:
                # update with modified time..
                self._modified = mtime
                return True
            else:
                # if not modified...
                return False
        else:
            # if file is gone it not new..
            return False

    def is_deleted(self):
        """Checks if file was deleted since tracking started

        Returns:
            True if deleted

        """
        # If there was a file...
        if self._modified is not None:
            # if file still exisits...
            if os.path.isfile(self._file):
                return False
            # if file doesnt exist anymore...
            return True
        # if it never existed...
        return False

    def clear(self):
        self._modified = None


def is_socket(socket):
    """Is Unix socket

    Args:
        socket (str): Socket path.

    Retrurns:
        Bool whether file is unix socket
    """
    try:
        mode = os.stat(socket).st_mode
        return stat.S_ISSOCK(mode)
    except Exception:
        return False


class FileObject(object):
    """Simple File Object structure for internal use

    contains attributes for: filename, type and the file itself

    """
    __slots__ = ('filename', 'type', 'file')

    def __init__(self, filename, type, file):
        self.filename = filename
        self.type = type
        self.file = file


class Lock(object):
    def __init__(self, file, perms=600):
        perms = _perm_to_octal(perms)
        self._lock_file = file + '.lock'
        self._lock_file_fd = open(
            os.open(self._lock_file, os.O_CREAT | os.O_WRONLY,
                    perms),
            'wb')
        fcntl.flock(self._lock_file_fd, fcntl.LOCK_EX)

    def unlock(self):
        rm(self._lock_file)
        self._lock_file_fd.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.unlock()


class Open(object):
    """Open File

    Opens a given file and performs actions on the file object.
    A number of default options can be specified as keyword arguments when
    spawning the file object.

    Options such as:

        * buffering
        * encoding
        * errors
        * newline
        * closefd
        * opener


    Args:
        file (file): file to be opened
        mode (str): mode

    """
    def __init__(self, file, mode='r', buffering=-1, encoding=None,
                 errors=None, newline=None, closefd=True, opener=None,
                 perms=600, create=True):

        if create is False:
            if not exists(file):
                raise FileNotFoundError(file)

        self._lock = Lock(file, perms)
        perms = _perm_to_octal(perms)

        try:
            self.fd = open(
                os.open(file, os.O_RDWR | os.O_CREAT, perms),
                mode=mode, buffering=buffering,
                encoding=encoding, errors=errors,
                newline=newline, closefd=closefd,
                opener=opener
            )
        except FileNotFoundError:
            self._lock_file_fd.close()
            raise

    @property
    def encoding(self):
        """Property

        Encode file"""
        if hasattr(self.fd, 'encoding'):
            return self.fd.encoding
        else:
            raise AttributeError('encoding')

    @property
    def errors(self):
        """Property

        Unicode Error Handler"""
        if hasattr(self.fd, 'errors'):
            return self.fd.errors
        else:
            raise AttributeError('errors')

    @property
    def newlines(self):
        """Property

        end-of-line convention"""
        if hasattr(self.fd, 'newlines'):
            return self.fd.newlines
        else:
            raise AttributeError('newlines')

    @property
    def buffer(self):
        """Property

        Buffer size"""
        if hasattr(self.fd, 'buffer'):
            return self.fd.buffer
        else:
            raise AttributeError('buffer')

    def read(self, size=-1):
        """Read file"""
        return self.fd.read(size)

    def readline(self, size=-1):
        """Read line"""
        if hasattr(self.fd, 'readline'):
            return self.fd.readline(size)
        else:
            raise AttributeError('readline')

    def seek(self, offset, whence=0):
        """Move to new file position"""
        if hasattr(self.fd, 'seek'):
            return self.fd.seek(offset, whence)
        else:
            raise AttributeError('seek')

    def tell(self):
        """Current file position"""
        if hasattr(self.fd, 'tell'):
            return self.fd.tell()
        else:
            raise AttributeError('tell')

    def write(self, value):
        """Write File"""
        self.fd.write(value)

    def flush(self):
        """Clear the buffer"""
        if hasattr(self.fd, 'flush'):
            return self.fd.flush
        else:
            raise AttributeError('flush')

    def close(self):
        """Close File"""
        self.flush()
        self.fd.close()
        self._lock.unlock()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


def get_free_space(path):
    """Get free space in path.

    blocks =  Size of filesystem in bytes.
    bytes = Actual number of free bytes.
    avail = Number of free bytes that ordinary users can use.


    Returns tuple (blocks, bytes, bytes_avail)
    """
    statvfs = os.statvfs(path)

    return (statvfs.f_frsize * statvfs.f_blocks,
            statvfs.f_frsize * statvfs.f_bfree,
            statvfs.f_frsize * statvfs.f_bavail,)


def get_mounts():
    """Get mounts

    """
    # NOTE(cfrademan): Only works on linux.

    try:
        with open('/proc/mounts', 'r') as f:
            mounts = [line.split()[1] for line in f.readlines()]
    except FileNotFoundError:
        return []

    return mounts


def get_cwd():
    """Return Current working directory"""
    return os.getcwd()


def chdir(path):
    # TODO Many features to add. auto create directory structure..
    os.chdir(path)


def chown(path, uid=None, gid=None, recursive=False):
    """Change Ownership

    Args:
        path (str): file path
        uid (str): new user id
        gid (str): new group id
    """
    if recursive is True:
        for file in walk(path):
            chown(file[1], gid)
    else:
        file = file_info(path)
        if uid is None:
            uid = file[3]
        if gid is None:
            gid = file[4]

        if isinstance(uid, str):
            uid = get_login_uid(uid)
        if isinstance(gid, str):
            gid = get_group_gid(gid)

        os.chown(path, uid, gid)


def exists(path):
    """Is the path a directory"""
    return os.path.exists(path)


def is_dir(path):
    """Is the path a directory"""
    return os.path.isdir(path)


def is_file(path):
    """Is the path a file"""
    return os.path.isfile(path)


def is_link(path):
    """Is the path a link"""
    return os.path.islink(path)


def is_mount(path):
    """Is the path a mount"""
    return os.path.ismount(path)


def rm(path, recursive=False):
    """Remove file or directory at given location

    Args:
        path (str): path to be removed
        recursive (bool): recursive option
    """
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        elif recursive is True:
            try:
                shutil.rmtree(path)
            except FileNotFoundError:
                pass
        else:
            os.removedirs(path)


def mkdir(path, recursive=False):
    """Creates a new directory in a given location

    Args:
        path (str): location of new directory
    """
    if not os.path.exists(path):
        if recursive is True:
            os.makedirs(path)
        else:
            os.mkdir(path)


def _perm_str_to_octal(perms):
    missing = 9 - len(perms)
    perms = "-" * missing + perms
    set_uid = False
    set_gid = False
    mode = 0
    perm_struct = [['x', 's'], 'w', 'r']
    for level in reversed(range(3)):
        level_mode = 0
        for pos, perm in enumerate(reversed(perms[level*3:(level*3)+3])):
            if perm not in perm_struct[pos]:
                raise Exception("Invalid file mode provided '%s'" % perms)

            if perm == 's':
                if level == 0:
                    set_uid = True
                if level == 1:
                    set_gid = True
            if perm != '-':
                level_mode += (2 ** pos)

        level = (level / 2) * 2
        mode += int((8 ** level)) * level_mode

    if set_uid is True and set_gid is True:
        mode += int((8 ** 3)) * 6
    elif set_uid is True:
        mode += int((8 ** 3)) * 4
    elif set_gid is True:
        mode += int((8 ** 3)) * 2

    return mode


def _perm_int_to_octal(val):
    octal = 0
    for i, v in enumerate(reversed(str(val))):
        octal += (8 ** i) * int(v)
    return octal


def _perm_to_octal(perms):
    if isinstance(perms, (str, bytes,)):
        perms = if_bytes_to_unicode(perms)
        perms = _perm_str_to_octal(perms)
    else:
        perms = _perm_int_to_octal(perms)

    return perms


def chmod(path, perms):
    """Change file mode permissi0ns.

    Expects value of int such as 755,
    Alternatively you can provide format in string rwxrwxrwx.
    """
    perms = _perm_to_octal(perms)

    os.chmod(path, perms)


def file_info(path):
    """File Information

    Args (str): location of file

    Returns a tuple with the following info:

        * file type
        * full path
        * short name
        * uid
        * gid
        * file mode
        * file size
        * access time
        * modified time
        * create time
        * extra
    """
    if os.path.isdir(path):
        file_type = 'directory'
    elif os.path.isfile(path):
        file_type = 'file'
    elif os.path.islink(path):
        file_type = 'link'
    else:
        raise FileNotFoundError(path)

    fullpath = path
    shortname = path.strip('/').split('/')[-1]
    f_stat = os.stat(path)
    owner = f_stat.st_uid
    group = f_stat.st_gid
    mode = f_stat.st_mode
    size = f_stat.st_size
    access_time = f_stat.st_atime
    modified_time = f_stat.st_mtime
    create_time = f_stat.st_ctime

    extra = None
    if file_type == 'link':
        extra = os.readlink(fullpath)

    return (file_type,
            fullpath,
            shortname,
            get_uid_login(owner),
            get_gid_group(group),
            stat.filemode(mode),
            size,
            to_timezone(access_time,
                        dst=TimezoneUTC(),
                        src=TimezoneSystem()),
            to_timezone(modified_time,
                        dst=TimezoneUTC(),
                        src=TimezoneSystem()),
            to_timezone(create_time,
                        dst=TimezoneUTC(),
                        src=TimezoneSystem()),
            extra,)


def walk(path):
    """Walks through directory

    Args:
        path (str): location of directory

    Returns a list of file information tuples for each file in directory
    """
    walk = []
    for directory, dirnames, filenames in os.walk(path):
        walk.append(file_info(directory))
        for filename in filenames:
            file_path = os.path.join(directory, filename)
            walk.append(file_info(file_path))

    return walk


def ls(path):
    if os.path.isfile(path):
        return [file_info(path)]
    else:
        walk = []
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            walk.append(file_info(file_path))
        return walk


def abspath(path):
    return os.path.abspath(path)


def joinpath(path, *p):
    return os.path.join(path, *p)


def dirname(path):
    return os.path.dirname(path)


def rename(src, dst):
    return os.rename(src, dst)
