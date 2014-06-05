# -*- coding: latin-1 -*-

""" Date/Time string parsing module.

    Note about the Y2K problems:

       The parser can only handle years with at least 2 digits. 2
       digit year values get expanded by adding the century using
       DateTime.add_century(), while 3 digit year get converted
       literally. To have 2 digit years also be interpreted literally,
       add leading zeros, e.g. year 99 must be written as 099 or 0099.

    Copyright (c) 1998-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

"""
import types,re,string
import DateTime,ISO,ARPA,Timezone

# Enable to produce debugging output
_debug = 0

# REs for matching date and time parts in a string; These REs
# parse a superset of ARPA, ISO, American and European style dates.
# Timezones are supported via the Timezone submodule.

_year = '(?P<year>-?\d+\d(?!:))'
_fullyear = '(?P<year>-?\d+\d\d(?!:))'
_year_epoch = '(?:' + _year + '(?P<epoch> *[ABCDE\.]+)?)'
_fullyear_epoch = '(?:' + _fullyear + '(?P<epoch> *[ABCDE\.]+)?)'
_relyear = '(?:\((?P<relyear>[-+]?\d+)\))'

_month = '(?P<month>\d?\d(?!:))'
_fullmonth = '(?P<month>\d\d(?!:))'
_litmonth = ('(?P<litmonth>'
             'jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|'
             'mär|mae|mrz|mai|okt|dez|'
             'fev|avr|juin|juil|aou|aoû|déc|'
             'ene|abr|ago|dic|'
             'out'
             ')[a-z,\.;]*')
litmonthtable = {
    # English
    'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6,
    'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12,
    # German
    'mär':3, 'mae':3, 'mrz':3, 'mai':5, 'okt':10, 'dez':12,
    # French
    'fev':2, 'avr':4, 'juin':6, 'juil':7, 'aou':8, 'aoû':8,
    'déc':12,
    # Spanish
    'ene':1, 'abr':4, 'ago':8, 'dic':12,
    # Portuguese
    'out':10,
    }
_relmonth = '(?:\((?P<relmonth>[-+]?\d+)\))'

_day = '(?P<day>\d?\d(?!:))'
_usday = '(?P<day>\d?\d(?!:))(?:st|nd|rd|th|[,\.;])?'
_fullday = '(?P<day>\d\d(?!:))'
_litday = ('(?P<litday>'
           'mon|tue|wed|thu|fri|sat|sun|'
           'die|mit|don|fre|sam|son|'
           'lun|mar|mer|jeu|ven|sam|dim|'
           'mie|jue|vie|sab|dom|'
           'pri|seg|ter|cua|qui'
           ')[a-z]*')
litdaytable = {
    # English
    'mon':0, 'tue':1, 'wed':2, 'thu':3, 'fri':4, 'sat':5, 'sun':6,
    # German
    'die':1, 'mit':2, 'don':3, 'fre':4, 'sam':5, 'son':6,
    # French
    'lun':0, 'mar':1, 'mer':2, 'jeu':3, 'ven':4, 'sam':5, 'dim':6,
    # Spanish
    'mie':2, 'jue':3, 'vie':4, 'sab':5, 'dom':6,
    # Portuguese
    'pri':0, 'seg':1, 'ter':2, 'cua':3, 'qui':4,
    }
_relday = '(?:\((?P<relday>[-+]?\d+)\))'

_hour = '(?P<hour>[012]?\d)'
_minute = '(?P<minute>[0-6]\d)'
_second = '(?P<second>[0-6]\d(?:[.,]\d+)?)'

_days = '(?P<days>\d*\d(?:[.,]\d+)?)'
_hours = '(?P<hours>\d*\d(?:[.,]\d+)?)'
_minutes = '(?P<minutes>\d*\d(?:[.,]\d+)?)'
_seconds = '(?P<seconds>\d*\d(?:[.,]\d+)?)'

_reldays = '(?:\((?P<reldays>[-+]?\d+(?:[.,]\d+)?)\))'
_relhours = '(?:\((?P<relhours>[-+]?\d+(?:[.,]\d+)?)\))'
_relminutes = '(?:\((?P<relminutes>[-+]?\d+(?:[.,]\d+)?)\))'
_relseconds = '(?:\((?P<relseconds>[-+]?\d+(?:[.,]\d+)?)\))'

_sign = '(?:(?P<sign>[-+]) *)'
_week = 'W(?P<week>\d?\d)'
_zone = Timezone.zone
_ampm = '(?P<ampm>[ap][m.]+)'

_time = (_hour + ':' + _minute + '(?::' + _second + '|[^:]|$) *'
         + _ampm + '? *' + _zone + '?')
_isotime = _hour + ':?' + _minute + ':?' + _second + '? *' + _zone + '?'

_weekdate = _year + '-?(?:' + _week + '-?' + _day + '?)?'
_eurodate = _day + '\.' + _month + '\.' + _year_epoch + '?'
_usdate = _month + '/' + _day + '(?:/' + _year_epoch + '|[^/]|$)'
_altusdate = _month + '-' + _day + '-' + _fullyear_epoch
_isodate = _year + '-' + _month + '-?' + _day + '?(?!:)'
_altisodate = _year + _fullmonth + _fullday + '(?!:)'
_usisodate = _fullyear + '/' + _fullmonth + '/' + _fullday
_litdate = ('(?:'+ _litday + ',? )? *' + 
            _usday + ' *' + 
            '[- ] *(?:' + _litmonth + '|'+ _month +') *[- ] *' +
            _year_epoch + '?')
