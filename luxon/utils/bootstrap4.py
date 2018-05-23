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
from collections import OrderedDict

from luxon.utils.html5 import select
from luxon.structs.htmldoc import HTMLDoc
from luxon.structs.models.model import Model
from luxon.utils.timezone import format_datetime
from luxon.utils.objects import orderdict


class NAVMenu(object):
    """CSS HTML Menu.
    """
    def __init__(self, name='Site', logo=None, url='#',
                 style=None,
                 css="navbar-expand-lg navbar-light bg-light"):

        self._html_object = HTMLDoc()
        nav = self._html_object.create_element('nav')
        nav.set_attribute('class',
                          'navbar ' + css)
        if style is not None:
            nav.set_attribute('style',
                              style)

        navbar_brand = nav.create_element('a')
        navbar_brand.set_attribute('class', 'navbar-brand')
        navbar_brand.set_attribute('href', url)
        if logo is not None:
            img = navbar_brand.create_element('img')
            img.set_attribute('src', logo)
            img.set_attribute('alt', 'Logo')
            img.set_attribute('height', '30')

        if logo and name:
            img.set_attribute('class', 'mr-2')

        if name is not None:
            navbar_brand.append(name)

        toggle = nav.create_element('button')
        toggle.set_attribute('class', 'navbar-toggler')
        toggle.set_attribute('type', 'button')
        toggle.set_attribute('data-toggle', 'collapse')
        toggle.set_attribute('data-target', '#navbarSupportedContent')
        toggle.set_attribute('aria-controls', 'navbarSupportedContent')
        toggle.set_attribute('aria-expanded', 'false')
        toggle.set_attribute('aria-label', 'Toggle navigation')
        toggle_span = toggle.create_element('span')
        toggle_span.set_attribute('class', 'navbar-toggler-icon')

        div = nav.create_element('div')
        div.set_attribute('class', 'collapse navbar-collapse')
        div.set_attribute('id', 'navbarSupportedContent')

        ul = div.create_element('ul')
        ul.set_attribute('class', 'navbar-nav mr-auto')

        self._ul = ul

        self.submenus = OrderedDict()

    def submenu(self, name):
        """Create new submenu item.

        Add submenu on menu and returns submenu for adding more items.

        Args:
            name (str): Name of submenu item.

        Returns meny object.
        """
        class Submenu(object):
            def __init__(self, name, parent):
                # Create new menu for submenu.
                self._column_count = 0
                self._row = None

                li = parent.create_element('li')
                li.set_attribute('class', 'nav-item dropdown')

                a = li.create_element('a')
                a.set_attribute('class', 'nav-link dropdown-toggle')
                name_id = 'dropdown_' + name.replace(' ', '').replace('-', '_')
                a.set_attribute('id', name_id)
                a.set_attribute('role', 'button')
                a.set_attribute('data-toggle', 'dropdown')
                a.set_attribute('aria-haspopup', 'true')
                a.set_attribute('aria-expanded', 'false')
                a.set_attribute('href', '#')
                a.append(name)
                div = li.create_element('div')
                div.set_attribute('class', 'dropdown-menu')
                div.set_attribute('aria-labelledby', name_id)
                table = div.create_element('table')
                self._html_object = table

            def link(self, name, href='#', active=False, **kwargs):
                kwargs = orderdict(kwargs)
                """Add submenu item.

                Args:
                    name (str): Menu item name.
                    href (str): Url for link. (default '#')

                Kwargs:
                    Kwargs are used to additional flexibility.
                    Kwarg key and values are used for properties of <a>.
                """
                if self._row is None or self._column_count > 1:
                    self._column_count = 0
                    self._row = self._html_object.create_element('tr')

                column = self._row.create_element('td')

                a = column.create_element('a')
                a.set_attribute('class', 'dropdown-item')
                a.set_attribute('href', href)
                for kwarg in kwargs:
                    a.set_attribute(kwarg, kwargs[kwarg])
                a.append(name)

                self._column_count += 1

            def submenu(self, name):
                return self

        # Create new menu for submenu.
        if name in self.submenus:
            return self.submenus[name]
        else:
            submenu = Submenu(name, self._ul)
            # Add Submenu to submenu cache.
            self.submenus[name] = submenu
            return submenu

    def link(self, name, href='#', active=False, **kwargs):
        """Add submenu item.

        Args:
            name (str): Menu item name.
            href (str): Url for link. (default '#')

        Kwargs:
            Kwargs are used to additional flexibility.
            Kwarg key and values are used for properties of <a> attribute.
        """
        kwargs = orderdict(kwargs)

        li = self._ul.create_element('li')
        if active:
            li.set_attribute('class', 'nav-item active')
        else:
            li.set_attribute('class', 'nav-item')

        a = li.create_element('a')
        a.set_attribute('class', 'nav-link')
        a.set_attribute('href', href)
        for kwarg in kwargs:
            a.set_attribute(kwarg, kwargs[kwarg])
        a.append(name)

    def __str__(self):
        return str(self._html_object)


