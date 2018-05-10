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
import pickle
import fcntl
import threading
from collections import OrderedDict

save_lock = threading.Lock()


def orderdict(dict):
    return OrderedDict(sorted(dict.items()))


def object_name(obj):
    """Generates a name for an object from it's module and class


    Args:
        obj (object): any object to be named

    Returns:
        String naming the object

    """
    try:
        try:
            return obj.__module__ + '.' + obj.__name__
        except TypeError:
            return obj.__name__
    except AttributeError:
        # NOTE(cfrademan): Maybe its a class...
        try:
            val = obj.__class__.__module__
            val += '.' + obj.__class__.__name__
            # NOTE(cfrademan): the replace makes it slower, only comestic..
            return val #.replace('builtins.','')
        except TypeError:
            return obj.__class__.__name__
        except AttributeError:
            # NOTE(cfrademan): We want this error. dont try work around...
            pass

    raise ValueError("Cannot determine object name '%s'" % type(obj)) from None

# NOTE(HieronymusCrouse): Not tested yet
def dict_value_property(dictionary, key):
    """Create a read-only property

    Args:
        dictionary (dict): Dictionary in object..
        key (str): Case-sensitive dictionary key.

    Returns:
        A property instance that can be assigned to a class variable.
    """

    def fget(self):
        dictionary_obj = getattr(self, dictionary)
        try:
            return dictionary_obj[key] or None
        except KeyError:
            return None

    return property(fget)


def save(obj, file_path):
    save_lock.acquire()
    try:
        fp = open(file_path, 'wb', 0)
        fcntl.flock(fp, fcntl.LOCK_EX)
        pickle.dump(obj, fp)
        fp.flush()
    finally:
        try:
            fcntl.flock(fp, fcntl.LOCK_UN)
            fp.close()
        except UnboundLocalError:
            pass
        save_lock.release()

def load(file_path):
    save_lock.acquire()
    try:
        fp = open(file_path, 'rb', 0)
        fcntl.flock(fp, fcntl.LOCK_EX)
        return pickle.load(fp)
    finally:
        try:
            fcntl.flock(fp, fcntl.LOCK_UN)
            fp.close()
        except UnboundLocalError:
            pass
        save_lock.release()
