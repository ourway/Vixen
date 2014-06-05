from mx.DateTime import *

t = now()
print 'Init...'
l = [None] * 10000
for i in range(10000):
        l[i] = DateTimeFromAbsDateTime(t.absdate + i,0)

print 'Sorting... plain'
t = now()
for i in range(100):
        l.sort()
        l.reverse()
d = now() - t
print ' elapsed time:',d

print 'Sorting... with cmp()'
t = now()
for i in range(100):
        l.sort(cmp)
        l.reverse()
d = now() - t

print ' elapsed time:',d
