""" Python part of the low-level DateTime[Delta] type implementation.

    Copyright (c) 1998-2001, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.
"""
# Import C extension module
from mxDateTime import *
from mxDateTime import __version__

# Singletons
oneSecond = DateTimeDelta(0,0,0,1)
oneMinute = DateTimeDelta(0,0,1)
oneHour = DateTimeDelta(0,1)
oneDay = DateTimeDelta(1)
oneWeek = DateTimeDelta(7)
Epoch = DateTimeFromAbsDateTime(1,0)

# Shortcuts for pickle; for backward compatibility only (they are now
# defined in __init__.py to further reduce the pickles length)
def _DT(absdate,abstime):
    return DateTimeFromAbsDateTime(absdate,abstime)
def _DTD(seconds):
    return DateTimeDeltaFromSeconds(seconds)

# Module init
class modinit:

    global _time,_string,_math,_types
    import time,string,math,types
    _time = time
    _string = string
    _math = math
    _types = types

del modinit

### Helpers

def _isstring(arg,

              isinstance=isinstance, types=_types):
    
    if isinstance(arg, types.StringType):
        return 1
    try:
        if isinstance(arg, types.UnicodeType):
            return 1
    except AttributeError:
        pass
    return 0

### Compatibility APIs

# Aliases and functions to make 'from mx.DateTime import *' work much
# like 'from time import *'

def localtime(ticks=None,
              # Locals:
              time=_time.time,float=float,localtime=_time.localtime,
              round=round,int=int,DateTime=DateTime,floor=_math.floor):

    """localtime(ticks=None)

       Construct a DateTime instance using local time from ticks.  If
       ticks are not given, it defaults to the current time.  The
       result is similar to time.localtime(). Fractions of a second
       are rounded to the nearest micro-second.

    """
    if ticks is None:
        ticks = time()
    else:
        ticks = float(ticks)
    ticks = round(ticks, 6)
    fticks = floor(ticks)
    Y,M,D,h,m,s = localtime(fticks)[:6]
    s = s + (ticks - fticks)
    return DateTime(Y,M,D,h,m,s)

def gmtime(ticks=None,
           # Locals:
           time=_time.time,float=float,gmtime=_time.gmtime,
           round=round,int=int,DateTime=DateTime,floor=_math.floor):

    """gmtime(ticks=None)

       Construct a DateTime instance using UTC time from ticks.  If
       ticks are not given, it defaults to the current time.  The
       result is similar to time.gmtime(). Fractions of a second are
       rounded to the nearest micro-second.

    """
    if ticks is None:
        ticks = time()
    else:
        ticks = float(ticks)
    ticks = round(ticks, 6)
    fticks = floor(ticks)
    Y,M,D,h,m,s = gmtime(ticks)[:6]
    s = s + (ticks - fticks)
    return DateTime(Y,M,D,h,m,s)

def mktime((year,month,day,hour,minute,second,dow,doy,dst),
           # Locals:
           DateTime=DateTime):

    """mktime((year,month,day,hour,minute,second,dow,doy,dst))

       Same as the DateTime() constructor accept that the interface
       used is compatible to the similar time.mktime() API.

       Note that the tuple elements dow, doy and dst are not used in
       any way.
      
    """
    return DateTime(year,month,day,hour,minute,second)

def ctime(datetime):

    """ctime(datetime)

       Returns a string representation of the given DateTime instance
       using the current locale's default settings.

    """
    return datetime.strftime('%c')

def today(hour=0,minute=0,second=0.0,
          # Locals:
          localtime=_time.localtime,time=_time.time,DateTime=DateTime):

    """today(hour=0,minute=0,second=0.0)

       Returns a DateTime instance for today (in local time) at the
       given time (defaults to midnight).

    """
    Y,M,D = localtime(time())[:3]
    return DateTime(Y,M,D,hour,minute,second)

def TimeDelta(hours=0.0,minutes=0.0,seconds=0.0,
              # Locals:
              DateTimeDelta=DateTimeDelta):

    """TimeDelta(hours=0.0,minutes=0.0,seconds=0.0)

       Returns a DateTimeDelta-object reflecting the given time
       delta. Seconds can be given as float to indicate fractions.

    """
    return DateTimeDelta(0,hours,minutes,seconds)

