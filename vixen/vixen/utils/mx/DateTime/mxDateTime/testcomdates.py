from mx.DateTime import *

c = 35000.0
error = 0
for i in range(1000000):
    t = DateTimeFromCOMDate(c)
    tc = t.COMDate()
    if not tc == c:
        print 'failed for: %s (%.16f != %.16f)' % (t,c,tc)
        error = 1
    # Let's give IEEE floats a hard time...
    if i % 10 == 0:
        c = c - 0.009
    else:
        c = c + 0.0099

if not error:
    print 'All went well !'