_altlitdate = ('(?:'+ _litday + ',? )? *' + 
               _litmonth + '[ ,.a-z]+' +
               _usday + 
               '(?:[ a-z]+' + _year_epoch + ')?')
_eurlitdate = ('(?:'+ _litday + ',?[ a-z]+)? *' + 
               '(?:'+ _usday + '[ a-z]+)? *' +
               _litmonth + 
               '(?:[ ,.a-z]+' + _year_epoch + ')?')

_relany = '[*%?a-zA-Z]+'

_relisodate = ('(?:(?:' + _relany + '|' + _year + '|' + _relyear + ')-' +
               '(?:' + _relany + '|' + _month + '|' + _relmonth + ')-' +
               '(?:' + _relany + '|' + _day + '|' + _relday + '))')

_asctime = ('(?:'+ _litday + ',? )? *' + 
                _usday + ' *' + 
                '[- ] *(?:' + _litmonth + '|'+ _month +') *[- ]' +
                '(?:[0-9: ]+)' + 
                _year_epoch + '?')

_relisotime = ('(?:(?:' + _relany + '|' + _hour + '|' + _relhours + '):' +
               '(?:' + _relany + '|' + _minute + '|' + _relminutes + ')' +
               '(?::(?:' + _relany + '|' + _second + '|' + _relseconds + '))?)')

_isodelta1 = (_sign + '?' +
              _days + ':' + _hours + ':' + _minutes + ':' + _seconds)
_isodelta2 = (_sign + '?' + 
              _hours + ':' + _minutes + ':' + _seconds)
_isodelta3 = (_sign + '?' + 
              _hours + ':' + _minutes)
_litdelta = (_sign + '?' +
             '(?:' + _days + ' *d[a-z]*[,; ]*)?' + 
             '(?:' + _hours + ' *h[a-z]*[,; ]*)?' + 
             '(?:' + _minutes + ' *m[a-z]*[,; ]*)?' +
             '(?:' + _seconds + ' *s[a-z]*[,; ]*)?')
_litdelta2 = (_sign + '?' +
             '(?:' + _days + ' *d[a-z]*[,; ]*)?' + 
              _hours + ':' + _minutes + '(?::' + _seconds + ')?')

_timeRE = re.compile(_time, re.I)
_isotimeRE = re.compile(_isotime, re.I)
_isodateRE = re.compile(_isodate, re.I)
_altisodateRE = re.compile(_altisodate, re.I)
_usisodateRE = re.compile(_usisodate, re.I)
_eurodateRE = re.compile(_eurodate, re.I)
_usdateRE = re.compile(_usdate, re.I)
_altusdateRE = re.compile(_altusdate, re.I)
_litdateRE = re.compile(_litdate, re.I)
_altlitdateRE = re.compile(_altlitdate, re.I)
_eurlitdateRE = re.compile(_eurlitdate, re.I)
_relisodateRE = re.compile(_relisodate, re.I)
_asctimeRE = re.compile(_asctime, re.I)
_isodelta1RE = re.compile(_isodelta1)
_isodelta2RE = re.compile(_isodelta2)
_isodelta3RE = re.compile(_isodelta3)
_litdeltaRE = re.compile(_litdelta)
_litdelta2RE = re.compile(_litdelta2)
_relisotimeRE = re.compile(_relisotime, re.I)

# Available date parsers
_date_formats = ('euro',
                 'usiso', 'us', 'altus',
                 'iso', 'altiso', 
                 'lit', 'altlit', 'eurlit',
                 'unknown')

# Available time parsers
_time_formats = ('standard',
                 'iso',
                 'unknown')

