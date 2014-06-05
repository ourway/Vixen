""" Calculate moveable feasts that depend on the date of Easter Sunday.

    Copyright (c) 1998-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.
"""

import DateTime

_eastereggs = {}

def EasterSunday(year):

    """EasterSunday(year)

    Return a DateTime instance pointing to Easter Sunday of the given
    year. Note: it must be given *with* century.
    
    Based on the algorithm presented in the Calendar FAQ by Claus
    Tondering (http://www.pip.dknet.dk/~pip10160/calendar.html), which
    in return is based on the algorithm of Oudin (1940) as quoted in
    "Explanatory Supplement to the Astronomical Almanac", P. Kenneth
    Seidelmann, editor."""

    if _eastereggs.has_key(year):
        return _eastereggs[year]
    G = year % 19
    C = year/100
    H = (C - C/4 - (8*C+13)/25 + 19*G + 15) % 30
    I = H - (H/28)*(1 - (H/28)*(29/(H + 1))*((21 - G)/11))
    J = (year + year/4 + I + 2 - C + C/4) % 7
    L = I - J
    month = 3 + (L + 40)/44
    day = L + 28 - 31*(month/4)
    _eastereggs[year] = d = DateTime.DateTime(year,month,day)
    return d

Ostersonntag = EasterSunday
DimanchePaques = EasterSunday

# Some common feasts derived from Easter Sunday

def CarnivalMonday(year):

    return EasterSunday(year) - 48

Rosenmontag = CarnivalMonday

def MardiGras(year):

    return EasterSunday(year) - 47

def AshWednesday(year):

    return EasterSunday(year) - 46

Aschermittwoch = AshWednesday
MercrediCendres = AshWednesday

def PalmSunday(year):

    return EasterSunday(year) - 7

Palmsonntag = PalmSunday
DimancheRameaux = PalmSunday

def EasterFriday(year):

    return EasterSunday(year) - 2

GoodFriday = EasterFriday
Karfreitag = EasterFriday
VendrediSaint = EasterFriday

def EasterMonday(year):

    return EasterSunday(year) + 1

Ostermontag = EasterMonday
LundiPaques = EasterMonday

def Ascension(year):

    return EasterSunday(year) + 39

Himmelfahrt = Ascension

def Pentecost(year):

    return EasterSunday(year) + 49

WhitSunday = Pentecost
Pfingstsonntag = WhitSunday
DimanchePentecote = WhitSunday

def WhitMonday(year):

    return EasterSunday(year) + 50

Pfingstmontag = WhitMonday
LundiPentecote = WhitMonday

def TrinitySunday(year):

    return EasterSunday(year) + 56

def CorpusChristi(year):

    return EasterSunday(year) + 60

Fronleichnam = CorpusChristi
FeteDieu = CorpusChristi

def _test():

    import ISO,ARPA
    print 'Easter Sunday for the next few years'
    for year in range(2000, 2038):
        easter = EasterSunday(year)
        mark = easter.month == 4 and easter.day == 6
        print 'ISO:',ISO.str(easter),'  ARPA:', ARPA.str(easter), ' *' * mark

if __name__ == '__main__':
    _test()
