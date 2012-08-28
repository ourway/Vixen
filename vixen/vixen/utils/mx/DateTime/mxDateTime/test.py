#! /usr/bin/python -u
            
from mx.DateTime import *
from mx.DateTime import __version__
import time,sys,traceback

print 'Testing mxDateTime version',__version__
print

if not __debug__:
    print '*** You have to run the test suite in non-optimized mode !'
    print
    sys.exit(1)

### Constructors

## DateTime()

d = DateTime(2008,1,2, 12,13,14)
assert d.year == 2008
assert d.month == 1
assert d.day == 2
assert d.hour == 12
assert d.minute == 13
assert d.second == 14
assert d.absdate == 733043
assert d.abstime == 43994.0
assert long(d.absdays*1000) == 733042509L

# Normalization
assert DateTime(2008,1,-1).day == 31
assert DateTime(2008,1,-31).day == 1
assert DateTime(2008,-1,1).month == 12
assert DateTime(2008,-12,1).month == 1
assert DateTime(-1,1,1).year == -1

## Test DateTimeFromAbsDateTime()

# wintertime
t = winter = DateTimeFromAbsDateTime(729368,55931.522913)
print t
print repr(t)
assert str(t) == '1997-12-10 15:32:11.52'

x = float(t)
print 'as ticks:',x
print 'time.gmtime:',time.gmtime(x),'(note the seconds)'
print 'time.localtime:',time.localtime(x)
print 'tuple:',t.tuple()

print

# summertime
t = summer = DateTimeFromAbsDateTime(729200,55931.522913)
print t
print repr(t)
assert str(t) == '1997-06-25 15:32:11.52'

x = float(t)
print 'as ticks:',x
print 'time.gmtime:',time.gmtime(x),'(note the seconds)'
print 'time.localtime:',time.localtime(x)
print 'tuple:',t.tuple()

print

## Test Timestamp()
t = Timestamp(1900,1,1,12,23,34.5)
print t
assert t.tuple()[:6] == (1900,1,1,12,23,34)
assert str(t) == '1900-01-01 12:23:34.50'

## Test DateTimeFromCOMDate()
t = DateTimeFromCOMDate(12345.6)
print t
assert t.COMDate() == 12345.6
assert str(t) == '1933-10-18 14:24:00.00'

t = DateTimeFromCOMDate(-12345.6)
print t
assert t.COMDate() == -12345.6
assert str(t) == '1866-03-13 14:24:00.00'

## Test DateTimeFromTicks()
x = time.time()
print 'ticks:',x,'localtime:',time.localtime(x)
t = DateTimeFromTicks(x)
print t.tuple(), t.absdate, t.abstime
assert t.ticks() == x
print

## Test Date()
t = Date(2007,1,1)
#print t
assert str(t) == '2007-01-01 00:00:00.00'
assert t.absdate == 732677
assert t.date == '2007-01-01'
assert t.time == '00:00:00.00'

# Negative days count from the month's end
t = Date(2007,1,-1)
#print t
assert str(t) == '2007-01-31 00:00:00.00'
assert t.absdate == 732707
assert t.date == '2007-01-31'
assert t.time == '00:00:00.00'
t = Date(2007,2,-1)
#print t
assert t.absdate == 732735
assert t.date == '2007-02-28'
assert t.time == '00:00:00.00'

print 'Basic constructors ok.'

### String format
t = DateTime(-1,1,1,12,34,56.78)
assert str(t) == '-0001-01-01 12:34:56.78'
t = DateTime(2007,1,1,12,34,56.78)
assert str(t) == '2007-01-01 12:34:56.78'
print 'String format ok.'

### Python Number protocol:
t1 = Date(1997,12,31)
t2 = Date(1997,12,30)
d = t2 - t1
try:
    t1 + t2
except TypeError:
    pass
try:
    t2 * t1
except TypeError:
    pass
try:
    t2 / t1
except TypeError:
    pass
print 'Number protocol ok.'

### Deltas
assert DateTimeDelta(2,1,-1,-3).tuple() == (2, 0, 58, 57.0)
assert DateTimeDelta(2,0,-1,-3).tuple() == (1, 23, 58, 57.0)
assert DateTime(1998,1,9) + DateTimeDelta(-1) == DateTime(1998,1,8)
assert DateTime(1998,1,9) - DateTimeDelta(1) == DateTime(1998,1,8)
assert DateTime(1998,1,9) - DateTimeDelta(1.5) == DateTime(1998,1,7,12,0,0)
assert DateTime(1998,1,9) - DateTime(1969,4,6) == DateTimeDelta(10505)
assert DateTimeDelta(10000) / (DateTimeDelta(10000) * 0.5) == 2.0
assert DateTime(2000,12,31) + DateTimeDelta(1) == DateTime(2001, 1, 1)
assert DateTime(2000,12,31) + DateTimeDelta(2) == DateTime(2001, 1, 2)
assert DateTime(2000,12,31) + 1 == DateTime(2001, 1, 1)
assert DateTime(2000,12,31) + 2 == DateTime(2001, 1, 2)
a = Date(2000,11,9)
b = Date(2000,11,10)
assert (b-a).seconds == 86400.0
assert (b-a).day == 1
assert (b-a).hour == 0
assert (b-a).second == 0
print 'Deltas ok.'
print