def _parse_date(text, formats=_date_formats, defaultdate=None,

                int=int,float=float,lower=string.lower,
                add_century=DateTime.add_century,
                now=DateTime.now,us_formats=('us', 'altus'),
                iso_formats=('iso', 'altiso', 'usiso')):

    """ Parses the date part given in text and returns a tuple
        (text,day,month,year,style) with the following
        meanings:

        * text gives the original text without the date part

        * day,month,year give the parsed date

        * style gives information about which parser was successful:
          'euro' - the European date parser
          'us' - the US date parser
          'altus' - the alternative US date parser (with '-' instead of '/')
          'iso' - the ISO date parser
          'altiso' - the alternative ISO date parser (without '-')
          'usiso' - US style ISO date parser (yyyy/mm/dd)
          'lit' - the US literal date parser
          'altlit' - the alternative US literal date parser
          'eurlit' - the Eurpean literal date parser
          'unknown' - no date part was found, defaultdate was used

        formats may be set to a tuple of style strings specifying
        which of the above parsers to use and in which order to try
        them. Default is to try all of them in the above order.

        defaultdate provides the defaults to use in case no date part
        is found. Most other parsers default to the current year
        January 1 if some of these date parts are missing.

        If 'unknown' is not given in formats and the date cannot be
        parsed, a ValueError is raised.

    """
    match = None
    style = ''
    
    # Apply parsers in the order given in formats
    for format in formats:

        if format == 'euro':
            # European style date
            match = _eurodateRE.search(text)
            if match is not None:
                day,month,year,epoch = match.groups()
                if year:
                    if len(year) == 2:
                        # Y2K problem:
                        year = add_century(int(year))
                    else:
                        year = int(year)
                else:
                    if defaultdate is None:
                        defaultdate = now()
                    year = defaultdate.year
                if epoch and 'B' in epoch:
                    year = -year + 1
                month = int(month)
                day = int(day)
                # Could have mistaken euro format for us style date
                # which uses month, day order
                if month > 12 or month == 0:
                    match = None
                    continue
                break

        elif format in iso_formats:
            # ISO style date
            if format == 'iso':
                match = _isodateRE.search(text)
            elif format == 'altiso':
                match = _altisodateRE.search(text)
                # Avoid mistaking ISO time parts ('Thhmmss') for dates
                if match is not None:
                    left, right = match.span()
                    if left > 0 and \
                       text[left - 1:left] == 'T':
                        match = None
                        continue
            else:
                match = _usisodateRE.search(text)
            if match is not None:
                year,month,day = match.groups()
                if len(year) == 2:
                    # Y2K problem:
                    year = add_century(int(year))
                else:
                    year = int(year)
                # Default to January 1st
                if not month:
                    month = 1
                else:
                    month = int(month)
                if not day:
                    day = 1
                else:
                    day = int(day)
                break

        elif format in us_formats:
            # US style date
            if format == 'us':
                match = _usdateRE.search(text)
            else:
                match = _altusdateRE.search(text)
            if match is not None:
                month,day,year,epoch = match.groups()
                if year:
                    if len(year) == 2:
                        # Y2K problem:
                        year = add_century(int(year))
                    else:
                        year = int(year)
                else:
                    if defaultdate is None:
                        defaultdate = now()
                    year = defaultdate.year
                if epoch and 'B' in epoch:
                    year = -year + 1
                # Default to 1 if no day is given
                if day:
                    day = int(day)
                else:
                    day = 1
                month = int(month)
                # Could have mistaken us format for euro style date
                # which uses day, month order
                if month > 12 or month == 0:
                    match = None
                    continue
                break

        elif format == 'lit':
            # US style literal date
            match = _litdateRE.search(text)
            if match is not None:
                litday,day,litmonth,month,year,epoch = match.groups()
                break

        elif format == 'altlit':
            # Alternative US style literal date
            match = _altlitdateRE.search(text)
            if match is not None: 
                litday,litmonth,day,year,epoch = match.groups()
                month = '<missing>'
                break

        elif format == 'eurlit':
            # European style literal date
            match = _eurlitdateRE.search(text)
            if match is not None: 
                litday,day,litmonth,year,epoch = match.groups()
                month = '<missing>'
                break

        elif format == 'unknown':
            # No date part: use defaultdate
            if defaultdate is None:
                defaultdate = now()
            year = defaultdate.year
            month = defaultdate.month
            day = defaultdate.day
            style = format
            break

    # Check success
    if match is not None:
        # Remove date from text
        left, right = match.span()
        if 0 and _debug:
            print 'parsed date:',repr(text[left:right]),\
                  'giving:',year,month,day
        text = text[:left] + text[right:]
        style = format
        
    elif not style:
        # Not recognized: raise an error
        raise ValueError, 'unknown date format: "%s"' % text

    # Literal date post-processing
    if style in ('lit', 'altlit', 'eurlit'):
        if 0 and _debug: print match.groups()
        # Default to current year, January 1st
        if not year:
            if defaultdate is None:
                defaultdate = now()
            year = defaultdate.year
        else:
            if len(year) == 2:
                # Y2K problem:
                year = add_century(int(year))
            else:
                year = int(year)
        if epoch and 'B' in epoch:
            year = -year + 1
        if litmonth:
            litmonth = lower(litmonth)
            try:
                month = litmonthtable[litmonth]
            except KeyError:
                raise ValueError,\
                      'wrong month name: "%s"' % litmonth
        elif month:
            month = int(month)
        else:
            month = 1
        if day:
            day = int(day)
        else:
            day = 1

    #print '_parse_date:',text,day,month,year,style
    return text,day,month,year,style

