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
import re
from html.parser import HTMLParser

from luxon.structs.htmldoc import HTMLDoc


BR_P_HTML_TAG = re.compile('<(br|/p)>', re.IGNORECASE)


def strip_tags(html):
    class _HTMLStripper(HTMLParser):
        def __init__(self):
            self.reset()
            self.fed = []
            self.convert_charrefs = True

        def handle_data(self, d):
            self.fed.append(d)

        def get_data(self):
            return ''.join(self.fed)

    html = BR_P_HTML_TAG.sub('\n', html)
    stripper = _HTMLStripper()
    stripper.feed(html)
    return stripper.get_data()


def select(name, options, selected, empty=False, cls=None, onchange=None,
           disabled=False, readonly=False):
    html = HTMLDoc()

    if disabled or readonly:
        input = html.create_element('input')
        input.set_attribute('type', 'text')
        input.set_attribute('id', name)
        input.set_attribute('name', name)
        input.set_attribute('disabled')
        if selected is not None:
            input.set_attribute('value', selected)
        input.set_attribute('class', 'form-control')
        return input

    select = html.create_element('select')
    select.set_attribute('name', name)
    select.set_attribute('id', name)

    if onchange is not None:
        select.set_attribute('onchange', onchange)

    if cls is not None:
        select.set_attribute('class', cls)

    if empty is True:
        option = select.create_element('option')
        option.set_attribute('value', '')
        option.append('')

    if options is not None:
        for opt in options:
            if isinstance(options, (list, tuple,)):
                if isinstance(opt, (list, tuple,)):
                    try:
                        option = select.create_element('option')
                        option.set_attribute('value', opt[0])
                        option.append(opt[1])
                        if opt[1] == selected:
                            option.set_attribute('selected')
                    except IndexError:
                        raise ValueError('Malformed values for HTML select')
                else:
                    if opt is not None:
                        option = select.create_element('option')
                        option.set_attribute('value', opt)
                        if opt == selected:
                            option.set_attribute('selected')
                        option.append(opt)
            elif isinstance(options, dict):
                    option = select.create_element('option')
                    option.set_attribute('value', opt)
                    if opt == selected:
                        option.set_attribute('selected')
                    option.append(options[opt])
    return html


def error_page(title, description):
    dom = HTMLDoc()
    html = dom.create_element('html')
    head = html.create_element('head')
    t = head.create_element('title')
    t.append(title)
    body = html.create_element('body')
    h1 = body.create_element('h1')
    h1.append(title)
    if description:
        h2 = body.create_element('h2')
        h2.append(description)
    return dom.get()


def error_ajax(title, description):
    dom = HTMLDoc()
    title = dom.create_element('B')
    title.append(title)
    if description:
        dom.create_element('<BR>')
        dom.append(description)
    return dom.get()
