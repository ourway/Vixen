from mx.DateTime import ISO

class AnyClass:
    pass

date = ISO.ParseDateTime('2002-01-01 00:00:00')
rubish = AnyClass()

if date == rubish: print "Oh Dear"
else: print "hurrah!"

class AnyClass:
    def __coerce__(self, other):
       print 'coerce %s and %s' % (repr(self), repr(other))

print date + rubish

#print float(rubish)

