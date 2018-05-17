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
from luxon import g


class Menu(object):
    """Class UIMenu.

    Used to generate Menu objects to add items
    for a Tachyonic Menu.
    """
    def __init__(self, html_class):
        self._items = []
        self._html_class = html_class

    def add(self, path_name, href='#', tag=None, **kwargs):
        self._items.append((path_name, tag, href, kwargs))

    def render(self, *args, **kwargs):
        req = g.current_request
        root_menu = self._html_class(*args, **kwargs)

        def render_item(menu, path_name, href, **kwargs):
            if len(path_name) == 1:
                # FORMAT URL to be under application.
                if href != '#' and ':' not in href:
                    href = "%s/%s" % (req.app, href.strip('/'))
                # Render link.
                menu.link(path_name[0], href=href, **kwargs)
            elif len(path_name) > 1:
                # Get Submenu.
                submenu = menu.submenu(path_name[0])
                # Render for Submenu.
                render_item(submenu, path_name[1:], href, **kwargs)

        has_policy_engine = hasattr(req, 'policy')
        # Run through items.
        for item in self._items:
            path_name, view, href, kwargs = item
            if (view is None or (has_policy_engine and
                                 req.policy.validate(view))):
                path_name = path_name.strip('/').split('/')
                render_item(root_menu, path_name, href, **kwargs)

        return root_menu

    def __len__(self):
        return len(self._itmes)

    def hasitems(self):
        if len(self._items) > 0:
            return True
        else:
            return False
