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

import configparser
import json

from luxon.utils import js


class Config(configparser.ConfigParser):
    """Tachyonic Python ConfigParser extended.

    You can find complete set of methods from Python ConfigParser
    documentation.

    Alterations in behaviour:
        * Sections are case-insenstive too.
        * Addition can use attributes to get section, options without spaces.

    However the methods within here only to provide extended functionality.

    Args:
        config_file (str): Optional config file or dict to load.
    """
    __slots__ = ()

    def __init__(self, config_file=None):
        super().__init__()
        if config_file is not None:
            self.load(config_file)

    def __getattr__(self, key):
        class Proxy(object):
            def __init__(self, section):
                self._config_section = section
                self._section_name = section

            def __getitem__(self, item):
                return self._config_section[item]

            def __setitem__(self, item, value):
                self._config_section[item] = value

            def __getattr__(self, key):
                try:
                    return self[key]
                except KeyError:
                    raise AttributeError(
                        "config section '%s' has no attribute '%s'" %
                        (self._section_name.name, key,))

        try:
            proxy = Proxy(self[key])
        except KeyError:
            raise AttributeError("config has no attribute '%s'" % key)

        return proxy

    def load(self, config_file, encoding=None):
        """Load Configuration file.

        Args:
            config_file (str): Path / Location to configuration file.
        """
        if encoding is not None:
            with open(config_file, 'r', encoding=encoding) as f:
                super().read_file(f)
        else:
            with open(config_file, 'r') as f:
                super().read_file(f)

    def save(self, config_file):
        """Save Configuration file.

        Args:
            config_file (str): Path / Location to configuration file.
        """
        with open(config_file, 'w') as f:
            self.write(f)

    def sections(self):
        """Return all the configuration section names, sans DEFAULT.
        """
        return super().sections()

    def has_section(self, section):
        """Return whether the given section exists.
        """
        return super().has_section(section)

    def options(self, section):
        """Return list of configuration options for the named section.
        """
        return super().options(section)

    def read(self, filenames, encoding=None):
        """Read and parse the list of named configuration files, given by
        name.  A single filename is also allowed.  Non-existing files
        are ignored.  Return list of successfully read files.
        """
        return super().read(filenames, encoding)

    def read_string(self, string):
        """Read configuration from a given string.
        """
        return super().read_string(string)

    def read_dict(self, dictionary):
        """Read configuration from a dictionary. Keys are section names,
        values are dictionaries with keys and values that should be present
        in the section. If the used dictionary type preserves order, sections
        and their keys will be added in order. Values are automatically
        converted to strings.
        """
        return super().read_dict(dictionary)

    def get(self, section, option, *, raw=False, vars=None,
            fallback=configparser._UNSET):
        """Get an option value for a given section.

        If `vars` is provided, it must be a dictionary. The option is looked up
        in `vars` (if provided), `section`, and in `DEFAULTSECT` in that order.
        If the key is not found and `fallback` is provided, it is used as
        a fallback value. `None` can be provided as a `fallback` value.

        If interpolation is enabled and the optional argument `raw` is False,
        all interpolations are expanded in the return values.

        The section DEFAULT is special.
        """
        return super().get(section, option, raw=raw, vars=vars,
                           fallback=fallback)

    def getint(self, section, option, *, raw=False, vars=None,
               fallback=configparser._UNSET):
        """Like get(), but convert value to an integer.
        """
        return super().getint(section, option, raw=raw, vars=vars,
                              fallback=fallback)

    def getfloat(self, section, option, *, raw=False, vars=None,
                 fallback=configparser._UNSET):
        """Like get(), but convert value to a float.
        """
        return super().getfloat(section, option, raw=raw, vars=vars,
                                fallback=fallback)

    def getboolean(self, section, option, *, raw=False, vars=None,
                   fallback=configparser._UNSET):
        """Like get(), but convert value to a boolean (currently case
        insensitively defined as 0, false, no, off for False, and 1, true,
        yes, on for True).  Returns False or True.
        """
        return super().getboolean(section, option, raw=raw, vars=vars,
                                  fallback=fallback)

    def items(self, section=None, *, raw=False, vars=None):
        """If section is given, return a list of tuples with (name, value) for
        each option in the section. Otherwise, return a list of tuples with
        (section_name, section_proxy) for each section, including DEFAULTSECT.
        """

        return super().items(section=section, raw=raw, vars=vars)

    def remove_section(self, section):
        """Remove the given file section and all its options.
        """
        super().remove_section(section)

    def remove_option(self, section, option):
        """Remove the given option from the given section.
        """
        super().remove_option(section, option)

    def set(self, section, option, value):
        """Set the given option.
        """
        super().set(section, option, value)

    def getjson(self, section, option, fallback=None):
        """Load JSON object from value.

        Args:
            section (str): section name.
            option (str): option name.

        Kwargs:
            fallback: Dict or List.

        Returns dict or list.
        """
        try:
            val = self.get(section, option)
            if val.strip() == '' and fallback is not None:
                return fallback
            elif val.strip() == '':
                raise configparser.NoSectionError(section) from None
        except configparser.NoSectionError as e:
            if fallback is not None:
                return fallback
            else:
                raise configparser.NoSectionError(section) from None
        except configparser.NoOptionError as e:
            if fallback is not None:
                return fallback
            else:
                raise configparser.NoOptionError(section, option) from None

        try:
            return js.loads(val)
        except json.decoder.JSONDecodeError as e:
            raise configparser.ParsingError("section '%s'" % section +
                                            " option '%s'" % option +
                                            " (JSON %s)" % e) from None

    def getlist(self, section, option, fallback=None):
        """Get list from option value.

        Example:

        .. code::

            [Bar]
            files_to_check =
                /path/to/file1,
                /path/to/file2,
                /path/to/another file with space in the name

        Args:
            section (str): section name.
            option (str): option name.

        Kwargs:
            fallback (list): List of default values.

        Returns list.
        """
        try:
            val = self.get(section, option)
            if val.strip() == '':
                return []
            val = val.replace('\n', '').replace('\r', '').split(',')
        except configparser.NoSectionError as e:
            if fallback is not None:
                val = fallback
            else:
                raise configparser.NoSectionError(section) from None
        except configparser.NoOptionError as e:
            if fallback is not None:
                val = fallback
            else:
                raise configparser.NoOptionError(section, option) from None

        if isinstance(val, list):
            return val
        else:
            raise configparser.ParsingError("section '%s'" % section +
                                            " option '%s'" % option +
                                            " expected list") from None

    def kwargs(self, section):
        """Get dict for kwargs for section.

        Excludes all default values.

        Convieniantly use with \*\*kwargs from configuration as arguements.

        Args:
            section (str): section name.

        Returns dict.
        """
        try:
            return self._sections[section]
        except KeyError:
            raise configparser.NoSectionError(section) from None
