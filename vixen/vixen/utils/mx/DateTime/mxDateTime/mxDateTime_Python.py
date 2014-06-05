"""
    Python implementation courtesy of Drew Csillag (StarMedia Network, Inc.)

    This version has been somewhat modified by MAL. It is still fairly
    rough though and not necessarily high performance... 

    XXX Still needs testing and checkup !!!

    WARNING: Using this file is only recommended if you really must
    use it for some reason. It is not being actively maintained !

"""

__version__ = '1.2.0 [Python]'

import time,types,exceptions,math

### Errors

class Error(exceptions.StandardError):
    pass

class RangeError(Error):
    pass

### Constants (internal use only)

month_offset=(
    (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365),
    (0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366),
    )

days_in_month=(
    (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31),
    )

### Helpers

def _IS_LEAPYEAR(d):
    return ((d.year % 4 == 0)
            and (
                (d.year % 100 != 0)
                or (d.year % 400 == 0)
                )
            )

def _YEAROFFSET(d):
    return (
        (d.year - 1) * 365
        + (d.year - 1) / 4
        - (d.year - 1) / 100
        + (d.year - 1) / 400
        )

class _EmptyClass:
    pass

def createEmptyObject(Class,
                      _EmptyClass=_EmptyClass):

    o = _EmptyClass()
    o.__class__ = Class
    return o

### DateTime class

