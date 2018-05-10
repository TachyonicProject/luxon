# -*- coding: utf-8 -*-
# Copyright (c) 2017, Christiaan Frans Rademan.
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
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import os

from luxon import g

class Theme():
    def __init__(self):
        self._default_theme = g.config.get('application', 'default_theme',
                                           fallback='default')
        self._static_web_path = g.config.get('application', 'static',
                                             fallback='/static').rstrip('/')
        self._static_file_path = g.app_root.rstrip('/') + '/static'

        self._static_web_path += '/themes/'
        self._static_file_path += '/themes/'

    def _pick_file(self, the_file):
        # Remove / on both ends the_file
        the_file = the_file.strip('/')

        # Get Current Domain/Host
        host = g.current_request.host

        # Domain Theme
        check_file = host + '/' + the_file
        if os.path.isfile(self._static_file_path + check_file):
            return self._static_web_path + check_file

        # Default Theme
        check_file = self._default_theme + '/' + the_file
        if os.path.isfile(self._static_file_path + check_file):
            return self._static_web_path + check_file

        # Builtin Tachyonic Theme
        check_file = 'default' + '/' + the_file
        if os.path.isfile(self._static_file_path + check_file):
            return self._static_web_path + check_file

        raise FileNotFoundError("Missing static" +
                                " content '%s'" % (self._static_web_path +
                                check_file,))

    @property
    def css(self):
        return self._pick_file('/theme.css')

    @property
    def icon(self):
        return self._pick_file('/icon-32x32.png')

    @property
    def logo(self):
        return self._pick_file('/logo.png')

    @property
    def background(self):
        return self._pick_file('/background.jpg')

    @property
    def loader(self):
        return self._pick_file('/loader.gif')

    @property
    def view_button(self):
        return self._pick_file('/view.png')

    @property
    def edit_button(self):
        return self._pick_file('/edit.png')
