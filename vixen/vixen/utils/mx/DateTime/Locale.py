# -*- coding: latin-1 -*-

""" Locale dependant formatting and parsing.

    XXX This module still has prototype status and is undocumented.

    XXX Check the spelling. 
    XXX Check the string format.

    Copyright (c) 1998-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.
"""

def _make_dict(*names):

    """ Helper to create a dictionary mapping indices to
        names and names to indices.
    """
    d = {}
    for i in range(len(names)):
        d[names[i]] = i
        d[i] = names[i]
    return d

class _TimeLocale:

    """ Base class for locale dependend formatting and parsing.
    """
    # Examples:
    Weekday = _make_dict('Monday','Tuesday','Wednesday','Thursday','Friday',
                         'Saturday','Sunday')
    Month = _make_dict(None,
             'January','February','March','April','May','June',
             'July','August','September','October','November','December')

    # Instance variables
    MonthNames = ()
    WeekdayNames = ()

    # Format string; this will be formatted using a dictionary providing
    # the entries: weekday, day, month, year, hour, minute, second
    longformat = '%(weekday)s, %(day)02i %(month)s %(year)04i, '\
                 '%(hour)02i:%(minute)02i:%(second)02i'

    def __init__(self):

        """ Init. the instance variables.
        """
        l = []
        for i in range(1,13):
            l.append(self.Month[i])
        self.MonthNames = tuple(l)

        l = []
        for i in range(7):
            l.append(self.Weekday[i])
        self.WeekdayNames = tuple(l)

    def str(self,d):
        
        """str(datetime)

           Return the given DateTime instance formatted according to
           the locale's convention. Timezone information is not
           presented.

        """
        return self.longformat % {
            'weekday': self.Weekday[d.day_of_week],
            'day': d.day,
            'month': self.Month[d.month],
            'litmonth': self.Month[d.month],
            'year': d.year,
            'hour': d.hour,
            'minute': d.minute,
            'second': d.second
            }

    # Alias
    ctime = str

# Singletons that implement the specific methods.

class English(_TimeLocale):
    Weekday = _make_dict('Monday','Tuesday','Wednesday','Thursday','Friday',
                            'Saturday','Sunday')
    Month = _make_dict(None,
             'January','February','March','April','May','June',
             'July','August','September','October','November','December')

    longformat = '%(weekday)s, %(month)s %(day)02i %(year)04i, '\
                 '%(hour)02i:%(minute)02i:%(second)02i'

English = English()

class German(_TimeLocale):
    Weekday = _make_dict('Montag','Dienstag','Mittwoch','Donnerstag',
                            'Freitag','Samstag','Sonntag')
    Month = _make_dict(None,
             'Januar','Februar','März','April','Mai','Juni',
             'Juli','August','September','Oktober','November','Dezember')

    longformat = '%(weekday)s, %(day)02i. %(month)s %(year)04i, '\
                 '%(hour)02i:%(minute)02i:%(second)02i'

German = German()

class French(_TimeLocale):
    Weekday = _make_dict('lundi','mardi','mercredi','jeudi',
                         'vendredi','samedi','dimanche')
    Month = _make_dict(None,
             'janvier','février','mars','avril','mai','juin',
             'juillet','août','septembre','octobre','novembre','décembre')

French = French()

class Spanish(_TimeLocale):
    Weekday = _make_dict('lunes','martes','miercoles','jueves','viernes',
                         'sabado','domingo')
    Month = _make_dict(None,
             'enero','febrero','marzo','abril','mayo','junio',
             'julio','agosto','septiembre','octubre','noviembre','diciembre')

Spanish = Spanish()

class Portuguese(_TimeLocale):
    Weekday = _make_dict('primeira feira', 'segunda feira','terceira feira',
                         'cuarta feira','quinta feira','sabado','domingo')
    Month = _make_dict(None,
             'janeiro','fevereiro','mar','abril','maio','junho',
             'julho','agosto','septembro','outubro','novembro','dezembro')

Portuguese = Portuguese()

###

def _test():

    import DateTime
    d = DateTime.now()
    for lang in (English,German,French,Spanish,Portuguese):
        print lang.__class__.__name__,':',lang.ctime(d)

if __name__ == '__main__':
    _test()
