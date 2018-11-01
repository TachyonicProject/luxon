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

from jinja2.exceptions import TemplateNotFound
from jinja2 import Environment as Jinja2Environment
from jinja2.loaders import BaseLoader, FileSystemLoader, PackageLoader

from luxon import g
from luxon.core.logger import GetLogger

log = GetLogger(__name__)


def split_template_path(template):
    """Split a path into segments and perform a sanity check. If it detects
    '..' in the path it will raise a `TemplateNotFound` error.
    """
    pieces = []
    for piece in template.split('/'):
        if os.path.sep in piece \
           or (os.path.altsep and os.path.altsep in piece) or \
           piece == os.path.pardir:
            raise TemplateNotFound(template)
        elif piece and piece != '.':
            pieces.append(piece)
    return pieces


class TachyonicLoader(BaseLoader):
    """Jinja class for loading templates.
    """
    __slots__ = ('override_path',
                 '_fsl',
                 '_pkgloaders')

    def __init__(self, app_path):
        """Load Templates Jinja2 Templates

        Initialize loading for Jinja2 Templates.
        """
        override_path = app_path + '/templates'
        self._fsl = FileSystemLoader(override_path)

        self._pkgloaders = {}

    def get_source(self, environment, template):
        """Get raw template for environment.

        First attempts to load overriding template then uses template within
        specified package. For example "package/template.html"
        """
        try:
            if self._fsl is not None:
                source = self._fsl.get_source(environment, template)
                log.info("Loaded Override Template %s" % template)

                return source
        except TemplateNotFound:
            pass

        try:
            package_path = split_template_path(template)
            package = package_path[0]
            template = "/".join(package_path[1:])
            if package not in self._pkgloaders:
                self._pkgloaders[package] = PackageLoader(
                    package,
                    package_path='/templates',
                    encoding='UTF-8')

            source = self._pkgloaders[package].get_source(environment,
                                                          template)
            log.info("Loaded Package Template %s/%s" % (package, template))

            return source

        except ImportError:
            raise TemplateNotFound("'importerror' " +
                                   package +
                                   '/' + template) from None
        except TemplateNotFound:
            raise TemplateNotFound(package +
                                   '/' + template) from None

    def list_overrides(self):
        """Returns a list of overiding templates for this environment.

        Overiding templates are located within wsgi application installation
        path in templates.

        Templates to override are located in package/templates path structure.
        For example /var/www/ui/templates/template.html
        """
        fsl = self.fsl.list_templates()

        return fsl

    def list_templates(self):
        """Returns a list of templates for this environment.

        Templates are located within the python package source.
        """
        raise NotImplementedError('list_templates')


class Environment(Jinja2Environment):
    """Wraps around the Jinja2 Environment class with
        TachyonicLoader() specified as the loader for this environment"""
    def __init__(self, loader):
        super().__init__(loader=loader,
                         trim_blocks=True,
                         lstrip_blocks=True)