def gm2local(datetime):

    """ gm2local(datetime)

        Convert a DateTime instance holding UTC time to a DateTime
        instance using local time.

    """
    return localtime(datetime.gmticks())

def local2gm(datetime):

    """ local2gm(datetime)

        Convert a DateTime instance holding local time to a DateTime
        instance using UTC time.

    """
    return gmtime(datetime.ticks())

# Alias
gmt = utc

# Default value for DateTimeFromTJD's tjd_myriad parameter
current_myriad = localtime().tjd_myriad

def DateTimeFromTJD(tjd,tjd_myriad=current_myriad):

    """ DateTimeFromTJD(tjd[,myriad])

        Return a DateTime instance for the given Truncated Julian Day.
        myriad defaults to the TJD myriad current at package import
        time.

        Note that this version of Truncated Julian Day number does
        real truncation of important information. It's use is
        discouraged and unsupported.

    """
    return DateTimeFromAbsDays(tjd + tjd_myriad * 10000.0 - 1721425.0)

def DateTimeFromJDN(jdn):

    """ DateTimeFromJDN(jdn)

        Return a DateTime instance for the given Julian Day Number.

        References:
        -----------
        Gregorian 2000-01-01 12:00:00 corresponds to JDN 2451545.0.
        Gregorian 1858-11-17 00:00:00.00 corresponds to JDN 2400000.5; MJD 0.0.
        Julian -4712-01-01 12:00:00.00 corresponds to JDN 0.0.
        Gregorian -4713-11-24 12:00:00.00 corresponds to JDN 0.0.

    """
    return DateTimeFromAbsDays(jdn - 1721425.5)

def DateTimeFromMJD(mjd):

    """ DateTimeFromMJD(mjd)

        Return a DateTime instance for the given Modified Julian Day
        (MJD). The MJD is calculated the same way as the JDN except
        that 1858-11-17 00:00:00.00 is taken as origin of the scale.

    """
    return DateTimeFromAbsDays(mjd + 678575.0)

def DateTimeFrom(*args, **kws):

    """ DateTimeFrom(*args, **kws)

        Generic DateTime instance constructor. Can handle parsing
        strings, numbers and keywords.

    """
    if len(args) == 1:
        # Single argument
        arg = args[0]
        argtype = type(arg)
        if _isstring(arg):
            import Parser
            return apply(Parser.DateTimeFromString, args, kws)
        elif argtype is DateTimeType:
            return arg
        elif argtype is DateTimeDeltaType:
            raise TypeError,'cannot convert DateTimeDelta to DateTime'
        else:
            try:
                value = float(arg)
            except (TypeError, ValueError):
                value = int(arg)
            assert not kws
            return DateTimeFromTicks(value)

    elif len(args) > 1:
        # More than one argument
        if len(args) == 2 and _isstring(args[0]) and _isstring(args[1]):
            # interpret as date and time string
            import Parser
            return apply(Parser.DateTimeFromString,
                         (args[0] + ' ' + args[1],),
                         kws)

        # Assume the arguments are the same as for DateTime()
        return apply(DateTime, args, kws)

    elif len(kws) > 0:
        # Keyword arguments; add defaults... today at 0:00:00
        hour = kws.get('hour',0)
        minute = kws.get('minute',0)
        second = kws.get('second',0)
        today = now()
        day = kws.get('day',today.day)
        month = kws.get('month',today.month)
        year = kws.get('year',today.year)
        return DateTime(year,month,day,hour,minute,second)

    else:
        raise TypeError,'cannot convert arguments to DateTime'