def form(model, values=None, readonly=False):
    html = HTMLDoc()
    fields = model.fields
    if values is None and not isinstance(model, type):
        values = model.dict
    elif values is None:
        values = {}

    def html_field(field):
            value = values.get(field)
            if value is None:
                value = obj.default

            if hasattr(value, '__call__'):
                value = value()

            form_group = html.create_element('div')
            form_group.set_attribute('class', 'form-group')
            label = form_group.create_element('label')
            label.set_attribute('class', 'control-label col-sm-2')
            label.set_attribute('for', 'field')

            if obj.label is not None:
                label.append(obj.label)
            else:
                label.append(obj.name.title().replace('_', ' '))

            div = form_group.create_element('div')
            div.set_attribute('class', 'col-sm-10')

            if obj.readonly is True:
                field_readonly = True
            else:
                field_readonly = readonly

            if isinstance(obj, Model.Enum):
                div.append(select(field, obj.enum, value, cls="select",
                                  readonly=field_readonly))
            elif isinstance(obj, Model.DateTime):
                if value is not None:
                    value = format_datetime(value)
                input = div.create_element('input')
                input.set_attribute('type', 'text')
                input.set_attribute('class', 'form-control')
                input.set_attribute('id', field)
                input.set_attribute('name', field)
                if readonly is True:
                    input.set_attribute('readonly')
                    input.set_attribute('disabled')
                if obj.placeholder is not None:
                    input.set_attribute('placeholder', obj.placeholder)
                if value is not None:
                    input.set_attribute('value', value)
                if field_readonly:
                    input.set_attribute('readonly')
                    input.set_attribute('disabled')
                if obj.null is False:
                    input.set_attribute('required')
                if obj.placeholder:
                    input.set_attribute('placeholder', obj.placeholder)
            elif isinstance(obj, Model.Boolean):
                input = div.create_element('input')
                input.set_attribute('type', 'checkbox')
                input.set_attribute('id', field)
                input.set_attribute('name', field)
                if field_readonly is True:
                    input.set_attribute('disabled')
                if value is True:
                    input.set_attribute('checked')
                input.set_attribute('value', 'true')

            elif isinstance(obj, (Model.String, Model.Confirm,)):
                input = div.create_element('input')
                if obj.password is False:
                    input.set_attribute('type', 'text')
                else:
                    input.set_attribute('type', 'password')
                input.set_attribute('class', 'form-control')
                input.set_attribute('id', field)
                input.set_attribute('name', field)
                if readonly is True:
                    input.set_attribute('readonly')
                    input.set_attribute('disabled')
                if obj.placeholder is not None:
                    input.set_attribute('placeholder', obj.placeholder)
                if value is not None:
                    input.set_attribute('value', value)
                if field_readonly:
                    input.set_attribute('readonly')
                    input.set_attribute('disabled')
                if obj.null is False:
                    input.set_attribute('required')
                if obj.placeholder:
                    input.set_attribute('placeholder', obj.placeholder)
            else:
                pass

    for field in fields:
        obj = fields[field]
        if obj.hidden is False and obj.internal is False:
            html_field(field)

    return html