### UTC vs. local time
t = DateTime(2000,11,17)
print 'UTC -> local time -> UTC'
for i in range(24*365):
    x = t + 0.041666*i

    try:
        try:
            assert cmp(x.gmtime().localtime(), x, 0.001) == 0
        except AssertionError:
            print '    Problem (local time) -- DST switching time ?:'
            print '    %s -> %s -> %s' % \
                  (x, x.gmtime(), x.gmtime().localtime())

        try:
            assert cmp(x.localtime().gmtime(), x, 0.001) == 0
        except AssertionError:
            print '    Problem (gmt time) -- DST switching time ?:'
            print '    %s -> %s -> %s' % \
                  (x, x.localtime(), x.localtime().gmtime())

    except Error, why:
        print '*** Problem: %s' % x
        
print 'ok.'

### Rounding problems with COM dates
t = DateTime(1998, 2, 24, 12, 40, 11)
c = DateTimeFromCOMDate(t.COMDate())
print 'DateTime->COM Date->DateTime rounding error:',(t == c) * 'no' or 'yes'
print 'COM Dates compare:',(t.COMDate()==c.COMDate()) * 'equal' or 'not equal'
print 'diff =',t-c,'in seconds:',t.second - c.second
print 'using cmp(,,0.5):',(cmp(t,c,0.5) == 0) * 'equal' or 'not equal'
print

# Sanity check

def testjdn(year,month,day):

    # Reference taken from the Calendar FAQ (see docs for reference)

    a = (14-month)/12
    y = year+4800-a
    m = month + 12*a - 3
    
    # Gregorian
    gJDN = day + (306*m+5)/10 + y*365 + y/4 - y/100 + y/400 - 32045
    # Julian
    jJDN = day + (306*m+5)/10 + y*365 + y/4 - 32083
    
    return gJDN,jJDN

print 'Running constructor test... (this can take up to a few minutes)'
try:
    if __version__ >= '1.3.0':
        # New versions:
        for suite in (range(-100,100),range(1900,2101)):
            p = None
            for year in suite:
                print year,; sys.stdout.flush()
                for month in range(1,13):
                    for day in range(1,32):
                        try:
                            t = DateTime(year,month,day,12)
                            jt = JulianDateTime(year,month,day,12)
                            ref_greg,ref_jul = testjdn(year,month,day)
                        except RangeError:
                            continue
                        if p:
                            try:
                                assert p + 1 == t
                                assert (p+1).tuple() == t.tuple()
                                assert t.tuple()[:3] == (year,month,day)
                                assert DateTimeFromAbsDateTime(t.absdate).tuple()[:3] \
                                       == (year,month,day)
                                assert t.jdn == ref_greg
                                assert jt.jdn == ref_jul
                            except AssertionError:
                                print '*** Test failed for:'
                                print '  p = %s, p+1 = %s and' % (p,p+1)
                                print '  t = %s, jdn=%i; jdn reference = %i' % \
                                      (t,t.jdn,ref_greg)
                                print '  jt = %s, jdn=%i; jdn reference = %i' % \
                                      (jt,jt.jdn,ref_jul)
                                print
                                traceback.print_exc()
                                print
                                sys.exit(1)
                        p = t
            print
    else:
        # Old versions and experimental Python version:
        for suite in (range(1900,2101),):
            p = None
            for year in suite:
                print year,; sys.stdout.flush()
                for month in range(1,13):
                    for day in range(1,32):
                        try:
                            t = DateTime(year,month,day,12)
                            ref_greg,ref_jul = testjdn(year,month,day)
                        except RangeError:
                            continue
                        if p:
                            try:
                                assert p + 1 == t
                                assert (p+1).tuple() == t.tuple()
                                assert t.tuple()[:3] == (year,month,day)
                                assert DateTimeFromAbsDateTime(t.absdate).tuple()[:3] \
                                       == (year,month,day)
                                assert t.jdn == ref_greg
                            except AssertionError:
                                print '*** Test failed for:'
                                print '  p = %s, p+1 = %s and' % (p,p+1)
                                print '  t = %s, jdn=%i; jdn reference = %i' % \
                                      (t,t.jdn,ref_greg)
                                print
                                traceback.print_exc()
                                print
                                sys.exit(1)
                        p = t
            print