def DateTimeDeltaFrom(*args, **kws):

    """ DateTimeDeltaFrom(*args, **kws)

        Generic DateTimeDelta instance constructor. Can handle parsing
        strings, numbers and keywords.

    """
    if len(args) == 1:
        # Single argument
        arg = args[0]
        if _isstring(arg):
            import Parser
            return apply(Parser.DateTimeDeltaFromString, args, kws)
        elif type(arg) is DateTimeDeltaType:
            return arg
        elif type(arg) is DateTimeType:
            raise TypeError,'cannot convert DateTime to DateTimeDelta'
        else:
            try:
                value = float(arg)
            except TypeError:
                value = int(arg)
            assert not kws
            return DateTimeDeltaFromSeconds(value)

    elif len(args) > 1:
        # Assume the arguments are the same as for DateTimeDelta()
        return apply(DateTimeDelta, args, kws)

    elif len(kws) > 0:
        # Keyword arguments; default: 00:00:00:00.00
        hours = kws.get('hours',0)
        minutes = kws.get('minutes',0)
        seconds = kws.get('seconds',0.0)
        days = kws.get('days',0)
        return DateTimeDelta(days,hours,minutes,seconds)

    else:
        raise TypeError,'cannot convert arguments to DateTimeDelta'

def TimeDeltaFrom(*args, **kws):

    """ TimeDeltaFrom(*args, **kws)

        Generic TimeDelta instance constructor. Can handle parsing
        strings, numbers and keywords.

    """
    if len(args) > 1:
        # Assume the arguments are the same as for TimeDelta(): without
        # days part !
        return apply(DateTimeDelta, (0,)+args, kws)
    else:
        # Otherwise treat the arguments just like for DateTimeDelta
        # instances.
        return apply(DateTimeDeltaFrom, args, kws)

def DateFromTicks(ticks,
                  # Locals:
                  DateTime=DateTime,localtime=_time.localtime):

    """ DateFromTicks(ticks)

        Constructs a DateTime instance pointing to the local time date
        at 00:00:00.00 (midnight) indicated by the given ticks value.
        The time part is ignored.

    """
    return apply(DateTime, localtime(ticks)[:3])

def TimestampFromTicks(ticks,
                       # Locals:
                       DateTime=DateTime,localtime=_time.localtime):

    """ TimestampFromTicks(ticks)

        Constructs a DateTime instance pointing to the local date and
        time indicated by the given ticks value.

    """
    return apply(DateTime, localtime(ticks)[:6])

def TimeFromTicks(ticks,
                  # Locals:
                  DateTimeDelta=DateTimeDelta,localtime=_time.localtime):

    """ TimeFromTicks(ticks)

        Constructs a DateTimeDelta instance pointing to the local time
        indicated by the given ticks value. The date part is ignored.

    """
    return apply(DateTimeDelta, (0,) + localtime(ticks)[3:6])

# Aliases
utctime = gmtime
utc2local = gm2local
local2utc = local2gm
DateTimeFromTicks = localtime
Date = DateTime
Time = TimeDelta
Timestamp = DateTime
DateFrom = DateTimeFrom # XXX should only parse the date part !
TimeFrom = TimeDeltaFrom
TimestampFrom = DateTimeFrom
GregorianDateTime = DateTime
GregorianDate = Date
JulianDate = JulianDateTime


### For backward compatibility (these are depreciated):

def gmticks(datetime):

    """gmticks(datetime)

       [DEPRECIATED: use the .gmticks() method]
    
       Returns a ticks value based on the values stored in
       datetime under the assumption that they are given in UTC,
       rather than local time.

    """
    return datetime.gmticks()

# Alias
utcticks = gmticks

def tz_offset(datetime,
              # Locals:
              oneSecond=oneSecond):

    """tz_offset(datetime)

       [DEPRECIATED: use the .gmtoffset() method]
    
       Returns a DateTimeDelta instance representing the UTC
       offset for datetime assuming that the stored values refer
       to local time. If you subtract this value from datetime,
       you'll get UTC time.

    """
    return datetime.gmtoffset()

### Constants (only English; see Locale.py for other languages)

# Weekdays
Monday =        0
Tuesday =       1
Wednesday =     2
Thursday =      3
Friday =        4
Saturday =      5
Sunday =        6
# as mapping
Weekday = {'Saturday': 5, 6: 'Sunday', 'Sunday': 6, 'Thursday': 3,
           'Wednesday': 2, 'Friday': 4, 'Tuesday': 1, 'Monday': 0,
           5: 'Saturday', 4: 'Friday', 3: 'Thursday', 2: 'Wednesday',
           1: 'Tuesday', 0: 'Monday'}