class DateTime:

    def __init__(self, year, month=1, day=1, hour=0, minute=0, second=0.0):

        second=1.0 * second
        if month <= 0:
            raise RangeError, "year out of range (>0)"

        #calculate absolute date
        leap = (year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))

        #Negative values indicate days relative to the years end
        if month < 0:
            month = month + 13 

        if not (month >= 1 and month <= 12):
            raise RangeError, "month out of range (1-12)"

        #Negative values indicate days relative to the months end
        if (day < 0):
            day = day + days_in_month[leap][month - 1] + 1;

        if not (day >= 1 and day <= days_in_month[leap][month - 1]):
            raise RangeError, "day out of range"

        year = year - 1
        yearoffset = year * 365 + year / 4 - year / 100 + year / 400
        year = year + 1
        absdate = day + month_offset[leap][month - 1] + yearoffset;

        self.absdate = absdate
        self.year = year
        self.month = month
        self.day = day
        self.day_of_week = (absdate - 1) % 7
        self.day_of_year = absdate - yearoffset
        self.days_in_month = days_in_month[leap][month - 1]
        comdate = absdate - 693594

        if not (hour >=0 and hour <= 23):
            raise RangeError, "hour out of range (0-23)"
        if not (minute >= 0 and minute <= 59):
            raise RangeError, "minute out of range (0-59)"
        if not (second >= 0.0 and
                (second < 60.0 or 
                 (hour == 23 and minute == 59 and second < 61.0))):
            raise RangeError, "second out of range (0.0 - <60.0; <61.0 for 23:59)"

        self.abstime = (hour * 3600 + minute * 60) + second
        self.hour = hour
        self.minute = minute
        self.second = second
        self.dst = -1
        self.tz = "???"
        self.is_leapyear = leap
        self.yearoffset = yearoffset

        if comdate < 0.0:
            comdate = comdate - self.abstime / 86400.0
        else:
            comdate = comdate + self.abstime / 86400.0

        self.comdate = comdate

    def COMDate(self):
        return self.comdate
    
    def __str__(self):
        return "%04d-%02d-%02d %02d:%02d:%05.2f" % (
            self.year, self.month, self.day, self.hour, self.minute,
            self.second)
    
    def __getattr__(self, attr):
        if attr == 'mjd':
            return (self - mjd0).days
        elif attr == 'jdn':
            return (self - jdn0).days
        elif attr == 'tjd':
            return (self - jdn0).days % 10000
        elif attr == 'tjd_myriad':
            return int((self - jdn0).days) / 10000 + 240
        elif attr == 'absdays':
            return self.absdate - 1 + self.abstime / 86400.0
        else:
            try:
                return self.__dict__[attr]
            except:
                raise AttributeError, attr

    def __mul__(self, other):
        raise TypeError, "bad operand type(s) for *"

    def __div__(self, other):
        raise TypeError, "bad operand type(s) for /"
    
    def strftime(self, format_string="%c"):
        return time.strftime(format_string, self.tuple())

    # Alias
    Format = strftime
    
    def tuple(self):
        return (self.year, self.month, self.day, self.hour, self.minute, self.second, self.day_of_week, 0, -1)
        #return time.localtime(self.ticks())

    def absvalues(self):
        return self.absdate, self.abstime
    
    def __float__(self):
        return self.ticks()

    def __int__(self):
        return int(self.ticks)
    
    def ticks(self, offset=0.0, dst=-1):
        tticks=time.mktime(self.year, self.month, self.day, self.hour,
                           self.minute, self.second, self.day_of_week, 0, dst)
        if tticks == -1:
            raise OverflowError, "cannot convert value to a time value"
        ticks = (1.0*tticks) + (self.abstime - int(self.abstime)) - offset
        return ticks

    def gmticks(self, offset=0.0):
        from mx.DateTime import tz_offset
        return (self-tz_offset(self)).ticks()
    
    def __repr__(self):
        return "<DateTime object for '%d-%02d-%02d %02d:%02d:%05.2f' at %x>"% (
            self.year, self.month, self.day, self.hour, self.minute,
            self.second, id(self))

    def __cmp__(self, other,
                cmp=cmp):

        if isinstance(other,DateTime):
            cmpdate = cmp(self.absdate,other.absdate)
            if cmpdate == 0:
                return cmp(self.abstime,other.abstime)
            else:
                return cmpdate
        elif type(other) == types.NoneType:
            return -1
        elif type(other) == types.StringType:
            return -1
        elif type(other) in (types.FloatType, types.LongType, types.IntType):
            return 1
        return -1
        
    def __add__(self, other):
        abstime=self.abstime
        absdate=self.absdate

        didadd=0
        
        if type(other) == types.InstanceType:
            if other.__class__ == DateTimeDelta:
                abstime = abstime + other.seconds
                didadd=1
            elif other.__class__ == DateTime:
                raise TypeError, "DateTime + DateTime is not supported"
            else:
                return other.__class__.__radd__(other, self)
            
        elif type(other) == types.IntType or type(other) == types.FloatType:
            abstime = abstime + other * 86400.0
            didadd=1

        if not didadd:
            raise TypeError, "cannot add these two types"

        if abstime >= 86400.0:
            days = abstime / 86400.0
            absdate = absdate + days
            abstime = abstime - (86400.0 * int(days))
            #print "absdate, abstime = ", absdate, abstime
        elif abstime < 0.0:
            days = int(((-abstime - 1) / 86400.0)) + 1
            #days = int(-abstime / 86400.0)
            absdate = absdate - days
            abstime = abstime + 86400.0 * int(days)

        if absdate < 1:
            raise RangeError, "underflow while adding"

        return DateTimeFromAbsDateTime(absdate, abstime)

    def __radd__(self, other):
        return DateTime.__add__(other, self)
    
    def __sub__(self, other):
        abstime=self.abstime
        absdate=self.absdate

        didsub=0
        if type(other) == types.InstanceType:
            if other.__class__ == DateTimeDelta:
                abstime = abstime - other.seconds
                didsub = 1
            elif other.__class__ == DateTime:
                absdate = absdate - other.absdate
                abstime = abstime - other.abstime
                return DateTimeDelta(absdate,0.0,0.0,abstime)

        elif type(other) == types.IntType or type(other) == types.FloatType:
            abstime = abstime - other * 86400.0;
            didsub=1

        if not didsub:
            raise TypeError, "cannot subtract these two types"

        if abstime >= 86400.0:
            days = abstime / 86400.0
            absdate = absdate + days
            abstime = abstime - (86400.0 * days)
            #print "absdate, abstime = ", absdate, abstime
        elif abstime < 0.0:
            #print "abstime < 0"
            days = int( ((-abstime - 1) / 86400.0) + 1)
            #days = -abstime / 86400.0
            absdate = absdate - int(days)
            abstime = (1.0*abstime) + (86400.0 * days)
            #print "absdate, abstime", absdate, abstime
        if absdate < 1:
            raise RangeError, "underflow while adding"

        return DateTimeFromAbsDateTime(absdate, abstime)

# Constants
mjd0 = DateTime(1858, 11, 17)
jdn0 = DateTime(-4713, 1, 1, 12, 0, 0.0)

# Other DateTime constructors

def DateTimeFromCOMDate(comdate):

    absdate = int(comdate)
    abstime = (comdate - float(absdate)) * 86400.0
    if abstime < 0.0:
        abstime = -abstime
    absdate = absdate + 693594;
    dt = DateTimeFromAbsDateTime(absdate, abstime)
    dt.comdate = comdate
    return dt
    
