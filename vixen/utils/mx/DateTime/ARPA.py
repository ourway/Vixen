""" This module provides a set of constructors and routines to convert
    between DateTime[Delta] instances and ARPA representations of date
    and time. The format is specified by RFC822 + RFC1123.

    Note: Timezones are only interpreted by ParseDateTimeGMT(). All
    other constructors silently ignore the time zone information.

    Copyright (c) 1998-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

"""
import DateTime,Timezone
import re,string

# Grammar: RFC822 + RFC1123 + depreciated RFC850
_litday = '(?P<litday>Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*'
_litmonth = '(?P<litmonth>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'\
            '[a-z]*'
_date = ('(?:(?P<day>\d?\d)(?: +' + _litmonth + 
         ' +|-(?P<month>\d?\d)-)(?P<year>(?:\d\d)?\d\d))')
_zone = Timezone.zone
_time = ('(?:(?P<hour>\d\d):(?P<minute>\d\d)'
         '(?::(?P<second>\d\d))?(?: +'+_zone+')?)')
#       Timezone information is made optional because some mail apps
#       forget to add it (most of these seem to be spamming engines, btw).
#       It defaults to UTC.

_arpadate = '(?:'+ _litday + ',? )? *' + _date
_arpadatetime = '(?:'+ _litday + ',? )? *' + _date + ' +' + _time

#       We are not strict about the extra characters: some applications
#       add extra information to the date header field. Additional spaces
#       between the fields and extra characters in the literal day
#       and month fields are also silently ignored.

arpadateRE = re.compile(_arpadate)
arpadatetimeRE = re.compile(_arpadatetime)

# Translation tables
litdaytable = {'mon':0, 'tue':1, 'wed':2, 'thu':3, 'fri':4, 'sat':5, 'sun':6 }
litmonthtable = {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6,
                 'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12 }
_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
_months = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec' ]

def ParseDate(arpastring,parse_arpadate=arpadateRE.match,

              strip=string.strip,atoi=string.atoi,atof=string.atof,
              lower=string.lower):

    """ParseDate(arpastring)

       Returns a DateTime instance reflecting the given ARPA
       date. Only the date part is parsed, any time part will be
       ignored. The instance's time is set to 0:00:00.

    """
    s = strip(arpastring)
    date = parse_arpadate(s)
    if not date:
        raise ValueError,'wrong format'
    litday,day,litmonth,month,year = date.groups()
    if len(year) == 2:
        year = DateTime.add_century(atoi(year))
    else:
        year = atoi(year)
    if litmonth:
        litmonth = lower(litmonth)
        try:
            month = litmonthtable[litmonth]
        except KeyError:
            raise ValueError,'wrong month format'
    else:
        month = atoi(month)
    day = atoi(day)
    # litday and timezone are ignored
    return DateTime.DateTime(year,month,day)

def ParseDateTime(arpastring,parse_arpadatetime=arpadatetimeRE.match,

                  strip=string.strip,atoi=string.atoi,atof=string.atof,
                  lower=string.lower):

    """ParseDateTime(arpastring)

       Returns a DateTime instance reflecting the given ARPA date assuming
       it is local time (timezones are silently ignored).
    """
    s = strip(arpastring)
    date = parse_arpadatetime(s)
    if not date:
        raise ValueError,'wrong format or unknown time zone'
    litday,day,litmonth,month,year,hour,minute,second,zone = date.groups()
    if len(year) == 2:
        year = DateTime.add_century(atoi(year))
    else:
        year = atoi(year)
    if litmonth:
        litmonth = lower(litmonth)
        try:
            month = litmonthtable[litmonth]
        except KeyError:
            raise ValueError,'wrong month format'
    else:
        month = atoi(month)
    day = atoi(day)
    hour = atoi(hour)
    minute = atoi(minute)
    if second is None:
        second = 0.0
    else:
        second = atof(second)
    # litday and timezone are ignored
    return DateTime.DateTime(year,month,day,hour,minute,second)

def ParseDateTimeGMT(arpastring,parse_arpadatetime=arpadatetimeRE.match,

                     strip=string.strip,atoi=string.atoi,atof=string.atof,
                     lower=string.lower):

    """ParseDateTimeGMT(arpastring)

       Returns a DateTime instance reflecting the given ARPA date converting
       it to UTC (timezones are honored).
    """
    s = strip(arpastring)
    date = parse_arpadatetime(s)
    if not date:
        raise ValueError,'wrong format or unknown time zone'
    litday,day,litmonth,month,year,hour,minute,second,zone = date.groups()
    if len(year) == 2:
        year = DateTime.add_century(atoi(year))
    else:
        year = atoi(year)
    if litmonth:
        litmonth = lower(litmonth)
        try:
            month = litmonthtable[litmonth]
        except KeyError:
            raise ValueError,'wrong month format'
    else:
        month = atoi(month)
    day = atoi(day)
    hour = atoi(hour)
    minute = atoi(minute)
    if second is None:
        second = 0.0
    else:
        second = atof(second)
    offset = Timezone.utc_offset(zone)
    # litday is ignored
    return DateTime.DateTime(year,month,day,hour,minute,second) - offset

# Alias
ParseDateTimeUTC = ParseDateTimeGMT

def str(datetime,tz=None):

    """str(datetime,tz=DateTime.tz_offset(datetime))

    Returns the datetime instance as ARPA date string. tz can be given
    as DateTimeDelta instance providing the time zone difference from
    datetime's zone to UTC. It defaults to
    DateTime.tz_offset(datetime) which assumes local time. """

    if tz is None:
        tz = datetime.gmtoffset()
    return '%s, %02i %s %04i %02i:%02i:%02i %+03i%02i' % (
        _days[datetime.day_of_week], datetime.day, 
        _months[datetime.month], datetime.year,
        datetime.hour, datetime.minute, datetime.second,
        tz.hour,tz.minute)

def strGMT(datetime):

    """ strGMT(datetime)

    Returns the datetime instance as ARPA date string assuming it
    is given in GMT. """

    return '%s, %02i %s %04i %02i:%02i:%02i GMT' % (
        _days[datetime.day_of_week], datetime.day, 
        _months[datetime.month], datetime.year,
        datetime.hour, datetime.minute, datetime.second)

def strUTC(datetime):

    """ strUTC(datetime)

    Returns the datetime instance as ARPA date string assuming it
    is given in UTC. """

    return '%s, %02i %s %04i %02i:%02i:%02i UTC' % (
        _days[datetime.day_of_week], datetime.day, 
        _months[datetime.month], datetime.year,
        datetime.hour, datetime.minute, datetime.second)

def _test():
    import sys, os, rfc822
    file = os.path.join(os.environ['HOME'], 'nsmail/Inbox')
    f = open(file, 'r')
    while 1:
        m = rfc822.Message(f)
        if not m:
            break
        print 'From:', m.getaddr('from')
        print 'To:', m.getaddrlist('to')
        print 'Subject:', m.getheader('subject')
        raw = m.getheader('date')
        try:
            date = ParseDateTimeUTC(raw)
            print 'Date:',strUTC(date)
        except ValueError,why:
            print 'PROBLEMS:',repr(raw),'-->',why
            raw_input('...hit return to continue')
        print
        # Netscape mail file
        while 1:
            line = f.readline()
            if line[:6] == 'From -':
                break

if __name__ == '__main__':
    _test()
