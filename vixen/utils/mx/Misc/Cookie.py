""" Cookie -- Create sendable Netscape Cookies.

    Needs mxDateTime, mxURL and mxTextTools.

    Copyright (c) 2000, Marc-Andre Lemburg; All Rights Reserved.
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

"""
import string
from mx import DateTime,URL,TextTools

# Version number
__version__ = '1.2'

# Enable debugging output ?
_debug = 0

class Cookie:

    """ Cookie object, cf. Netscape's specification.
    """
    # Default values
    expires = None # temporary cookie
    path = '/'
    domain = ''
    secure = 0

    def __init__(self, name, value, expires=None, 
                 path=None, domain=None, secure=None):

        """ Create a Netscape cookie for name with the given value.

            If expires is given, the cookie will be a temporary cookie
            which expires after a certain amount of time.  expires may
            be given as integer (seconds relative to the current
            time), DateTime instance (absolute date/time) or
            RelativeDateTime instance (relative date/time to current
            time).

            path, domain, secure work according to the Netscape
            specification.
            
        """
        self.name = name
        self.value = value
        if expires is not None:
            # Long living cookie
            if isinstance(expires, DateTime.DateTimeType):
                self.expires = expires.gmtime()
            elif isinstance(expires, DateTime.RelativeDateTime):
                self.expires = DateTime.gmtime() + expires
            else:
                self.expires = DateTime.gmtime() + \
                               expires * DateTime.oneSecond
        if path:
            self.path = path
        if domain:
            self.domain = domain
        if secure:
            self.secure = 1

    def header_content(self,

                       now=DateTime.now,oneSecond=DateTime.oneSecond,
                       urlencode=URL.urlencode,join=string.join):

        # Add things that always have a value
        l = ['%s=%s' % (self.name, urlencode(self.value)),
             'path=%s' % self.path]
        if self.expires is not None:
            l.append('expires=%s' %\
                     self.expires.strftime('%a, %d %b %Y %H:%M:%S GMT'))
        if self.domain:
            l.append('domain=%s' % self.domain)
        if self.secure:
            l.append('secure')
        return join(l,';')

    # Alias for b/w compatibility:
    content = header_content

    def set_cookie_header(self):

        return 'Set-Cookie: %s\r\n' % self.header_content()

    # Alias for b/w compatibility:
    http_header = set_cookie_header

    def cookie_header(self,

                      urlencode=URL.urlencode):

        return 'Cookie: %s=%s\r\n' % (self.name, urlencode(self.value))

    def match(self, url, datetime=None):

        """ Return 1/0 depending on whether the Cookie matches
            the given url or not.

            datetime is used to check for expiration in case the
            Cookie is a temporary one. It defaults to the current
            date/time.

        """
        url = URL.URL(url)
        if self.expires is not None:
            if datetime is None:
                datetime = DateTime.now()
            if self.expires < datetime:
                if _debug:
                    print 'expired'
                return 0
        if TextTools.prefix(url.path, (self.path,)) is None:
            if _debug:
                print 'path does not match'
            return 0
        if TextTools.suffix(url.host, (self.domain,)) is None:
            if _debug:
                print 'domain does not match'
            return 0
        return 1

    def __str__(self):

        return 'Set-Cookie: %s' % self.header_content()

    def __repr__(self):

        return '<%s.%s "%s = %s" at 0x%x>' % ( 
            self.__class__.__module__,
            self.__class__.__name__, 
            self.name,
            self.value,
            id(self))

### Set-Cookie header parser

def CookieFromHeader(value,

                     splitat=TextTools.splitat,strip=string.strip,
                     charsplit=TextTools.charsplit,urldecode=URL.urldecode,
                     lower=TextTools.lower,
                     DateTimeFrom=DateTime.DateTimeFrom):

    """ Parse the value of an Set-Cookie header and return
        a corresponding Cookie instance.

    """
    items = map(strip, charsplit(value, ';'))
    c = Cookie('no-name', '')
    if not items:
        return c
    c.name, value = splitat(items[0], '=')
    c.value = urldecode(value)
    if len(items) > 1:
        for item in items[1:]:
            key, value = splitat(item,'=')
            key = lower(key)
            if key == 'path':
                c.path = value
            elif key == 'expires':
                try:
                    c.expires = DateTimeFrom(value)
                except ValueError:
                    pass
            elif key == 'domain':
                c.domain = value
            elif key == 'secure':
                c.secure = 1
    return c

# Alias for b/w compatibility
ParserCookie = CookieFromHeader

if __name__ == '__main__':

    c1 = Cookie('a', 'b',
                path='/mysite', expires=20, domain='egenix.com')
    print c1
    s1 = c1.header_content()
    c2 = ParserCookie(s1)
    print c2
    c3 = ParserCookie(s1[:-10])
    print c3
    print
    c4 = Cookie('a', 'b', expires=10)
    print c4.set_cookie_header()
    s1 = c4.header_content()
    c5 = ParserCookie(s1)
    print c5.cookie_header()

