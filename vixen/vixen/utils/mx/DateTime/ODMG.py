""" ODMG type classes for date/time handling

    These are built on top of the basic DateTime[Delta] types and
    include rudimentary time zone handling through an offset in
    minutes. It is the applications responsibility to set the offset
    to correct values. The offsets are then used in date calculations.

    The implementation has not yet been thoroughly tested, but
    provides a good example of the swiftness with which you can build
    new date/time classes on top of the two basic types. If you find
    any errors or would like to see new features, mail them to
    mal@lemburg.com.

"""
__version__ = '0.1alpha'
__author__ = 'Marc-Andre Lemburg, mailto:mal@lemburg.com'

import DateTime

class _EmptyClass: pass

class Date:

    offset = 0                  # from some imaginary time zone in minutes

    def __init__(self,*args):

        self.data = apply(DateTime.DateTime,args)

    def set_timezone(self,offset):

        self.offset = offset

    def __getattr__(self,what):

        return getattr(self.data,what)

    def __sub__(self,other):

        if isinstance(other,Date):
            if self.offset != other.offset:
                # Be careful about different offsets:
                d = (self.data - self.offset * DateTime.oneMinute) \
                    - (other.data - other.offset * DateTime.oneMinute)
            else:
                # Offsets are equal: no adjustment needed
                d = self.data - other.data
            o = _EmptyClass()
            o.__class__ = Interval
            o.data = d
            return o
        elif isinstance(other,Interval):
            d = self.data - other.data
            o = _EmptyClass()
            o.__class__ = Date
            o.data = d
            o.offset = self.offset # inherit the offset
            return o
        else:
            raise TypeError,"operation not supported"

    def __add__(self,other):

        if isinstance(other,Interval):
            d = self.data + other.data
            o = _EmptyClass()
            o.__class__ = Date
            o.data = d
            o.offset = self.offset # inherit the offset
            return o
        else:
            raise TypeError,"operation not supported"

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return '<Date object for "%s" at %x>' % (str(self.data),id(self))

class Timestamp(Date):

    def __repr__(self):
        return '<Timestamp object for "%s" at %x>' % (str(self.data),id(self))

class Time:

    def __init__(self,*args):

        self.data = apply(DateTime.TimeDelta,args)

    def __getattr__(self,what):

        return getattr(self.data,what)

    def __sub__(self,other):

        if isinstance(other,Time):
            d = self.data - other.data
            o = _EmptyClass()
            o.__class__ = Interval
            o.data = d
            return o
        elif isinstance(other,Interval):
            d = self.data - other.data
            o = _EmptyClass()
            o.__class__ = Time
            o.data = d
            return o
        else:
            raise TypeError,"operation not supported"

    def __add__(self,other):

        if isinstance(other,Time):
            d = self.data + other.data
            o = _EmptyClass()
            o.__class__ = Interval
            o.data = d
            return o
        elif isinstance(other,Interval):
            d = self.data + other.data
            o = _EmptyClass()
            o.__class__ = Time
            o.data = d
            return o
        else:
            raise TypeError,"operation not supported"

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return '<Time object for "%s" at %x>' % (str(self.data),id(self))

class Interval:

    def __init__(self,*args):

        self.data = apply(DateTime.DateTimeDelta,args)

    def __getattr__(self,what):

        return getattr(self.data,what)

    def __sub__(self,other):

        if isinstance(other,Interval):
            d = self.data - other.data
            o = _EmptyClass()
            o.__class__ = Interval
            o.data = d
            return o
        else:
            raise TypeError,"operation not supported"

    def __add__(self,other):

        if isinstance(other,Interval):
            d = self.data + other.data
            o = _EmptyClass()
            o.__class__ = Interval
            o.data = d
            return o
        else:
            raise TypeError,"operation not supported"

    def __mul__(self,other):

        value = float(other)
        d = value * self.data
        o = _EmptyClass()
        o.__class__ = Interval
        o.data = d
        return o
    __rmul__ = __mul__

    def __div__(self,other):

        value = float(other)
        d = self.data / value
        o = _EmptyClass()
        o.__class__ = Interval
        o.data = d
        return o

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return '<Interval object for "%s" at %x>' % (str(self.data),id(self))

if __name__ == '__main__':
    # Some test instances to play around with
    d = Date(1998,3,2)
    e = Date(1998,1,2)
    f = Date(1998,1,2)
    f.set_timezone(60)
    t = Time(12,0,0)
    u = Time(13,0,0)
