""" A timegm() emulation for platforms that do not provide the C lib
    API.

    This is the prototype I used to code the timegm() C emulation in
    mxDateTime. It offers a little more than is really needed...

    Copyright (c) 2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

"""
from time import *

_debug = 0

def local_offset(ticks):

    if _debug:
        print 'local:',localtime(ticks)
        print 'GMT:',gmtime(ticks)
    (localyear,localmonth,localday,
     localhour,localminute,localsecond,
     localwday,localyday,localdst) = localtime(ticks)
    (gmyear,gmmonth,gmday,
     gmhour,gmminute,gmsecond,
     gmwday,gmyday,gmdst) = gmtime(ticks)
    if gmday != localday:
        localdate = localyear * 10000 + localmonth * 100 + localday
        gmdate = gmyear * 10000 + gmmonth * 100 + gmday
        if localdate < gmdate:
            offset = -86400
        else:
            offset = 86400
    else:
        offset = 0
    return (offset 
            + (localhour - gmhour) * 3600
            + (localminute - gmminute) * 60
            + (localsecond - gmsecond))

def timegm(year,month,day,hour,minute,second,wday,yday,dst):

    try:
        ticks = mktime(year,month,day,hour,minute,second,wday,yday,-1)
        return ticks + local_offset(ticks)
    except OverflowError:
        # Hmm, we may have stumbled into the "missing" hour during a
        # DST switch...
        ticks = mktime(year,month,day,0,0,0,wday,yday,-1) 
        offset = local_offset(ticks)
        return (ticks + offset
                + 3600 * hour
                + 60 * minute
                + second)

def dst(ticks):

    offset = local_offset(ticks)
    for checkpoint in (-8640000,10000000,-20560000,20560000):
        try:
            reference = local_offset(ticks + checkpoint)
        except OverflowError:
            continue
        if reference != offset:
            break
    if _debug:
        print 'given:',offset,'reference:',reference,'(checkpoint:',checkpoint,')'
    return offset > reference

def _test():

    t = 920710000
    oops = 0
    while 1:
        x = apply(timegm,gmtime(t))
        if x != t:
            print 'Ooops:',gmtime(t),'t =',t,'diff =',x-t
            oops = oops + 1
        isdst = localtime(t)[-1]
        if isdst != -1 and isdst != dst(t):
            print 'Ooops: t =',t,'dst() =',dst(t),'isdst =',isdst
            oops = oops + 1
        try:
            t = t + 10011
        except OverflowError:
            break
    if not oops:
        print 'Works.'
        return 1
    else:
        print 'Got %i warnings.' % oops
        return 0

if __name__ == '__main__':
    _test()