def _parse_time(text, formats=_time_formats,

                int=int,float=float,replace=string.replace):

    """ Parses a time part given in text and returns a tuple
        (text,hour,minute,second,offset,style) with the following
        meanings:

        * text gives the original text without the time part
        * hour,minute,second give the parsed time
        * offset gives the time zone UTC offset
        * style gives information about which parser was successful:
          'standard' - the standard parser
          'iso' - the ISO time format parser
          'unknown' - no time part was found

        formats may be set to a tuple specifying the parsers to use:
          'standard' - standard time format with ':' delimiter
          'iso' - ISO time format (superset of 'standard')
          'unknown' - default to 0:00:00, 0 zone offset

        If 'unknown' is not given in formats and the time cannot be
        parsed, a ValueError is raised.

    """
    match = None
    style = ''

    # Apply parsers in the order given in formats
    for format in formats:

        # Standard format
        if format == 'standard':
            match = _timeRE.search(text)
            if match is not None:
                hour,minute,second,ampm,zone = match.groups()
                style = 'standard'
                break

        # ISO format
        if format == 'iso':
            match =  _isotimeRE.search(text)
            if match is not None:
                hour,minute,second,zone = match.groups()
                ampm = None
                style = 'iso'
                break

        # Default handling
        elif format == 'unknown':
            hour,minute,second,offset = 0,0,0.0,0
            style = 'unknown'
            break

    if not style:
        # If no default handling should be applied, raise an error
        raise ValueError, 'unknown time format: "%s"' % text

    # Post-processing
    if match is not None:
        if zone:
            # Convert to UTC offset
            offset = Timezone.utc_offset(zone)
        else:
            offset = 0
        hour = int(hour)
        if ampm:
            if ampm[0] in ('p', 'P'):
                # 12pm = midday
                if hour < 12:
                    hour = hour + 12
            else:
                # 12am = midnight 
                if hour >= 12:
                    hour = hour - 12
        if minute:
            minute = int(minute)
        else:
            minute = 0
        if not second:
            second = 0.0
        else:
            if ',' in second:
                second = replace(second, ',', '.')
            second = float(second)

        # Remove time from text
        left,right = match.span()
        if 0 and _debug: 
            print 'parsed time:',repr(text[left:right]),\
                  'giving:',hour,minute,second,offset
        text = text[:left] + text[right:]

    #print '_parse_time:',text,hour,minute,second,offset,style
    return text,hour,minute,second,offset,style

###

def DateTimeFromString(text, formats=_date_formats, defaultdate=None,
                       time_formats=_time_formats,

                       DateTime=DateTime):

    """ DateTimeFromString(text, [formats, defaultdate])
    
        Returns a DateTime instance reflecting the date and time given
        in text. In case a timezone is given, the returned instance
        will point to the corresponding UTC time value. Otherwise, the
        value is set as given in the string.

        formats may be set to a tuple of strings specifying which of
        the following parsers to use and in which order to try
        them. Default is to try all of them in the order given below:

          'euro' - the European date parser
          'us' - the US date parser
          'altus' - the alternative US date parser (with '-' instead of '/')
          'iso' - the ISO date parser
          'altiso' - the alternative ISO date parser (without '-')
          'usiso' - US style ISO date parser (yyyy/mm/dd)
          'lit' - the US literal date parser
          'altlit' - the alternative US literal date parser
          'eurlit' - the Eurpean literal date parser
          'unknown' - if no date part is found, use defaultdate

        defaultdate provides the defaults to use in case no date part
        is found. Most of the parsers default to the current year
        January 1 if some of these date parts are missing.

        If 'unknown' is not given in formats and the date cannot
        be parsed, a ValueError is raised.

        time_formats may be set to a tuple of strings specifying which
        of the following parsers to use and in which order to try
        them. Default is to try all of them in the order given below:

          'standard' - standard time format HH:MM:SS (with ':' delimiter)
          'iso' - ISO time format (superset of 'standard')
          'unknown' - default to 00:00:00 in case the time format
                      cannot be parsed

        Defaults to 00:00:00.00 for time parts that are not included
        in the textual representation.

        If 'unknown' is not given in time_formats and the time cannot
        be parsed, a ValueError is raised.

    """
    origtext = text
    formats = tuple(formats)

    if formats is _date_formats or \
       'iso' in formats or \
       'altiso' in formats:

        # First try standard order (parse time, then date)
        if formats[0] not in ('iso', 'altiso'):
            text,hour,minute,second,offset,timestyle = _parse_time(
                origtext,
                time_formats)
            text,day,month,year,datestyle = _parse_date(
                text,
                formats + ('unknown',),
                defaultdate)
            if 0 and _debug:
                print 'tried time/date on %s, date=%s, time=%s' % (origtext,
                                                                   datestyle,
                                                                   timestyle)
        else:
            timestyle = 'iso'
            
        # If this fails, try the ISO order (date, then time)
        if timestyle in ('iso', 'unknown'):
            text,day,month,year,datestyle = _parse_date(
                origtext,
                formats,
                defaultdate)
            text,hour,minute,second,offset,timestyle = _parse_time(
                text,
                time_formats)
            if 0 and _debug:
                print 'tried ISO on %s, date=%s, time=%s' % (origtext,
                                                             datestyle,
                                                             timestyle)
    else:
        # Standard order: time part, then date part
        text,hour,minute,second,offset,timestyle = _parse_time(
            origtext,
            time_formats)
        text,day,month,year,datestyle = _parse_date(
            text,
            formats,
            defaultdate)

    if (datestyle == 'unknown' and 'unknown' not in formats) or \
       (timestyle == 'unknown' and 'unknown' not in time_formats):
        raise ValueError,\
              'Failed to parse "%s": found "%s" date, "%s" time' % \
              (origtext, datestyle, timestyle)
    
    try:
        return DateTime.DateTime(year,month,day,hour,minute,second) - offset
    except DateTime.RangeError, why:
        raise DateTime.RangeError,\
              'Failed to parse "%s": %s' % (origtext, why)

def DateFromString(text, formats=_date_formats, defaultdate=None,

                   DateTime=DateTime):

    """ DateFromString(text, [formats, defaultdate])
    
        Returns a DateTime instance reflecting the date given in
        text. A possibly included time part is ignored.

        formats and defaultdate work just like for
        DateTimeFromString().

    """
    _text,day,month,year,datestyle = _parse_date(text, formats, defaultdate)

    if datestyle == 'unknown' and \
       'unknown' not in formats:
        raise ValueError,\
              'Failed to parse "%s": found "%s" date' % \
              (origtext, datestyle)

    try:
        return DateTime.DateTime(year,month,day)
    except DateTime.RangeError, why:
        raise DateTime.RangeError,\
              'Failed to parse "%s": %s' % (text, why)

