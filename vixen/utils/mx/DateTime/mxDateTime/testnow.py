from mx.DateTime import now
from time import time, clock

rounds = range(10000)

# Warm-up
for i in rounds:
    x = now()
for i in rounds:
    x = time()

c = clock()

for i in rounds:
    x = now()

print 'now(): %5.2f sec.' % (clock() - c)

c = clock()

for i in rounds:
    x = time()

print 'time(): %5.2f sec.' % (clock() - c)