def DateTimeFromAbsDateTime(absdate, abstime):

    # Create the object without calling its default constructor
    dt = createEmptyObject(DateTime)

    # Init. the object
    abstime=1.0 * abstime
    if abstime < 0 and abstime > -0.001: abstime = 0.0
    if not (absdate > 0):
        raise RangeError, "absdate out of range (>0)"
    if not (abstime >= 0.0 and abstime <= 86400.0):
        raise RangeError, "abstime out of range (0.0 - 86400.0) <%s>" % abstime

    dt.absdate=absdate
    dt.abstime=abstime

    #calculate com date
    comdate = 1.0 * (dt.absdate - 693594)
    if comdate < 0.0:
        comdate = comdate - dt.abstime / 86400.0
    else:
        comdate = comdate + dt.abstime / 86400.0
    dt.comdate = comdate

    #calculate the date
    #print "absdate=", absdate
    year = int((1.0 * absdate) / 365.2425)

    #newApproximation:
    while 1:
        #print "year=", year
        yearoffset = year * 365 + year / 4 - year / 100 + year / 400
        #print "yearoffset=", yearoffset
        #print "absdate=", absdate
        if yearoffset >= absdate:
            year = year - 1
            #print "year = ", year
            continue #goto newApproximation

        year = year + 1
        leap = (year % 4 == 0) and ((year % 100 != 0) or (year % 400 == 0))
        dayoffset = absdate - yearoffset
        #print "dayoffset=", dayoffset
        if dayoffset > 365 and leap == 0:
            #print "dayoffset=", dayoffset
            continue #goto newApproximation

        monthoffset = month_offset[leap]
        for month in range(1, 13):
            if monthoffset[month] >= dayoffset:
                break
        dt.year = year
        dt.month = month
        dt.day = dayoffset - month_offset[leap][month-1]
        dt.day_of_week = (dt.absdate - 1) % 7
        dt.day_of_year = dayoffset
        break
    
    #calculate the time
    inttime = int(abstime)
    hour = inttime / 3600
    minute = (inttime % 3600) / 60
    second = abstime - 1.0 * (hour*3600 + minute*60)
    dt.hour = hour;
    dt.minute = minute;
    dt.second = second;
    dt.days_in_month = days_in_month[leap][month - 1]
    dt.dst = -1
    dt.tz = "???"
    dt.is_leapyear = leap
    dt.yearoffset = yearoffset
    return dt

def now(
        time=time.time,float=float,localtime=time.localtime,
        round=round,int=int,DateTime=DateTime,floor=math.floor):

    ticks = time()
    Y,M,D,h,m,s = localtime(ticks)[:6]
    s = s + (ticks - floor(ticks))
    return DateTime(Y,M,D,h,m,s)

def utc(
        time=time.time,float=float,gmtime=time.gmtime,
        round=round,int=int,DateTime=DateTime,floor=math.floor):

    ticks = time()
    Y,M,D,h,m,s = gmtime(ticks)[:6]
    s = s + (ticks - floor(ticks))
    return DateTime(Y,M,D,h,m,s)

# Aliases
Date = Timestamp = DateTime

# XXX Calendars are not supported:
def notSupported(*args,**kws):
    raise Error,'calendars are not supported by the Python version of mxDateTime'
JulianDateTime = notSupported

### DateTimeDelta class
               