def validateDateTimeString(text, formats=_date_formats):

    """ validateDateTimeString(text, [formats, defaultdate])

        Validates the given text and returns 1/0 depending on whether
        text includes parseable date and time values or not.

        formats works just like for DateTimeFromString() and defines
        the order of date/time parsers to apply. It defaults to the
        same list of parsers as for DateTimeFromString().

        XXX Undocumented !
    
    """
    formats = list(formats)
    if 'unknown' in formats:
        formats.remove('unknown')
    try:
        DateTimeFromString(text, formats)
    except (DateTime.RangeError, ValueError), why:
        return 0
    return 1

def validateDateString(text, formats=_date_formats):

    """ validateDateString(text, [formats, defaultdate])

        Validates the given text and returns 1/0 depending on whether
        text includes a parseable date value or not.

        formats works just like for DateTimeFromString() and defines
        the order of date/time parsers to apply. It defaults to the
        same list of parsers as for DateTimeFromString().
    
        XXX Undocumented !
    
    """
    formats = list(formats)
    if 'unknown' in formats:
        formats.remove('unknown')
    try:
        DateFromString(text, formats)
    except (DateTime.RangeError, ValueError), why:
        return 0
    return 1

def TimeFromString(text, formats=_time_formats,

                   DateTime=DateTime):

    """ TimeFromString(text, [formats])
    
        Returns a DateTimeDelta instance reflecting the time given in
        text. A possibly included date part is ignored.

        formats may be set to a tuple of strings specifying which of
        the following parsers to use and in which order to try
        them. Default is to try all of them in the order given below:

          'standard' - standard time format with ':' delimiter
          'iso' - ISO time format (superset of 'standard')
          'unknown' - default to 00:00:00 in case the time format
                      cannot be parsed

        Defaults to 00:00:00.00 for parts that are not included in the
        textual representation.
        
    """
    _text,hour,minute,second,offset,timestyle = _parse_time(
        text,
        formats)

    if timestyle == 'unknown' and \
       'unknown' not in formats:
        raise ValueError,\
              'Failed to parse "%s": found "%s" time' % \
              (text, timestyle)

    try:
        dtd = DateTime.DateTimeDelta(0.0, hour, minute, second)
    except DateTime.RangeError, why:
        raise DateTime.RangeError,\
              'Failed to parse "%s": %s' % (text, why)
    else:
        # XXX What to do with offset ?
        return dtd

#
# XXX Still missing: validateTimeString(), validateDateTimeDeltaString()
#                    and validateTimeDeltaString()
#

def DateTimeDeltaFromString(text,

                            float=float,DateTime=DateTime):

    """ DateTimeDeltaFromString(text)
    
        Returns a DateTimeDelta instance reflecting the delta given in
        text. Defaults to 0:00:00:00.00 for parts that are not
        included in the textual representation or cannot be parsed.

    """
    match = _isodelta1RE.search(text)
    if match is not None:
        sign, days, hours, minutes, seconds = match.groups()
    else:
        match = _litdelta2RE.search(text)
        if match is not None:
            sign, days, hours, minutes, seconds = match.groups()
        else:
            match = _isodelta2RE.search(text)
            if match is not None:
                sign, hours, minutes, seconds = match.groups()
                days = None
            else:
                match = _isodelta3RE.search(text)
                if match is not None:
                    sign, hours, minutes = match.groups()
                    days = None
                    seconds = None
                else:
                    match = _litdeltaRE.search(text)
                    if match is not None:
                        sign, days, hours, minutes, seconds = match.groups()

                    else:
                        # Not matched:
                        return DateTime.DateTimeDelta(0.0)

    # Conversions
    if days:
        days = float(days)
    else:
        days = 0.0
    if hours:
        hours = float(hours)
    else:
        hours = 0.0
    if minutes:
        minutes = float(minutes)
    else:
        minutes = 0.0
    if seconds:
        seconds = float(seconds)
    else:
        seconds = 0.0
    if sign != '-':
        sign = 1
    else:
        sign = -1

    try:
        dtd = DateTime.DateTimeDelta(days,hours,minutes,seconds)
    except DateTime.RangeError, why:
        raise DateTime.RangeError,\
              'Failed to parse "%s": %s' % (text, why)
    else:
        if sign < 0:
            return -dtd
        else:
            return dtd

# Aliases
TimeDeltaFromString = DateTimeDeltaFromString

###

def _parse_reldate(text,

                   int=int,float=float):

    match = _relisodateRE.search(text)
    if match is not None:
        groups = match.groups()
        if 0 and _debug: print groups
        year,years,month,months,day,days = groups
        if year:
            year = int(year)
        if years:
            years = float(years)
        else:
            years = 0
        if month:
            month = int(month)
        if months:
            months = float(months)
        else:
            months = 0
        if day:
            day = int(day)
        if days:
            days = float(days)
        else:
            days = 0
        return year,years,month,months,day,days
    else:
        return None,0,None,0,None,0

