from mx.DateTime import ISO

class AnyClass:
    pass

date = ISO.ParseDateTime('2002-01-01 00:00:00')
anyclass = AnyClass()

if date == anyclass: print "Should not compare equal ?!"
else: print "Works."
