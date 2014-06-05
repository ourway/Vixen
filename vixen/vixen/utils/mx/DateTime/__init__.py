""" mxDateTime - Date and time handling routines and types

    Copyright (c) 1998-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.
"""
from DateTime import *
from DateTime import __version__

### Lazy import submodules
from mx.Misc import LazyModule

ISO = LazyModule.LazyModule('ISO',locals(),globals())
ARPA = LazyModule.LazyModule('ARPA',locals(),globals())
ODMG = LazyModule.LazyModule('ODMG',locals(),globals())
Locale = LazyModule.LazyModule('Locale',locals(),globals())
Feasts = LazyModule.LazyModule('Feasts',locals(),globals())
Parser = LazyModule.LazyModule('Parser',locals(),globals())
NIST = LazyModule.LazyModule('NIST',locals(),globals())
Timezone = LazyModule.LazyModule('Timezone',locals(),globals())

del LazyModule

### Make the types pickleable:

# Shortcuts for pickle (reduces the pickle's length)
def _DT(absdate,abstime,

        DateTimeFromAbsDateTime=DateTimeFromAbsDateTime):

    return DateTimeFromAbsDateTime(absdate,abstime)

def _DTD(seconds,

         DateTimeDeltaFromSeconds=DateTimeDeltaFromSeconds):

    return DateTimeDeltaFromSeconds(seconds)

# Module init
class modinit:

    ### Register the two types
    import copy_reg
    def pickle_DateTime(d):
        return _DT,(d.absdate,d.abstime)
    def pickle_DateTimeDelta(d):
        return _DTD,(d.seconds,)
    copy_reg.pickle(DateTimeType,
                    pickle_DateTime,
                    _DT)
    copy_reg.pickle(DateTimeDeltaType,
                    pickle_DateTimeDelta,
                    _DTD)

del modinit
