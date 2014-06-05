""" This module provides a set of constructors and routines to convert
    between DateTime[Delta] instances and ISO representations of date
    and time.

    Note: Timezones are only interpreted by ParseDateTimeGMT(). All
    other constructors silently ignore the time zone information.

    Copyright (c) 1998-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author.

"""
import DateTime,Timezone
import re,string

# Grammar: ISO 8601 (not all, but what we need from it)
_year = '(?P<year>\d?\d\d\d)'
_month = '(?P<month>\d?\d)'
_day = '(?P<day>\d?\d)'
_hour = '(?P<hour>\d?\d)'
_minute = '(?P<minute>\d?\d)'
_second = '(?P<second>\d?\d(?:\.\d+)?)'
_sign = '(?P<sign>[-+])'
_week = 'W(?P<week>\d?\d)'
_zone = Timezone.isozone

_weekdate = _year + '-?(?:' + _week + '-?' + _day + '?)?'
_date = _year + '-?' + '(?:' + _month + '-?' + _day + '?)?'
_time = _hour + ':?' + _minute + ':?' + _second + '?(?:' + _zone + ')?'

isodatetimeRE = re.compile(_date + '(?:[ T]' + _time + ')?$')
isodateRE = re.compile(_date + '$')
isotimeRE = re.compile(_time + '$')
isodeltaRE = re.compile(_sign + '?' + _time + '$')
isoweekRE = re.compile(_weekdate + '$')
isoweektimeRE = re.compile(_weekdate + '(?:[ T]' + _time + ')?$')

def WeekTime(year,isoweek=1,isoday=1,hour=0,minute=0,second=0.0):

    """Week(year,isoweek=1,isoday=1,hour=0,minute=0,second=0.0)

       Returns a DateTime instance pointing to the given ISO week and
       day.  isoday defaults to 1, which corresponds to Monday in the
       ISO numbering. The time part is set as given.

    """
    d = DateTime.DateTime(year,1,1,hour,minute,second)
    if d.iso_week[0] == year:
        # 1.1. belongs to year (backup to Monday)
        return d + (-d.day_of_week + 7 * (isoweek-1) + isoday-1)
    else:
        # 1.1. belongs to year-1 (advance to next Monday)
        return d + (7-d.day_of_week + 7 * (isoweek-1) + isoday-1)

# Alias
Week = WeekTime

# Aliases for the other constructors (they all happen to already use
# ISO format)
Date = DateTime.Date
Time = DateTime.Time
TimeDelta = DateTime.TimeDelta

def ParseDateTime(isostring,parse_isodatetime=isodatetimeRE.match,

                  strip=string.strip,atoi=string.atoi,atof=string.atof):

    """ParseDateTime(isostring)

       Returns a DateTime instance reflecting the given ISO date. A
       time part is optional and must be delimited from the date by a
       space or 'T'.

       Time zone information is parsed, but not evaluated.

    """
    s = strip(isostring)
    date = parse_isodatetime(s)
    if not date:
        raise ValueError,'wrong format, use YYYY-MM-DD HH:MM:SS'
    year,month,day,hour,minute,second,zone = date.groups()
    year = atoi(year)
    if month is None:
        month = 1
    else:
        month = atoi(month)
    if day is None:
        day = 1
    else:
        day = atoi(day)
    if hour is None:
        hour = 0
    else:
        hour = atoi(hour)
    if minute is None:
        minute = 0
    else:
        minute = atoi(minute)
    if second is None:
        second = 0.0
    else:
        second = atof(second)
    return DateTime.DateTime(year,month,day,hour,minute,second)

def ParseDateTimeGMT(isostring,parse_isodatetime=isodatetimeRE.match,

                     strip=string.strip,atoi=string.atoi,atof=string.atof):

    """ParseDateTimeGMT(isostring)

       Returns a DateTime instance in UTC reflecting the given ISO
       date. A time part is optional and must be delimited from the
       date by a space or 'T'. Timezones are honored.

    """
    s = strip(isostring)
    date = parse_isodatetime(s)
    if not date:
        raise ValueError,'wrong format, use YYYY-MM-DD HH:MM:SS'
    year,month,day,hour,minute,second,zone = date.groups()
    year = atoi(year)
    if month is None:
        month = 1
    else:
        month = atoi(month)
    if day is None:
        day = 1
    else:
        day = atoi(day)
    if hour is None:
        hour = 0
    else:
        hour = atoi(hour)
    if minute is None:
        minute = 0
    else:
        minute = atoi(minute)
    if second is None:
        second = 0.0
    else:
        second = atof(second)
    offset = Timezone.utc_offset(zone)
    return DateTime.DateTime(year,month,day,hour,minute,second) - offset

# Alias
ParseDateTimeUTC = ParseDateTimeGMT

def ParseDate(isostring,parse_isodate=isodateRE.match,

              strip=string.strip,atoi=string.atoi,atof=string.atof):

    """ParseDate(isostring)

       Returns a DateTime instance reflecting the given ISO date. A
       time part may not be included.

    """
    s = strip(isostring)
    date = parse_isodate(s)
    if not date:
        raise ValueError,'wrong format, use YYYY-MM-DD'
    year,month,day = date.groups()
    year = atoi(year)
    if month is None:
        month = 1
    else:
        month = atoi(month)
    if day is None:
        day = 1
    else:
        day = atoi(day)
    return DateTime.DateTime(year,month,day)