# Months
January =       1
February =      2
March =         3
April =         4
May =           5
June =          6
July =          7
August =        8 
September =     9
October =       10
November =      11
December =      12
# as mapping
Month = {2: 'February', 3: 'March', None: 0, 'July': 7, 11: 'November',
    'December': 12, 'June': 6, 'January': 1, 'September': 9, 'August':
    8, 'March': 3, 'November': 11, 'April': 4, 12: 'December', 'May':
    5, 10: 'October', 9: 'September', 8: 'August', 7: 'July', 6:
    'June', 5: 'May', 4: 'April', 'October': 10, 'February': 2, 1:
    'January', 0: None}

# Limits (see also the range checks in mxDateTime.c)
MaxDateTime = DateTime(5867440,12,31) 
MinDateTime = DateTime(-5851455,1,1)
MaxDateTimeDelta = DateTimeDeltaFromSeconds(2147483647 * 86400.0)
MinDateTimeDelta = -MaxDateTimeDelta

###

class RelativeDateTime:

    """RelativeDateTime(years=0,months=0,days=0,
                  hours=0,minutes=0,seconds=0,
                  year=0,month=0,day=0,
                  hour=None,minute=None,second=None,
                  weekday=None,weeks=None)

       Returns a RelativeDateTime instance for the specified relative
       time. The constructor handles keywords, so you'll only have to
       give those parameters which should be changed when you add the
       relative to an absolute DateTime instance.

       Adding RelativeDateTime instances is supported with the
       following rules: deltas will be added together, right side
       absolute values override left side ones.

       Adding RelativeDateTime instances to DateTime instances will
       return DateTime instances with the appropriate calculations
       applied, e.g. to get a DateTime instance for the first of next
       month, you'd call now() + RelativeDateTime(months=+1,day=1).

    """
    years = 0
    months = 0
    days = 0
    year = None
    month = 0
    day = 0
    hours = 0
    minutes = 0
    seconds = 0
    hour = None
    minute = None
    second = None
    weekday = None

    # cached hash value
    _hash = None

    # For Zope security:
    __roles__ = None
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self,
                 years=0,months=0,days=0,
                 hours=0,minutes=0,seconds=0,
                 year=None,month=None,day=None,
                 hour=None,minute=None,second=None,
                 weekday=None,weeks=0):
        
        self.years = years
        self.months = months
        self.days = days + weeks*7
        self.year = year
        self.month = month
        self.day = day
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.hour = hour
        self.minute = minute
        self.second = second
        if weekday is not None:
            #  Make sure we've got a 2-tuple
            assert len(weekday) == 2
            self.weekday = weekday

    def __add__(self,other,
                # Locals:
                isinstance=isinstance):

        if isinstance(other,RelativeDateTime):
            # RelativeDateTime (self) + RelativeDateTime (other)

            r = RelativeDateTime()
            # date deltas
            r.years = self.years + other.years
            r.months = self.months + other.months
            r.days = self.days + other.days
            # absolute entries of other override those in self, if given
            r.year = other.year or self.year
            r.month = other.month or self.month
            r.day = other.day or self.day
            r.weekday = other.weekday or self.weekday
            # time deltas
            r.hours = self.hours + other.hours
            r.minutes = self.minutes + other.minutes
            r.seconds = self.seconds + other.seconds
            # absolute entries of other override those in self, if given
            r.hour = other.hour or self.hour
            r.minute = other.minute or self.minute
            r.second = other.second or self.second
            return r

        else:
            raise TypeError,"can't add the two types"

    def __radd__(self,other,
                 # Locals:
                 isinstance=isinstance,DateTimeType=DateTimeType,
                 DateTime=DateTime,DateTimeDelta=DateTimeDelta):

        if isinstance(other,DateTimeType):
            # DateTime (other) + RelativeDateTime (self)

            # date
            if self.year is None:
                year = other.year + self.years
            else:
                year = self.year + self.years
            if self.month is None:
                month = other.month + self.months
            else:
                month = self.month + self.months
            if self.day is None:
                day = other.day
            else:
                day = self.day
            if day < 0:
                # fix negative day values
                month = month + 1
                day = day + 1
            day = day + self.days
            # time
            if self.hour is None:
                hour = other.hour + self.hours
            else:
                hour = self.hour + self.hours
            if self.minute is None:
                minute = other.minute + self.minutes
            else:
                minute = self.minute + self.minutes
            if self.second is None:
                second = other.second + self.seconds
            else:
                second = self.second + self.seconds

            # Refit into proper ranges:
            if month < 1 or month > 12:
                month = month - 1
                yeardelta, monthdelta = divmod(month, 12)
                year = year + yeardelta
                month = monthdelta + 1

            # Make sure we have integers
            year = int(year)
            month = int(month)
            day = int(day)

            if self.weekday is None:
                return DateTime(year, month, 1) + \
                       DateTimeDelta(day-1,hour,minute,second)
            
            # Adjust to the correct weekday
            day_of_week,index = self.weekday
            d = DateTime(year, month, 1) + \
                DateTimeDelta(day-1,hour,minute,second)
            if index == 0:
                # 0 index: next weekday if no match
                return d + (day_of_week - d.day_of_week)
            elif index > 0:
                # positive index (1 == first weekday of month)
                first = d - (d.day - 1)
                diff = day_of_week - first.day_of_week
                if diff >= 0:
                    return first + (diff + (index-1) * 7)
                else:
                    return first + (diff + index * 7)
            else:
                # negative index (-1 == last weekday of month)
                last = d + (d.days_in_month - d.day)
                diff = day_of_week - last.day_of_week
                if diff <= 0:
                    return last + (diff + (index+1) * 7)
                else:
                    return last + (diff + index * 7)
            
        else:
            raise TypeError,"can't add the two types"

    def __sub__(self,other):

        if isinstance(other,RelativeDateTime):
            # RelativeDateTime (self) - RelativeDateTime (other)

            r = RelativeDateTime()
            # date deltas
            r.years = self.years - other.years
            r.months = self.months - other.months
            r.days = self.days - other.days
            # absolute entries of other override those in self, if given
            r.year = other.year or self.year
            r.month = other.month or self.month
            r.day = other.day or self.day
            r.weekday = other.weekday or self.weekday
            # time deltas
            r.hours = self.hours - other.hours
            r.minutes = self.minutes - other.minutes
            r.seconds = self.seconds - other.seconds
            # absolute entries of other override those in self, if given
            r.hour = other.hour or self.hour
            r.minute = other.minute or self.minute
            r.second = other.second or self.second

            return r

        else:
            raise TypeError,"can't subtract the two types"

    def __rsub__(self,other,
                 # Locals:
                 isinstance=isinstance,DateTimeType=DateTimeType):

        if isinstance(other,DateTimeType):
            # DateTime (other) - RelativeDateTime (self)
            return other + self.__neg__()

        else:
            raise TypeError,"can't subtract the two types"

    def __neg__(self):

        # - RelativeDateTime(self)

        r = RelativeDateTime()
        # negate date deltas
        r.years = - self.years
        r.months = - self.months
        r.days = - self.days
        # absolute entries don't change
        r.year = self.year
        r.month = self.month
        r.day = self.day
        r.weekday = self.weekday
        # negate time deltas
        r.hours = - self.hours
        r.minutes = - self.minutes
        r.seconds = - self.seconds
        # absolute entries don't change
        r.hour = self.hour
        r.minute = self.minute
        r.second = self.second

        return r

    def __nonzero__(self):

        # RelativeDateTime instances are considered false in case
        # they do not define any alterations
        if (self.year is None and
            self.years == 0 and
            self.month is None and
            self.months == 0 and
            self.day is None and
            self.weekday is None and
            self.days == 0 and
            self.hour is None and
            self.hours == 0 and
            self.minute is None and
            self.minutes == 0 and
            self.second is None and
            self.seconds == 0):
            return 0
        else:
            return 1

    def __mul__(self,other):

        # RelativeDateTime (self) * Number (other)
        factor = float(other)

        r = RelativeDateTime()
        # date deltas
        r.years = factor * self.years
        r.months = factor * self.months
        r.days = factor * self.days
        # time deltas
        r.hours = factor * self.hours
        r.minutes = factor * self.minutes
        r.seconds = factor * self.seconds
        return r

    __rmul__ = __mul__

    def __div__(self,other):

        # RelativeDateTime (self) / Number (other)
        return self.__mul__(1/float(other))

    def __eq__(self, other):

        if isinstance(self, RelativeDateTime) and \
           isinstance(other, RelativeDateTime):
            # RelativeDateTime (self) == RelativeDateTime (other)
            if (self.years == other.years and
                self.months == other.months and
                self.days == other.days and
                self.year == other.year and
                self.day == other.day and
                self.hours == other.hours and
                self.minutes == other.minutes and
                self.seconds == other.seconds and
                self.hour == other.hour and
                self.minute == other.minute and
                self.second == other.second and
                self.weekday == other.weekday):
                return 1
            else:
                return 0
        else:
            raise TypeError,"can't compare the two types"

    def __hash__(self):

        if self._hash is not None:
            return self._hash
        x = 1234
        for value in (self.years, self.months, self.days,
                      self.year, self.day,
                      self.hours, self.minutes, self.seconds,
                      self.hour, self.minute, self.second,
                      self.weekday):
            if value is None:
                x = 135051820 ^ x
            else:
                x = hash(value) ^ x
        self._hash = x
        return x

    def __str__(self,

                join=_string.join):

        l = []
        append = l.append

        # Format date part
        if self.year is not None:
            append('%04i-' % self.year)
        elif self.years:
            append('(%0+5i)-' % self.years)
        else:
            append('YYYY-')
        if self.month is not None:
            append('%02i-' % self.month)
        elif self.months:
            append('(%0+3i)-' % self.months)
        else:
            append('MM-')
        if self.day is not None:
            append('%02i' % self.day)
        elif self.days:
            append('(%0+3i)' % self.days)
        else:
            append('DD')
        if self.weekday:
            append(' %s:%i' % (Weekday[self.weekday[0]][:3],self.weekday[1]))
        append(' ')
        
        # Normalize relative time values to avoid fractions
        hours = self.hours
        minutes = self.minutes
        seconds = self.seconds
        hours_fraction = hours - int(hours)
        minutes = minutes + hours_fraction * 60.0
        minutes_fraction = minutes - int(minutes)
        seconds = seconds + minutes_fraction * 6.0
        seconds_fraction = seconds - int(seconds)

        if 0:
            # Normalize to standard time ranges
            if seconds > 60.0:
                extra_minutes, seconds = divmod(seconds, 60.0)
                minutes = minutes + extra_minutes
            elif seconds < -60.0:
                extra_minutes, seconds = divmod(seconds, -60.0)
                minutes = minutes - extra_minutes
            if minutes >= 60.0:
                extra_hours, minutes = divmod(minutes, 60.0)
                hours = hours + extra_hours
            elif minutes <= -60.0:
                extra_hours, minutes = divmod(minutes, -60.0)
                hours = hours - extra_hours

        # Format time part
        if self.hour is not None:
            append('%02i:' % self.hour)
        elif hours:
            append('(%0+3i):' % hours)
        else:
            append('HH:')
        if self.minute is not None:
            append('%02i:' % self.minute)
        elif minutes:
            append('(%0+3i):' % minutes)
        else:
            append('MM:')
        if self.second is not None:
            append('%02i' % self.second)
        elif seconds:
            append('(%0+3i)' % seconds)
        else:
            append('SS')
            
        return join(l,'')

    def __repr__(self):

        return "<%s instance for '%s' at 0x%x>" % ( 
            self.__class__.__name__, 
            self.__str__(), 
            id(self))

