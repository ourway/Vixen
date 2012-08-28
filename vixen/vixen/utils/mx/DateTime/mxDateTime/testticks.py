from mx.DateTime import *
import time,sys,string

print 'Python',string.split(sys.version)[0],'on',sys.platform
print

x = time.time()
print 'ticks:',x
print 'time.localtime():',time.localtime(x)
print 'time.gmtime():',time.gmtime(x)
print 'time.mktime():',time.mktime(time.localtime(x)[:-1]+(-1,))
t = DateTimeFromTicks(x)
print 't.ticks():',t.ticks()
print 't.tuple():',t.tuple()
print 't.absdate:',t.absdate
print 't.abstime:',t.abstime
print 't.tuple() -> time.mktime():',apply(time.mktime,t.tuple())
print '          -> time.localtime():',time.localtime(apply(time.mktime,t.tuple()))
print "hasattr(Epoch,'gmticks'):",hasattr(Epoch,'gmticks')
try:
    print 'tz_offset(t):',tz_offset(t)
except:
    print 'tz_offset not working'

print

x = x - 15768000
print 'ticks:',x
print 'time.localtime():',time.localtime(x)
print 'time.gmtime():',time.gmtime(x)
print 'time.mktime():',time.mktime(time.localtime(x)[:-1]+(-1,))
t = DateTimeFromTicks(x)
print 't.ticks():',t.ticks()
print 't.tuple():',t.tuple()
print 't.absdate:',t.absdate
print 't.abstime:',t.abstime
print 't.tuple() -> time.mktime():',apply(time.mktime,t.tuple())
print '          -> time.localtime():',time.localtime(apply(time.mktime,t.tuple()))
print "hasattr(Epoch,'gmticks'):",hasattr(Epoch,'gmticks')
try:
    print 'tz_offset(t):',tz_offset(t)
except:
    print 'tz_offset not working'
