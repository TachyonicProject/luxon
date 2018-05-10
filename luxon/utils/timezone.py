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
from datetime import datetime as py_datetime
from datetime import tzinfo, timedelta

import pytz
from tzlocal import get_localzone

from luxon import g

_cached_time_zone_system = None
_cached_time_zone_app = None

TIME_FORMATS = (
    '%Y-%m-%dT%H:%M:%SZ',
    '%Y-%m-%d %H:%M:%S.%f%z',
    '%Y-%m-%d %H:%M:%S%z',
    '%Y-%m-%d %H:%M:%S %Z',
    '%Y/%m/%d %H:%M:%S %Z',
    '%Y-%m-%d %H:%M %Z',
    '%Y/%m/%d %H:%M %Z',
    '%Y-%m-%d %H:%M:%S',
    '%Y/%m/%d %H:%M:%S',
    '%Y-%m-%d %H:%M',
    '%Y/%m/%d %H:%M',
    '%a, %d %b %Y %H:%M:%S %Z',
    '%a, %d-%b-%Y %H:%M:%S %Z',
    '%A, %d-%b-%y %H:%M:%S %Z',
    '%a %b %d %H:%M:%S %Y',
    '%a %b %d %H:%M:%S %Y',
)


def parse_http_date(http_date, obs_date=False):
    """Converts an HTTP date string to a datetime instance.

    Args:
        http_date (str): An RFC 1123 date string.
            e.g. Tue, 15 Nov 1994 12:45:26 GMT
        obs_date (bool): Support obs-date formats according to
            RFC 7231. (Default False)
            e.g. Sunday, 06-Nov-94 08:49:37 GMT

    Returns:
        datetime: A UTC datetime instance corresponding to the given
        HTTP date.

    Raises:
        ValueError: http_date doesn't match any of the available time formats
    """

    if not obs_date:
        return py_datetime.strptime(http_date, '%a, %d %b %Y %H:%M:%S %Z')

    return parse_datetime(http_date)


class TimezoneGMT(tzinfo):
    """GMT timezone class implementing GMT Timezone"""

    UTC_OFFSET = timedelta(hours=0)
    DST_OFFSET = timedelta(hours=0)
    NAME = 'GMT'

    def utcoffset(self, dt):
        """Get the offset from UTC.

        Args:
            dt(datetime.datetime): Ignored

        Returns:
            datetime.timedelta: Offset.
        """

        return self.UTC_OFFSET

    def tzname(self, dt):
        """Get the name of this timezone.

        Args:
            dt(datetime.datetime): Ignored

        Returns:
            str: e.g. "GMT"
        """

        return self.NAME

    def dst(self, dt):
        """Return the daylight saving time (DST) adjustment.

        GMT has no daylight savings time. Always Zero.

        Args:
            dt(datetime.datetime): Ignored

        Returns:
            datetime.timedelta: DST adjustment for GMT.
        """
        return self.DST_OFFSET


class TimezoneUTC(TimezoneGMT):
    """UTC timezone class implementing UTC Timezone"""
    TZNAME = 'UTC'


def TimezoneSystem():
    global _cached_time_zone_system

    if _cached_time_zone_system is None:
        _cached_time_zone_system = get_localzone()

    return _cached_time_zone_system


def TimezoneApp():
    global _cached_time_zone_app

    if _cached_time_zone_app is None:
        app_timezone = g.config.get('application',
                                    'timezone')

        if app_timezone == 'local' or app_timezone == 'server':
            _cached_time_zone_app = get_localzone()
        else:
            _cached_time_zone_app = pytz.timezone(app_timezone)

    return _cached_time_zone_app


def parse_datetime(datetime):
    if isinstance(datetime, (int, float,)):
        return py_datetime.fromtimestamp(datetime)
    if isinstance(datetime, py_datetime):
        return datetime

    if not isinstance(datetime, str):
        raise ValueError("datetime value not" +
                         " 'str' or 'datetime'")

    # NOTE(cfrademan): PARSE UTC OFFSET FROM in FORM of +HH:MM to +HHMM
    splitted_datetime = datetime.split('+')
    datetime = splitted_datetime[0]
    try:
        datetime += '+' + splitted_datetime[1].replace(':', '')
    except IndexError:
        pass

    for time_format in TIME_FORMATS:
        try:
            return py_datetime.strptime(datetime, time_format)
        except ValueError:
            continue

    raise ValueError('datetime value %r does not' % datetime +
                     ' match known formats')


def to_timezone(datetime, dst=TimezoneSystem(), src=None):
    if not isinstance(datetime, py_datetime):
        datetime = parse_datetime(datetime)

    if src is None and datetime.tzinfo is None:
        raise ValueError('to_timezone not possible from naive datetime' +
                         ' use src keyword to define source timezone')
    if isinstance(dst, str):
        dst = pytz.timezone(dst)
    if src is not None:
        if isinstance(src, str):
            src = pytz.timezone(src)
        try:
            datetime = src.localize(datetime)
        except AttributeError:
            datetime = datetime.replace(tzinfo=src)

    datetime = datetime.astimezone(tz=dst)
    try:
        datetime = dst.normalize(datetime)
    except AttributeError:
        pass
    return datetime


def now(tz=TimezoneUTC()):
    """Current date time.

    Keyword Args:
        tz (tzinfo): Timezone Object. Defaults to UTC.
    """
    return py_datetime.now(tz=tz)


def utc(datetime):
    return to_timezone(datetime, dst=TimezoneUTC(), src=TimezoneUTC())


def to_utc(datetime, src=None):
    return to_timezone(datetime, dst=TimezoneUTC(), src=src)


def to_gmt(datetime, src=None):
    return to_timezone(datetime, dst=TimezoneGMT(), src=src)


def to_system(datetime, src=None):
    return to_timezone(datetime, dst=TimezoneSystem(), src=src)


def to_app(datetime, src=None):
    return to_timezone(datetime, dst=TimezoneApp(), src=src)


def format_datetime(datetime, src=TimezoneUTC()):
    """String Formatted Date & Time.

    Many countries have adopted the ISO standard of year-month-day
    hour:minute:seconds. For
        example, 2015-03-30 10:15:25 (SAST).

    Appends short timezone name.

    Args:
        datetime (datetime): Datetime object. (Optional)
        destination_tz (str): Destination Timezone.
            List of valid entries in timezones attribute.

    Returns string formatted date.
    """
    datetime = to_timezone(datetime, dst=TimezoneApp(), src=src)

    return(datetime.strftime('%Y-%m-%d %H:%M:%S ') + "(" +
           datetime.tzname() + ")")


def format_http_datetime(datetime, src=TimezoneUTC()):
    """String Formatted Date & Time.

    An RFC 1123 date string.
    e.g. Tue, 15 Nov 1994 12:45:26 GMT

    Args:
        datetime (datetime): Datetime object. (Optional)
        destination_tz (str): Destination Timezone.
            List of valid entries in timezones attribute.

    Returns string formatted date.
    """
    datetime = to_timezone(datetime, dst=TimezoneGMT(), src=src)

    return(datetime.strftime('%a, %d %b %Y %H:%M:%S %Z'))
