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

import sys

from luxon.core.logger import GetLogger

log = GetLogger(__name__)


def import_module(module):
    """Import module.

    Args:
        module: Module import path definition.

    Returns:
        Module in given path.
    """
    if module not in sys.modules:
        log.info('Importing module: %s' % module)

        __import__(module)

    return sys.modules[module]


def import_modules(modules):
    """Import modules.

    Typically uses for modules in WSGI.

    Args:
        modules (list,tuple): List of module path definitions.

    Returns:
        A dict of imported modules. { 'name':: module }
    """
    loaded = {}
    for module in modules:
        if module.strip() != '':
            m = import_module(module)
            loaded[module] = m

    return loaded


def get_class(path):
    """Return class in module.

    Imports module and returns class.

    Args:
        path (str): package.module:class definition.

    Return:
        The class at given path
    """
    if path is None:
        raise ImportError("Cannot import 'None'")

    try:
        module, cls_name = path.split(':')
    except Exception:
        raise ValueError("Invalid path definition '%s'" % path)

    module = import_module(module)

    try:
        return getattr(module, cls_name)
    except AttributeError:
        raise ValueError("'%s' has no '%s'" % (module, cls_name,))


get_func = get_class


def get_classes(classes):
    """Initilize Classes.

    Typically uses by Middleware in WSGI.

    Args:
        classes (list,tuple): List of Class path definitions.

    Returns:
        A list of objects.
    """
    loaded = []

    for cls in classes:
        if cls.strip() != '':
            loaded.append(get_class(cls))

    return loaded
