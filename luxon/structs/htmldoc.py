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
from html.parser import HTMLParser

from luxon import exceptions

html5_void_elements = ["area", "base", "br", "col",
                       "command", "embed", "hr", "img",
                       "input", "keygen", "link", "meta",
                       "param", "source", "track", "wbr"]


class HTMLDoc(object):
    """HTMLDoc HTMLDoc Object.

    This class provides minimal validation for speed.

    Used for creating html documents.
    """
    def __init__(self):
        # Dictionary of element attributes and values.
        # NOTE(cfrademan): Import to keep order the same of attributes.
        # This is because of caching + etags.
        self.attributes = OrderedDict()
        # List of element content.
        self.contents = []
        # Name of element. (example. <html)
        self.element = None
        # Parent Element
        self._parent = None

    def create_element(self, name):
        """Create Element / HTMLDoc tag entity.

        Args:
            name (str): Element / Tag name. ie html for <html>

        Returns HTMLDoc HTMLDoc object for tag.
        """
        name = name.lower()
        element = HTMLDoc()
        element.element = name
        element._parent = self
        self.contents.append(element)

        return element

    def set_attribute(self, attribute, value=None):
        """Set Attributes on Element / HTMLDoc tag entity.

        Args:
            attribute (str): Attribute name such as 'class'.
            value (str): Attribute value such as 'uber_menu'.

        Validates tags and the values provided.
        """
        value = str(value)

        attribute = attribute.lower()
        self.attributes[attribute] = value

    def append(self, value):
        """Append raw text to element.

        Args:
            value (str): text such as 'Goodbye World'
        """
        if self.element in html5_void_elements:
            raise exceptions.Error("DOM: Appending on void element %s" % (self.element,))
        else:
            self.contents.append(value)

    def prepend(self, value):
        """Prepend raw text to element.

        Args:
            value (str): text such as 'Hello World'
        """
        if self.element in html5_void_elements:
            raise Exception("DOM: Prepending on void" +
                            " element %s" % (self.element,))
        else:
            self.contents[:0] = value

    def get_contents(self):
        """Get HTMLDoc output for element contents.

        Returns HTMLDoc in strings in list.
        """
        to_return = ''

        for content in self.contents:
            if isinstance(content, HTMLDoc):
                to_return += content.get()
            else:
                to_return += str(content)

        return to_return

    def get(self):
        """Get HTMLDoc output for current element and contents.

        Returns HTMLDoc in strings in list.
        """

        to_return = ''

        if self.element is not None:
            to_return += "<%s" % self.element

            for attribute in self.attributes:
                value = self.attributes[attribute]
                to_return += ' ' + attribute.replace('_', '-')
                if value is not None and value.strip() != '':
                    to_return += "=\"%s\"" % value

            to_return += '>'

        to_return += self.get_contents()

        if self.element is not None:
            if self.element not in html5_void_elements:
                to_return += "</%s>" % self.element

        return to_return

    def parse_html(self, html):
        """Load HTMLDoc string into document object.

        Args:
            html (str): Valid HTMLDoc for processing.
        """
        html = html.strip()
        parser = _Parse(self, html)
        parser.feed(html)
        parser.close()

    def __str__(self):
        return self.get()

    def __repr__(self):
        return self.get()

class _Parse(HTMLParser):
    def __init__(self, dom, html):
        self._dom = dom
        super().__init__(convert_charrefs=False)

    def handle_starttag(self, tag, attrs):
        dom = self._dom.create_element(tag)
        for attr in attrs:
            dom.set_attribute(attr[0], attr[1])
        if tag not in html5_void_elements:
            self._dom = dom

    def handle_endtag(self, tag):
        if self._dom.element == tag.lower():
            self._dom = self._dom._parent
        else:
            line, col = self.getpos()
            raise Exception('Unexpected \'</%s>\' Line:%s Col: %s' % (tag,
                                                                      line,
                                                                      col))

    def handle_data(self, data):
        self._dom.append(data)

    def handle_decl(self, decl):
        self._dom.append('<!' + decl + '>')

    def handle_comment(self, comment):
        self._dom.append('<!-- ' + comment + ' -->')

    def handle_pi(self, data):
        self._dom.append('<?' + data + '>')
