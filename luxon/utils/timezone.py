# -*- coding: utf-8 -*-
# Copyright (c) 2018-2020 Christiaan Frans Rademan <chris@fwiw.co.za>.
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
import time
import calendar
from datetime import datetime as py_datetime
from datetime import tzinfo, timedelta
from math import floor

import pytz
from tzlocal import get_localzone
from dateutil.parser import parse as dateutil_parse

from luxon import g

_cached_time_zone_system = None
_cached_time_zone_app = None


if time.gmtime(0).tm_year != 1970:
    raise Exception('System does not provide unix epoch time, incompatible')


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
        app_timezone = g.app.config.get('application',
                                        'timezone')

        if app_timezone == 'local' or app_timezone == 'server':
            _cached_time_zone_app = get_localzone()
        else:
            _cached_time_zone_app = pytz.timezone(app_timezone)

    return _cached_time_zone_app


def TimezoneUser():
    try:
        usertz = g.current_request.get_header('X-Timezone')
        if usertz is not None:
            return pytz.timezone(usertz)
    except Exception:
        return TimezoneApp()


def parse_datetime(datetime):
    if isinstance(datetime, (int, float,)):
        pdt = py_datetime.fromtimestamp(datetime, tz=TimezoneUTC())
        return pdt
    if isinstance(datetime, py_datetime):
        return datetime

    if not isinstance(datetime, str):
        raise ValueError("datetime value not" +
                         " 'str' or 'datetime'")

    try:
        return dateutil_parse(datetime)
    except ValueError:
        raise ValueError('datetime value %r does not' % datetime +
                         ' match known formats')


def to_timezone(datetime, dst=TimezoneSystem(), src=None, fallback=None):
    if not isinstance(datetime, py_datetime):
        datetime = parse_datetime(datetime)

    if src is None and datetime.tzinfo is None:
        if fallback is None:
            raise ValueError('timezone modification not possible' +
                             ' from naive datetime')
        else:
            src = fallback

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
    # Set datetime to UTC without altering.
    return to_timezone(datetime, dst=TimezoneUTC(), src=TimezoneUTC())


def to_utc(datetime, src=None, fallback=None):
    return to_timezone(datetime, dst=TimezoneUTC(),
                       src=src, fallback=fallback)


def to_gmt(datetime, src=None, fallback=None):
    return to_timezone(datetime, dst=TimezoneGMT(),
                       src=src, fallback=fallback)


def to_system(datetime, src=None, fallback=None):
    return to_timezone(datetime, dst=TimezoneSystem(),
                       src=src, fallback=None)


def to_app(datetime, src=None, fallback=None):
    return to_timezone(datetime, dst=TimezoneApp(),
                       src=src, fallback=fallback)


def to_user(datetime, src=None, fallback=None):
    return to_timezone(datetime, dst=TimezoneUser(),
                       src=src, fallback=fallback)


def format_datetime(datetime):
    """String Formatted Date & Time.

    Many countries have adopted the ISO standard of year-month-day
    hour:minute:seconds. For
        example, 2015-03-30T10:15:25+00:00

    Appends short timezone name.

    Args:
        datetime (datetime): Datetime object.

    Returns string formatted date.
    """
    tz = datetime.strftime('%z')
    if tz and tz != '':
        tz = tz[0] + tz[1] + tz[2] + ':' + tz[3] + tz[4]
        return(datetime.strftime('%Y-%m-%dT%H:%M:%S') + tz)

    raise ValueError('Cannot ISO format naive datetime')


def format_pretty(datetime):
    return(datetime.strftime('%Y-%m-%d %H:%M:%S'))


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


def epoch():
    return time.time()


def format_iso8601(datetime, ms=True, always_offset=False):
    """String Formatted Date & Time.

    An ISO 8601 date string.
    e.g. 2011-04-14T16:00:49Z

    Args:
        datetime (datetime): Datetime object.

    Returns string ISO8601 formatted date+time.
    """
    offset = datetime.utcoffset()
    if ms:
        ms = '.' + datetime.strftime('%f')[0:3]
    else:
        ms = ''

    if offset is None:
        raise ValueError('Cannot ISO8601 format naive datetime')
    if not always_offset and offset == timedelta(hours=0):
        return(datetime.strftime('%Y-%m-%dT%H:%M:%S' + ms + 'Z'))
    else:
        seconds = offset.total_seconds()
        hours, remainder = divmod(seconds, 3600)
        minutes, remainder = divmod(remainder, 60)
        if seconds >= 0:
            tz = ("+{:02d}".format(int(hours)) +
                  ":{:02d}".format(int(minutes)))
        else:
            tz = ("{:03d}".format(int(hours)) +
                  ":{:02d}".format(int(minutes)))

        return(datetime.strftime('%Y-%m-%dT%H:%M:%S' + ms) + tz)


def add_date(orig_date, days=None, weeks=None, months=None):
    if days:
        orig_date = (orig_date + timedelta(days=days))

    if weeks:
        orig_date = (orig_date + timedelta(weeks=weeks))

    if months:
        # advance year and month by one month
        new_year = orig_date.year
        new_month = orig_date.month + months
        # note: in datetime.date, months go from 1 to 12
        if new_month > 12:
            new_year += floor(new_month / 12)
            new_month = new_month % 12

        last_day_of_month = calendar.monthrange(new_year, new_month)[1]
        new_day = min(orig_date.day, last_day_of_month)

        orig_date = orig_date.replace(year=new_year,
                                      month=new_month,
                                      day=new_day)

    return orig_date


def calc_next_expire(metric, span, expired):
    if metric == 'days':
        new_expire = add_date(expired,
                              days=span)
    elif metric == 'weeks':
        new_expire = add_date(expired,
                              weeks=span)
    elif metric == 'months':
        new_expire = add_date(expired,
                              months=span)
    return new_expire


def daterange(start_date, end_date):
    if end_date > start_date:
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

        yield end_date

    if start_date > end_date:
        for n in range(int((start_date - end_date).days)):
            yield start_date + timedelta(n)