# Alias
RelativeDate = RelativeDateTime

def RelativeDateTimeFrom(*args, **kws):

    """ RelativeDateTimeFrom(*args, **kws)

        Generic RelativeDateTime instance constructor. Can handle
        parsing strings and keywords.

    """
    if len(args) == 1:
        # Single argument
        arg = args[0]
        if _isstring(arg):
            import Parser
            return apply(Parser.RelativeDateTimeFromString, args, kws)
        elif isinstance(arg, RelativeDateTime):
            return arg
        else:
            raise TypeError,\
                  'cannot convert argument to RelativeDateTime'

    else:
        return apply(RelativeDateTime,args,kws)

def RelativeDateTimeDiff(date1,date2,

                         floor=_math.floor,int=int,divmod=divmod,
                         RelativeDateTime=RelativeDateTime):

    """ RelativeDateTimeDiff(date1,date2)

        Returns a RelativeDateTime instance representing the difference
        between date1 and date2 in relative terms.

        The following should hold: 
        
        date2 + RelativeDateDiff(date1,date2) == date1 

        for all dates date1 and date2.

        Note that due to the algorithm used by this function, not the
        whole range of DateTime instances is supported; there could
        also be a loss of precision.

        XXX There are still some problems left (thanks to Carel
        Fellinger for pointing these out):

        29 1 1901 ->  1 3 1901 = 1 month
        29 1 1901 ->  1 3 1900 = -10 month and -28 days, but
        29 1 1901 -> 28 2 1900 = -11 month and -1 day

        and even worse:

        >>> print RelativeDateDiff(Date(1900,3,1),Date(1901,2,1))
        YYYY-(-11)-DD HH:MM:SS

        with:

        >>> print Date(1901,1,29) + RelativeDateTime(months=-11)
        1900-03-01 00:00:00.00
        >>> print Date(1901,2,1) + RelativeDateTime(months=-11)
        1900-03-01 00:00:00.00

    """
    diff = date1 - date2
    if diff.days == 0:
        return RelativeDateTime()
    date1months = date1.year * 12 + (date1.month - 1)
    date2months = date2.year * 12 + (date2.month - 1)
    #print 'months',date1months,date2months

    # Calculate the months difference
    diffmonths = date1months - date2months
    #print 'diffmonths',diffmonths
    if diff.days > 0:
        years,months = divmod(diffmonths,12)
    else:
        years,months = divmod(diffmonths,-12)
        years = -years
    date3 = date2 + RelativeDateTime(years=years,months=months)
    diff3 = date1 - date3
    days = date1.absdays - date3.absdays
    #print 'date3',date3,'diff3',diff3,'days',days

    # Correction to ensure that all relative parts have the same sign
    while days * diff.days < 0:
        if diff.days > 0:
            diffmonths = diffmonths - 1
            years,months = divmod(diffmonths,12)
        else:
            diffmonths = diffmonths + 1
            years,months = divmod(diffmonths,-12)
            years = -years
        #print 'diffmonths',diffmonths
        date3 = date2 + RelativeDateTime(years=years,months=months)
        diff3 = date1 - date3
        days = date1.absdays - date3.absdays
        #print 'date3',date3,'diff3',diff3,'days',days

    # Drop the fraction part of days
    if days > 0:
        days = int(floor(days))
    else:
        days = int(-floor(-days))

    return RelativeDateTime(years=years,
                            months=months,
                            days=days,
                            hours=diff3.hour,
                            minutes=diff3.minute,
                            seconds=diff3.second)

