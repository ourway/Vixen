# -*- coding: latin-1 -*-

""" Timezone information.

    XXX This module still has prototype status and is undocumented.

    XXX Double check the offsets given in the zonetable below.

    XXX Add TZ environment variable parsing functions. The REs are already
        there.

    Copyright (c) 1998-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

"""
import DateTime
import re,string

### REs

# time zone parsing
isozone = ('(?P<zone>[+-]\d\d:?(?:\d\d)?|Z)')
zone = ('(?P<zone>[A-Z]+|[+-]\d\d?:?(?:\d\d)?)')
zoneoffset = ('(?:'
              '(?P<zonesign>[+-])?'
              '(?P<hours>\d\d?)'
              ':?'
              '(?P<minutes>\d\d)?'
              '(?P<extra>\d+)?'
              ')'
              )

# TZ environment variable parsing
dstswitchtime = ('(?P<hour>\d\d?):?'
                 '(?P<minute>\d\d)?:?'
                 '(?P<second>\d\d)?')
dstswitch = ('(?:'
              '(?P<doy>\d+)|'
              '(?:J(?P<jdoy>\d+))|'
              '(?:M(?P<month>\d+).(?P<week>\d+).(?P<day>\d+))'
             ')'
             '(?:/' + dstswitchtime + ')?'
             )

# XXX Doesn't work since re doesn't like multiple occurrences of
#     group names.
#tz = ('(?::(?P<filename>.+))|'
#      '(?P<std>[A-Z]+)' + zoneoffset + 
#      '(?:'
#       '(?P<dst>[A-Z]+)' + zoneoffset + '?'+
#       '(?:[;,]' + dstswitch + '[;,]' + dstswitch + ')'
#      ')?'
#      )

# Compiled RE objects
isozoneRE = re.compile(zone)
zoneRE = re.compile(zone)
zoneoffsetRE = re.compile(zoneoffset)
#tzRE= re.compile(tz)

### Time zone offset table
#
# The offset given here represent the difference between UTC and the
# given time zone.
#
# Additions and corrections are always welcome :-)
#
# Note that some zone names are ambiguous, e.g. IST can refer to Irish
# Summer Time, Indian Standard Time, Israel Standard Time. We've
# usualy chosen meaning with the most wide-spread use.
#
zonetable = {
              # Timezone abbreviations
              # Std     Summer

              # Standards
              'UT':0,
              'UTC':0,
              'GMT':0,

              # A few common timezone abbreviations
              'CET':1,  'CEST':2, 'CETDST':2, # Central European
              'MET':1,  'MEST':2, 'METDST':2, # Mean European
              'MEZ':1,  'MESZ':2,             # Mitteleuropäische Zeit
              'EET':2,  'EEST':3, 'EETDST':3, # Eastern Europe
              'WET':0,  'WEST':1, 'WETDST':1, # Western Europe
              'MSK':3,  'MSD':4,  # Moscow
              'IST':5.5,          # India
              'JST':9,            # Japan
              'KST':9,            # Korea
              'HKT':8,            # Hong Kong

              # US time zones
              'AST':-4, 'ADT':-3, # Atlantic
              'EST':-5, 'EDT':-4, # Eastern
              'CST':-6, 'CDT':-5, # Central
              'MST':-7, 'MDT':-6, # Midwestern
              'PST':-8, 'PDT':-7, # Pacific

              # Australian time zones
              'CAST':9.5, 'CADT':10.5, # Central
              'EAST':10,  'EADT':11,   # Eastern
              'WAST':8,   'WADT':9,    # Western
              'SAST':9.5, 'SADT':10.5, # Southern

              # US military time zones
              'Z': 0,
              'A': 1,
              'B': 2,
              'C': 3,
              'D': 4,
              'E': 5,
              'F': 6,
              'G': 7,
              'H': 8,
              'I': 9,
              'K': 10,
              'L': 11,
              'M': 12,
              'N':-1,
              'O':-2,
              'P':-3,
              'Q':-4,
              'R':-5,
              'S':-6,
              'T':-7,
              'U':-8,
              'V':-9,
              'W':-10,
              'X':-11,
              'Y':-12
              }    

def utc_offset(zone,

               atoi=string.atoi,zoneoffset=zoneoffsetRE,
               zonetable=zonetable,zerooffset=DateTime.DateTimeDelta(0),
               oneMinute=DateTime.oneMinute,upper=string.upper):

    """ utc_offset(zonestring)

        Return the UTC time zone offset as DateTimeDelta instance.

        zone must be string and can either be given as +-HH:MM,
        +-HHMM, +-HH numeric offset or as time zone
        abbreviation. Daylight saving time must be encoded into the
        zone offset.

        Timezone abbreviations are treated case-insensitive.

    """
    if not zone:
        return zerooffset
    uzone = upper(zone)
    if zonetable.has_key(uzone):
        return zonetable[uzone]*DateTime.oneHour
    offset = zoneoffset.match(zone)
    if not offset:
        raise ValueError,'wrong format or unknown time zone: "%s"' % zone
    zonesign,hours,minutes,extra = offset.groups()
    if extra:
        raise ValueError,'illegal time zone offset: "%s"' % zone
    offset = int(hours or 0) * 60 + int(minutes or 0)
    if zonesign == '-':
        offset = -offset
    return offset*oneMinute