def _parse_reltime(text,

                   int=int,float=float):

    match = _relisotimeRE.search(text)
    if match is not None:
        groups = match.groups()
        if 0 and _debug: print groups
        hour,hours,minute,minutes,second,seconds = groups
        if hour:
            hour = int(hour)
        if hours:
            hours = float(hours)
        else:
            hours = 0
        if minute:
            minute = int(minute)
        if minutes:
            minutes = float(minutes)
        else:
            minutes = 0
        if second:
            second = int(second)
        if seconds:
            seconds = float(seconds)
        else:
            seconds = 0
        return hour,hours,minute,minutes,second,seconds
    else:
        return None,0,None,0,None,0

def RelativeDateTimeFromString(text,

                               RelativeDateTime=DateTime.RelativeDateTime):

    """ RelativeDateTimeFromString(text)
    
        Returns a RelativeDateTime instance reflecting the relative
        date and time given in text.

        Defaults to wildcards for parts or values which are not
        included in the textual representation or cannot be parsed.

        The format used in text must adhere to the following syntax:

        		[YYYY-MM-DD] [HH:MM[:SS]]

        with the usual meanings. Values which should not be altered
        may be replaced with '*', '%', '?' or any combination of
        letters, e.g. 'YYYY'. Relative settings must be enclosed in
        parenthesis if given and should include a sign, e.g. '(+0001)'
        for the year part. All other settings are interpreted as
        absolute values.

        Date and time parts are both optional as a whole. Seconds in
        the time part are optional too. Everything else (including the
        hyphens and colons) is mandatory.

    """
    year,years,month,months,day,days = _parse_reldate(text)
    hour,hours,minute,minutes,second,seconds = _parse_reltime(text)
    return RelativeDateTime(year=year,years=years,
                            month=month,months=months,
                            day=day,days=days,
                            hour=hour,hours=hours,
                            minute=minute,minutes=minutes,
                            second=second,seconds=seconds)

def RelativeDateFromString(text,

                           RelativeDateTime=DateTime.RelativeDateTime):

    """ RelativeDateFromString(text)
    
        Same as RelativeDateTimeFromString(text) except that only the
        date part of text is taken into account.

    """
    year,years,month,months,day,days = _parse_reldate(text)
    return RelativeDateTime(year=year,years=years,
                            month=month,months=months,
                            day=day,days=days)

def RelativeTimeFromString(text,

                           RelativeDateTime=DateTime.RelativeDateTime):

    """ RelativeTimeFromString(text)
    
        Same as RelativeDateTimeFromString(text) except that only the
        time part of text is taken into account.

    """
    hour,hours,minute,minutes,second,seconds = _parse_reltime(text)
    return RelativeDateTime(hour=hour,hours=hours,
                            minute=minute,minutes=minutes,
                            second=second,seconds=seconds)

### Tests