def ParseWeek(isostring,parse_isoweek=isoweekRE.match,

              strip=string.strip,atoi=string.atoi,atof=string.atof):

    """ParseWeek(isostring)

       Returns a DateTime instance reflecting the given ISO date. A
       time part may not be included.

    """
    s = strip(isostring)
    date = parse_isoweek(s)
    if not date:
        raise ValueError,'wrong format, use yyyy-Www-d, e.g. 1998-W01-1'
    year,week,day = date.groups()
    year = atoi(year)
    if week is None:
        week = 1
    else:
        week = atoi(week)
    if day is None:
        day = 1
    else:
        day = atoi(day)
    return Week(year,week,day)

def ParseWeekTime(isostring,parse_isoweektime=isoweektimeRE.match,

                  strip=string.strip,atoi=string.atoi,atof=string.atof):

    """ParseWeekTime(isostring)

       Returns a DateTime instance reflecting the given ISO date. A
       time part is optional and must be delimited from the date by a
       space or 'T'.

    """
    s = strip(isostring)
    date = parse_isoweektime(s)
    if not date:
        raise ValueError,'wrong format, use e.g. "1998-W01-1 12:00:30"'
    year,week,day,hour,minute,second,zone = date.groups()
    year = atoi(year)
    if week is None:
        week = 1
    else:
        week = atoi(week)
    if day is None:
        day = 1
    else:
        day = atoi(day)
    if hour is None:
        hour = 0
    else:
        hour = atoi(hour)
    if minute is None:
        minute = 0
    else:
        minute = atoi(minute)
    if second is None:
        second = 0.0
    else:
        second = atof(second)
    return WeekTime(year,week,day,hour,minute,second)

def ParseTime(isostring,parse_isotime=isotimeRE.match,

              strip=string.strip,atoi=string.atoi,atof=string.atof):

    """ParseTime(isostring)

       Returns a DateTimeDelta instance reflecting the given ISO time.
       Hours and minutes must be given, seconds are
       optional. Fractions of a second may also be used,
       e.g. 12:23:12.34.

    """
    s = strip(isostring)
    time = parse_isotime(s)
    if not time:
        raise ValueError,'wrong format, use HH:MM:SS'
    hour,minute,second,zone = time.groups()
    hour = atoi(hour)
    minute = atoi(minute)
    if second is not None:
        second = atof(second)
    else:
        second = 0.0
    return DateTime.TimeDelta(hour,minute,second)

def ParseTimeDelta(isostring,parse_isodelta=isodeltaRE.match,

                   strip=string.strip,atoi=string.atoi,atof=string.atof):

    """ParseTimeDelta(isostring)

       Returns a DateTimeDelta instance reflecting the given ISO time
       as delta. Hours and minutes must be given, seconds are
       optional. Fractions of a second may also be used,
       e.g. 12:23:12.34. In addition to the ISO standard a sign may be
       prepended to the time, e.g. -12:34.

    """
    s = strip(isostring)
    time = parse_isodelta(s)
    if not time:
        raise ValueError,'wrong format, use [-]HH:MM:SS'
    sign,hour,minute,second,zone = time.groups()
    hour = atoi(hour)
    minute = atoi(minute)
    if second is not None:
        second = atof(second)
    else:
        second = 0.0
    if sign and sign == '-':
        return -DateTime.TimeDelta(hour,minute,second)
    else:
        return DateTime.TimeDelta(hour,minute,second)

def ParseAny(isostring):

    """ParseAny(isostring)

       Parses the given string and tries to convert it to a
       DateTime[Delta] instance.

    """
    try:
        return ParseDateTime(isostring)
    except ValueError:
        pass
    try:
        return ParseWeekTime(isostring)
    except ValueError:
        pass
    try:
        return ParseTimeDelta(isostring)
    except ValueError:
        raise ValueError,'unsupported format: "%s"' % isostring

def str(datetime,tz=None):

    """str(datetime,tz=DateTime.tz_offset(datetime))

       Returns the datetime instance as ISO date string. tz can be
       given as DateTimeDelta instance providing the time zone
       difference from datetime's zone to UTC. It defaults to
       DateTime.tz_offset(datetime) which assumes local time.

    """
    if tz is None:
        tz = datetime.gmtoffset()
    return '%04i-%02i-%02i %02i:%02i:%02i%+03i%02i' % (
        datetime.year, datetime.month, datetime.day, 
        datetime.hour, datetime.minute, datetime.second,
        tz.hour,tz.minute)

def strGMT(datetime):

    """strGMT(datetime)

       Returns the datetime instance as ISO date string assuming it is
       given in GMT.

    """
    return '%04i-%02i-%02i %02i:%02i:%02i+0000' % (
        datetime.year, datetime.month, datetime.day, 
        datetime.hour, datetime.minute, datetime.second)

def strUTC(datetime):

    """strUTC(datetime)

       Returns the datetime instance as ISO date string assuming it is
       given in UTC.

    """
    return '%04i-%02i-%02i %02i:%02i:%02i+0000' % (
        datetime.year, datetime.month, datetime.day, 
        datetime.hour, datetime.minute, datetime.second)

# Testing
if __name__ == '__main__':
    e = DateTime.Date(1900,1,1)
    for i in range(100000):
        d = e + i
        year,week,day = d.iso_week
        c = WeekTime(year,week,day)
        if d != c:
            print ' Check %s (given; %i) != %s (parsed)' % (d,d.day_of_week,c)
        elif i % 1000 == 0:
            print d,'ok'
