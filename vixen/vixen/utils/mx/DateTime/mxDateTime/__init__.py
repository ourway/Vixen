""" mxDateTime - Date and time handling routines and types

    Copyright (c) 2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.
"""
try:
    from mxDateTime import *
    from mxDateTime import __version__
except ImportError, why:
    print "*** You don't have the (right) mxDateTime binaries installed !"
    raise ImportError, why
    #from mxDateTime_Python import *
    #from mxDateTime_Python import __version__
    
### Python part of the intialization

import time

# Use the time.time() function as basis for now()
try:
    setnowapi(time.time)
except NameError:
    pass

# If strptime() is not available, use the time.strptime() as
# work-around, if that is available
try:
    strptime
    raise NameError
except NameError:
    if hasattr(time, 'strptime'):
        def strptime(string, format,
                     _time=time):
            return DateTime(*_time.strptime(string, format)[:6])

del time