except KeyboardInterrupt:
    print
    print 'Interrupted.'
else:
    print 'Date construction works.'
    print

# Non zero testing
if t:
    print 'Non zero testing works.'

# ticks and dst
print 'Converting ticks and DST handling.'
try:
    summer.ticks(0,0)
    winter.ticks(0,0)
    summer.ticks(0,1)
    winter.ticks(0,1)
except SystemError:
    print
    print '-'*72
    print 'WARNING:'
    print
    print 'The mktime() C API on your platform does not support'
    print 'setting the DST flag to anything other than -1. This'
    print 'will cause the datetime.ticks() method to raise an'
    print 'error in case you pass a DST flag other than -1.'
    print '-'*72

# Sanity checks
date1 = Date(2000,11,1) + \
        RelativeDateTime(day=1,month=1,hour=0,minute=0,second=0)
date2 = Date(2000,11,1) + \
        RelativeDateTime(day=1,month=6,hour=0,minute=0,second=0)

print '%.15f == %.15f ?' % (date1.ticks(), time.mktime(date1.tuple()))
print '%.15f == %.15f ?' % (date2.ticks(), time.mktime(date2.tuple()))

try:
    assert date1.ticks() == time.mktime(date1.tuple())
    assert date2.ticks() == time.mktime(date2.tuple())
except AssertionError:
    print
    print '-'*72
    print 'WARNING:'
    print
    print 'Conversion from mx.DateTime instances to ticks is not relyable'
    print 'on your platform. Please run "python testticks.py" and send'
    print 'the output to the author at mal@lemburg.com.'
    print
    print '-'*72

print '%s == %s ?' % \
      (time.localtime(time.mktime(date1.tuple()))[:6], 
      date1.tuple()[:6])
print '%s == %s ?' % \
      (time.localtime(time.mktime(date2.tuple()))[:6], 
      date2.tuple()[:6])

try:
    assert time.localtime(time.mktime(date1.tuple()))[:6] == \
           date1.tuple()[:6]
    assert time.localtime(time.mktime(date2.tuple()))[:6] == \
           date2.tuple()[:6]
except AssertionError:
    print
    print '-'*72
    print 'WARNING:'
    print
    print 'time.localtime() and time.mktime() are not inverse functions'
    print 'on your platform. This may lead to strange results in some'
    print 'applications. Please run "python testticks.py" and send'
    print 'the output to the author at mal@lemburg.com.'
    print
    print '-'*72

print

# RelativeDateTime
print 'RelativeDateTime...',
assert hash(RelativeDateTime(year=2002)) == 135051564
assert hash(RelativeDateTime(year=2001)) == 135051567
assert hash(RelativeDateTime(year=2004)) == 135051562
assert RelativeDateTime(year=2004) == RelativeDateTime(year=2004)
assert RelativeDateTime(year=2004) != RelativeDateTime(year=2002)
assert str(RelativeDateTime(minutes=75)) == 'YYYY-MM-DD HH:(+75):SS'
assert str(RelativeDateTime(minutes=-75)) == 'YYYY-MM-DD HH:(-75):SS'
assert str(RelativeDateTime(hours=0.5)) == 'YYYY-MM-DD (+00):(+30):SS'
assert str(RelativeDateTime(hours=-0.5)) == 'YYYY-MM-DD (+00):(-30):SS'
print 'done.'

# timegm() emulation
print
print 'Testing .gmticks()... (this can take up to a few minutes)'
t = start = 920710000
stop = 2140240000
oops = 0
try:
    while 1:
        if t % 10000 < 20:
            print t,
        d = apply(DateTime,time.gmtime(t)[:6])
        try:
            x = d.gmticks()
        except Error:
            break
        if x != t:
            print ' Ooops:',d,'t =',t,'diff =',x-t
            oops = oops + 1
        try:
            t = t + 10011
        except OverflowError:
            break
        else:
            if t > stop:
                break
except KeyboardInterrupt:
    print
    print 'Interrupted.'
else:
    print
print ' Tested ticks range %i to %i.' % (start,t)
assert oops == 0
print '...Works.'
print

# Try importing a subpackage
print 'Importing subpackage Feasts.'
print
from mx.DateTime import Feasts
try:
    Feasts._test()
except SystemError:
    print '-'*72
    print 'WARNING:'
    print
    print 'Subpackges ISO and ARPA will not work on your platform because'
    print 'mxDateTime found no working API to query the timezone'
    print 'for a given date/time. Please run "python testticks.py" and send'
    print 'the output to the author at mal@lemburg.com.'
    print
    print '-'*72
print

# Run parser tests
print 'Importing subpackage Parser.'
print
from mx.DateTime import Parser
Parser._test()

print
print 'Works.'