# Aliases
RelativeDateDiff = RelativeDateTimeDiff
Age = RelativeDateTimeDiff

###

_current_year = now().year
_current_century, _current_year_in_century = divmod(_current_year, 100)
_current_century = _current_century * 100

def add_century(year,

                current_year=_current_year,
                current_century=_current_century):
    
    """ Sliding window approach to the Y2K problem: adds a suitable
        century to the given year and returns it as integer.

        The window used depends on the current year (at import time).
        If adding the current century to the given year gives a year
        within the range current_year-70...current_year+30 [both
        inclusive], then the current century is added. Otherwise the
        century (current + 1 or - 1) producing the smallest difference is
        chosen.

    """
    if year > 99:
        # Take it as-is
        return year
    year = year + current_century
    diff = year - current_year
    if diff >= -70 and diff <= 30:
        return year
    elif diff < -70:
        return year + 100
    else:
        return year - 100

# Reference formulas for JDN taken from the Calendar FAQ:

def gregorian_jdn(year,month,day):

    # XXX These require proper integer division.
    a = (14-month)/12
    y = year+4800-a
    m = month + 12*a - 3
    return day + (306*m+5)/10 + y*365 + y/4 - y/100 + y/400 - 32045

def julian_jdn(year,month,day):

    # XXX These require proper integer division.
    a = (14-month)/12
    y = year+4800-a
    m = month + 12*a - 3
    return day + (306*m+5)/10 + y*365 + y/4 - 32083
