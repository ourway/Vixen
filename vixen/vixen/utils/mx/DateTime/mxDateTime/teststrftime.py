from mx.DateTime import *

t = now()
for i in range(10000):
        s = t.strftime('%D %T %Z')
d = now() - t

print 'elapsed time:',d,' output:',s