class DateTimeDelta:

    def __init__(self, days=0, hours=0, minutes=0, seconds=0):

        seconds = seconds + (days * 86400.0 + hours * 3600.0 + minutes * 60.0)
        self.seconds = seconds
        if seconds < 0.0:
            seconds = -seconds
        day = long(seconds / 86400.0)
        seconds = seconds - (86400.0 * day)
        wholeseconds = int(seconds)
        hour = wholeseconds / 3600
        minute = (wholeseconds % 3600) / 60
        second = seconds - (hour * 3600.0 + minute * 60.0)
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        seconds=self.seconds
        self.minutes = seconds / 60.0
        self.hours = seconds / 3600.0
        self.days = seconds / 86400.0

    def __str__(self):
        if self.day != 0:
            if self.seconds >= 0.0:
                r="%s:%02d:%02d:%05.2f" % (
                    self.day, self.hour, self.minute, self.second)
            else:
                r="-%s:%02d:%02d:%05.2f" % (
                    self.day, self.hour, self.minute, self.second)
        else:
            if self.seconds >= 0.0:
                r="%02d:%02d:%05.2f" % (self.hour, self.minute, self.second)
            else:
                r="-%02d:%02d:%05.2f" % (self.hour, self.minute, self.second)
        return r
            
    def absvalues(self):
        days=self.seconds / 86400
        seconds=self.seconds - (days * 86400.0)
        return days, seconds

    def tuple(self):
        return (self.day, self.hour, self.minute, self.second)

    def strftime(self, format_string):
        raise NotImplementedError
    
    def __int__(self):
        return int(self.seconds)

    def __float__(self):
        return self.seconds
    
    def __cmp__(self, other, accuracy=0.0):
        if (type(other) == types.InstanceType
            and other.__class__ == DateTimeDelta):

            diff=self.seconds - other.seconds
            if abs(diff) > accuracy:
                if diff > 0: return 1
                return -1
            
        elif type(other) == types.FloatType:
            diff=self.seconds - other
            if abs(diff) > accuracy:
                if diff > 0: return 1
                return -1
            
        elif type(other) == types.IntType:
            diff=self.seconds - other
            if abs(diff) > accuracy:
                if diff > 0: return 1
                return -1
            
        return 0
    
    def __getattr__(self, attr):
        seconds=self.__dict__['seconds']
        if attr in ('hour', 'minute', 'second', 'day'):
            if seconds >= 0.0:
                return self.__dict__[attr]
            else:
                return -self.__dict__[attr]
        else:
            try:
                return self.__dict__[attr]
            except:
                raise AttributeError, attr

    def __div__(self, other):
        if type(other) in (types.IntType, types.FloatType):
            return DateTimeDelta(0.0,0.0,0.0,self.seconds / other)
        elif (type(other) == types.InstanceType
              and isinstance(other,DateTimeDelta)):
            return DateTimeDelta(0.0,0.0,0.0,self.seconds / other.seconds)
        raise TypeError, "bad operand types for /"
    
    def __mul__(self, other):
        if type(other) == types.IntType or type(other) == types.FloatType:
            return DateTimeDelta(0.0,0.0,0.0,self.seconds * other)
        else:
            #print "type", type(other)
            raise TypeError, "cannot multiply these two types"

    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __neg__(self):
        return DateTimeDelta(0.0,0.0,0.0,-self.seconds)
        
    def __repr__(self):
        if self.day != 0:
            if self.seconds >= 0.0:
                strval="%s:%02d:%02d:%05.2f" % (self.day, self.hour,
                                                 self.minute, self.second)
            else:
                strval="-%s:%02d:%02d:%05.2f" % (self.day, self.hour,
                                                  self.minute, self.second)
        else:
            if self.seconds >= 0.0:
                strval="%02d:%02d:%05.2f" % (self.hour, self.minute,
                                            self.second)
            else:
                strval="-%02d:%02d:%05.2f" % (self.hour, self.minute,
                                             self.second)
        return "<DateTimeDelta object for '%s' at %x>" % (strval, id(self))
    
    def __abs__(self):
        if self.seconds < 0:
            return -self
        return self

    def __nonzero__(self):
        return self.seconds != 0.0
    
    def __add__(self, other):
        if type(other) == types.InstanceType:
            if isinstance(other,DateTime):
                return other + self
            elif isinstance(other,DateTimeDelta):
                return DateTimeDelta(0.0,0.0,0.0,self.seconds + other.seconds)

    # What about __radd__ ?
        
# Other DateTimeDelta constructors

def TimeDelta(hour=0.0, minute=0.0, second=0.0):
    return DateTimeDelta(0.0, hours, minutes, seconds)

Time=TimeDelta

def DateTimeDeltaFromSeconds(seconds):
    return DateTimeDelta(0.0,0.0,0.0,seconds)

def DateTimeDeltaFromDays(days):
    return DateTimeDelta(days)

### Types

DateTimeType = DateTime
DateTimeDeltaType = DateTimeDelta

### Functions

def cmp(a,b,acc):

    if isinstance(a,DateTime) and isinstance(b,DateTime):
        diff = a.absdays - b.absdays
        if (diff >= 0 and diff <= acc) or (diff < 0 and -diff <= acc):
            return 0
        elif diff < 0:
            return 1
        else:
            return -1

    elif isinstance(a,DateTimeDelta) and isinstance(b,DateTimeDelta):
        diff = a.days - b.days
        if (diff >= 0 and diff <= acc) or (diff < 0 and -diff <= acc):
            return 0
        elif diff < 0:
            return 1
        else:
            return -1

    else:
        raise TypeError,"objects must be DateTime[Delta] instances"