def _test():

    import sys

    t = DateTime.now()

    print 'Testing DateTime Parser...'

    l = [

        # Literal formats
        ('Sun Nov  6 08:49:37 1994', '1994-11-06 08:49:37.00'),
        ('sun nov  6 08:49:37 1994', '1994-11-06 08:49:37.00'),
        ('sUN NOV  6 08:49:37 1994', '1994-11-06 08:49:37.00'),
        ('Sunday, 06-Nov-94 08:49:37 GMT', '1994-11-06 08:49:37.00'),
        ('Sun, 06 Nov 1994 08:49:37 GMT', '1994-11-06 08:49:37.00'),
        ('06-Nov-94 08:49:37', '1994-11-06 08:49:37.00'),
        ('06-Nov-94', '1994-11-06 00:00:00.00'),
        ('06-NOV-94', '1994-11-06 00:00:00.00'),
        ('November 19 08:49:37', '%s-11-19 08:49:37.00' % t.year),
        ('Nov. 9', '%s-11-09 00:00:00.00' % t.year),
        ('Sonntag, der 6. November 1994, 08:49:37 GMT', '1994-11-06 08:49:37.00'),
        ('6. November 2001, 08:49:37', '2001-11-06 08:49:37.00'),
        ('sep 6', '%s-09-06 00:00:00.00' % t.year),
        ('sep 6 2000', '2000-09-06 00:00:00.00'),
        ('September 29', '%s-09-29 00:00:00.00' % t.year),
        ('Sep. 29', '%s-09-29 00:00:00.00' % t.year),
        ('6 sep', '%s-09-06 00:00:00.00' % t.year),
        ('29 September', '%s-09-29 00:00:00.00' % t.year),
        ('29 Sep.', '%s-09-29 00:00:00.00' % t.year),
        ('sep 6 2001', '2001-09-06 00:00:00.00'),
        ('Sep 6, 2001', '2001-09-06 00:00:00.00'),
        ('September 6, 2001', '2001-09-06 00:00:00.00'),
        ('sep 6 01', '2001-09-06 00:00:00.00'),
        ('Sep 6, 01', '2001-09-06 00:00:00.00'),
        ('September 6, 01', '2001-09-06 00:00:00.00'),
        ('30 Apr 2006 20:19:00', '2006-04-30 20:19:00.00'),
        
        # ISO formats
        ('1994-11-06 08:49:37', '1994-11-06 08:49:37.00'),
        ('010203', '2001-02-03 00:00:00.00'),
        ('2001-02-03 00:00:00.00', '2001-02-03 00:00:00.00'),
        ('2001-02 00:00:00.00', '2001-02-01 00:00:00.00'),
        ('2001-02-03', '2001-02-03 00:00:00.00'),
        ('2001-02', '2001-02-01 00:00:00.00'),
        ('20000824/2300', '2000-08-24 23:00:00.00'),
        ('20000824/0102', '2000-08-24 01:02:00.00'),
        ('20000824', '2000-08-24 00:00:00.00'),
        ('20000824/020301', '2000-08-24 02:03:01.00'),
        ('20000824 020301', '2000-08-24 02:03:01.00'),
        ('-20000824 020301', '-2000-08-24 02:03:01.00'),
        ('20000824T020301', '2000-08-24 02:03:01.00'),
        ('20000824 020301', '2000-08-24 02:03:01.00'),
        ('2000-08-24 02:03:01.00', '2000-08-24 02:03:01.00'),
        ('T020311', '%s 02:03:11.00' % t.date),
        ('2003-12-9', '2003-12-09 00:00:00.00'),
        ('03-12-9', '2003-12-09 00:00:00.00'),
        ('003-12-9', '0003-12-09 00:00:00.00'),
        ('0003-12-9', '0003-12-09 00:00:00.00'),
        ('2003-1-9', '2003-01-09 00:00:00.00'),
        ('03-1-9', '2003-01-09 00:00:00.00'),
        ('003-1-9', '0003-01-09 00:00:00.00'),
        ('0003-1-9', '0003-01-09 00:00:00.00'),

        # US formats
        ('06/11/94 08:49:37', '1994-06-11 08:49:37.00'),
        ('11/06/94 08:49:37', '1994-11-06 08:49:37.00'),
        ('9/23/2001', '2001-09-23 00:00:00.00'),
        ('9-23-2001', '2001-09-23 00:00:00.00'),
        ('9/6', '%s-09-06 00:00:00.00' % t.year),
        ('09/6', '%s-09-06 00:00:00.00' % t.year),
        ('9/06', '%s-09-06 00:00:00.00' % t.year),
        ('09/06', '%s-09-06 00:00:00.00' % t.year),
        ('9/6/2001', '2001-09-06 00:00:00.00'),
        ('09/6/2001', '2001-09-06 00:00:00.00'),
        ('9/06/2001', '2001-09-06 00:00:00.00'),
        ('09/06/2001', '2001-09-06 00:00:00.00'),
        ('9-6-2001', '2001-09-06 00:00:00.00'),
        ('09-6-2001', '2001-09-06 00:00:00.00'),
        ('9-06-2001', '2001-09-06 00:00:00.00'),
        ('09-06-2001', '2001-09-06 00:00:00.00'),
        ('2002/05/28 13:10:56.1147 GMT+2', '2002-05-28 13:10:56.11'),
        ('1970/01/01', '1970-01-01 00:00:00.00'),
        ('20021025 12:00 PM', '2002-10-25 12:00:00.00'),
        ('20021025 12:30 PM', '2002-10-25 12:30:00.00'),
        ('20021025 12:00 AM', '2002-10-25 00:00:00.00'),
        ('20021025 12:30 AM', '2002-10-25 00:30:00.00'),
        ('20021025 1:00 PM', '2002-10-25 13:00:00.00'),
        ('20021025 2:00 AM', '2002-10-25 02:00:00.00'),
        ('Thursday, February 06, 2003 12:40 PM', '2003-02-06 12:40:00.00'),
        ('Mon, 18 Sep 2006 23:03:00', '2006-09-18 23:03:00.00'),

        # European formats
        ('6.11.2001, 08:49:37', '2001-11-06 08:49:37.00'),
        ('06.11.2001, 08:49:37', '2001-11-06 08:49:37.00'),
        ('06.11. 08:49:37', '%s-11-06 08:49:37.00' % t.year),
        #('21/12/2002', '2002-12-21 00:00:00.00'),
        #('21/08/2002', '2002-08-21 00:00:00.00'),
        #('21-08-2002', '2002-08-21 00:00:00.00'),
        #('13/01/03', '2003-01-13 00:00:00.00'),
        #('13/1/03', '2003-01-13 00:00:00.00'),
        #('13/1/3', '2003-01-13 00:00:00.00'),
        #('13/01/3', '2003-01-13 00:00:00.00'),

        # Time only formats
        ('01:03', '%s 01:03:00.00' % t.date),
        ('01:03:11', '%s 01:03:11.00' % t.date),
        ('01:03:11.50', '%s 01:03:11.50' % t.date),
        ('01:03:11.50 AM', '%s 01:03:11.50' % t.date),
        ('01:03:11.50 PM', '%s 13:03:11.50' % t.date),
        ('01:03:11.50 a.m.', '%s 01:03:11.50' % t.date),
        ('01:03:11.50 p.m.', '%s 13:03:11.50' % t.date),

        # Invalid formats
        ('6..2001, 08:49:37', '%s 08:49:37.00' % t.date),
        ('9//2001', 'ignore'),
        ('06--94 08:49:37', 'ignore'),
        ('20000824020301', 'ignore'),
        ('20-03 00:00:00.00', 'ignore'),
        ('9/2001', 'ignore'),
        ('9-6', 'ignore'),
        ('09-6', 'ignore'),
        ('9-06', 'ignore'),
        ('09-06', 'ignore'),
        ('20000824/23', 'ignore'),
        ('November 1994 08:49:37', 'ignore'),
        ('Nov. 94', 'ignore'),
        ('Mon, 18 Sep 2006 23:03:00 +1234567890', 'ignore'),

        ]

    # Add Unicode versions
    try:
        unicode
    except NameError:
        pass
    else:
        k = []
        for text, result in l:
            k.append((unicode(text), result))
        l.extend(k)

    for text, reference in l:
        try:
            value = DateTimeFromString(text)
        except:
            if reference is None:
                continue
            else:
                value = str(sys.exc_info()[1])
        valid_datetime = validateDateTimeString(text)
        valid_date = validateDateString(text)
        if str(value) != reference and \
           not reference == 'ignore':
            print 'Failed to parse "%s"' % text
            print '  expected: %s' % (reference or '<exception>')
            print '  parsed:   %s' % value
        elif _debug:
            print 'Parsed "%s" successfully' % text
        if _debug:
            if not valid_datetime:
                print '  "%s" failed date/time validation' % text
            if not valid_date:
                print '  "%s" failed date validation' % text

    et = DateTime.now()
    print 'done. (after %f seconds)' % ((et-t).seconds)

    ###

    print 'Testing DateTimeDelta Parser...'

    t = DateTime.now()
    l = [

        # Literal formats
        ('Sun Nov  6 08:49:37 1994', '08:49:37.00'),
        ('1 day, 8 hours, 49 minutes, 37 seconds', '1:08:49:37.00'),
        ('10 days, 8 hours, 49 minutes, 37 seconds', '10:08:49:37.00'),
        ('8 hours, 49 minutes, 37 seconds', '08:49:37.00'),
        ('49 minutes, 37 seconds', '00:49:37.00'),
        ('37 seconds', '00:00:37.00'),
        ('37.5 seconds', '00:00:37.50'),
        ('8 hours later', '08:00:00.00'),
        ('2 days', '2:00:00:00.00'),
        ('2 days 23h', '2:23:00:00.00'),
        ('2 days 23:57', '2:23:57:00.00'),
        ('2 days 23:57:13', '2:23:57:13.00'),
        ('', '00:00:00.00'),
        
        # ISO formats
        ('1994-11-06 08:49:37', '08:49:37.00'),
        ('10:08:49:37', '10:08:49:37.00'),
        ('08:49:37', '08:49:37.00'),
        ('08:49', '08:49:00.00'),
        ('-10:08:49:37', '-10:08:49:37.00'),
        ('-08:49:37', '-08:49:37.00'),
        ('-08:49', '-08:49:00.00'),
        ('- 10:08:49:37', '-10:08:49:37.00'),
        ('- 08:49:37', '-08:49:37.00'),
        ('- 08:49', '-08:49:00.00'),
        ('10:08:49:37.5', '10:08:49:37.50'),
        ('08:49:37.5', '08:49:37.50'),
        ('10:8:49:37', '10:08:49:37.00'),
        ('8:9:37', '08:09:37.00'),
        ('8:9', '08:09:00.00'),
        ('8', '00:00:00.00'),

        # Invalid formats
        #('', None),
        #('8', None),

        ]

    for text, reference in l:
        try:
            value = DateTimeDeltaFromString(text)
        except:
            if reference is None:
                continue
            else:
                value = str(sys.exc_info()[1])
        if str(value) != reference and \
           not reference == 'ignore':
            print 'Failed to parse "%s"' % text
            print '  expected: %s' % (reference or '<exception>')
            print '  parsed:   %s' % value
        elif _debug:
            print 'Parsed "%s" successfully' % text

    et = DateTime.now()
    print 'done. (after %f seconds)' % ((et-t).seconds)

    ###

    print 'Testing Time Parser...'

    t = DateTime.now()
    l = [

        # Standard formats
        ('08:49:37 AM', '08:49:37.00'),
        ('08:49:37 PM', '20:49:37.00'),
        ('12:00:00 AM', '00:00:00.00'),
        ('12:00:00 PM', '12:00:00.00'),
        ('8:09:37', '08:09:37.00'),
        ('8:09', '08:09:00.00'),
        
        # ISO formats
        ('08:49:37', '08:49:37.00'),
        ('08:49', '08:49:00.00'),
        ('08:49:37.5', '08:49:37.50'),
        ('08:49:37,5', '08:49:37.50'),
        ('08:09', '08:09:00.00'),

        # Invalid formats
        ('', None),
        ('8:9:37', 'XXX Should give an exception'),
        ('08:9:37', 'XXX Should give an exception'),
        ('8:9', None),
        ('8', None),

        ]

    for text, reference in l:
        try:
            value = TimeFromString(text, formats=('standard', 'iso'))
        except:
            if reference is None:
                continue
            else:
                value = str(sys.exc_info()[1])
        if str(value) != reference and \
           not reference == 'ignore':
            print 'Failed to parse "%s"' % text
            print '  expected: %s' % (reference or '<exception>')
            print '  parsed:   %s' % value
        elif _debug:
            print 'Parsed "%s" successfully' % text

    et = DateTime.now()
    print 'done. (after %f seconds)' % ((et-t).seconds)

if __name__ == '__main__':
    _test()
