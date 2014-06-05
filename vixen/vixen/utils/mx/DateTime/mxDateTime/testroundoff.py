from mx.DateTime import *

t = DateTimeFromAbsDateTime(730488,81317.647058823524)
t = t + 1.0/17.0

print t
print
for attr in t.__members__:
    print attr, ':', getattr(t,attr)
