""" Access routines to the NIST Network Time Services.

    This module allows you to access the UTC standard time bases via
    the Internet. The two functions localtime() and gmtime() will
    return accurate DateTime instances based on the NIST services.

    Since access through the Internet can be slow, the module also
    provides a way to calibrate the computer's clock and then have
    localtime() and gmtime() use the calibrated clock instead of the
    NIST services. To calibrate the two functions, call calibrate()
    with the number of calibration rounds you wish to apply.

    Copyright (c) 2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

"""
import socket # This module needs access to sockets !
import select # This module needs access to select !
import DateTime
import re,errno,exceptions,string,time

# Enable to produce debugging output
_debug = 0

# Timeout waiting for a daytime server to respond in seconds
TIMEOUT = 4.0

# Port numbers
try:
    DAYTIME_PORT = socket.getservbyname('daytime','tcp')
except socket.error:
    DAYTIME_PORT = 13

try:
    TIME_PORT = socket.getservbyname('time','tcp')
except socket.error:
    TIME_PORT = 37

# Known servers:
daytime_servers = ('time.nist.gov',
                   'time-a.nist.gov',
                   'time-b.nist.gov',
                   'time-nw.nist.gov',
                   'time-a.timefreq.bldrdoc.gov',
                   'time-b.timefreq.bldrdoc.gov',
                   'time-c.timefreq.bldrdoc.gov',
                   'utcnist.colorado.edu',
                   'utcnist1.reston.mci.net',
                   'nist1.datum.com',
                   )

# IP cache (XXX update these every now and then):
ip_cache = {'utcnist1.reston.mci.net': '204.70.131.13', 
            'time-a.nist.gov': '129.6.16.35', 
            'time-c.timefreq.bldrdoc.gov': '132.163.135.132',
            'time-a.timefreq.bldrdoc.gov': '132.163.135.130', 
            'nist1.datum.com': '209.0.72.7', 
            'time-nw.nist.gov': '131.107.1.10',
            'time-b.timefreq.bldrdoc.gov': '132.163.135.131', 
            'time-b.nist.gov': '129.6.16.36', 
            'time.nist.gov': '192.43.244.18',
            'utcnist.colorado.edu': '128.138.140.44'}

# XXX Not yet implemented...
# Use as fallback alternative for people behind firewalls:
daytime_http_servers = ('http://time-a.timefreq.bldrdoc.gov:14/',
                        )

### Errors

class Error(exceptions.StandardError):
    pass

### Parsers

# NIST daytime signal (JJJJ YR-MO-DA HH:MM:SS TT L H msADV UTC(NIST) OTM);
# see http://www.bldrdoc.gov/timefreq/service/nts.htm for details.
_daytime = ('(?P<mjd>\d+) '
            '(?P<date>\d+-\d\d-\d\d) '
            '(?P<hour>\d?\d):(?P<minute>\d\d):(?P<second>\d\d) '
            '(?P<dst>\d\d) '
            '(?P<leap>\d) '
            '(?P<health>\d) '
            '(?P<msadv>\d+(?:\.\d+)?) '
            '(?P<label>[\w()]+) '
            '(?P<otm>.)')
_daytimeRE = re.compile(_daytime)

def _parse_datetime(daytime):

    """ Returns a sequence representing the parsed information in daytime.

        The sequence has the following format:
          [mjd,date,hour,minute,second,dst,leap,health,msadv,label,otm]

        Numbers are converted to numbers. Entries may be None.

        Raises a ValueError is the daytime information cannot be
        parsed.

    """
    m = _daytimeRE.match(daytime)
    if not m:
        raise ValueError,'unknown daytime format: "%s"' % daytime
    groups = m.groups()
    l = list(groups)
    for i in range(len(l)):
        value = l[i]
        try:
            l[i] = int(value)
        except ValueError:
            try:
                 l[i] = float(value)
            except ValueError:
                pass
    return l

### Internal functions
    
def _connect(host, port, timeout):

    """ Connect to the given host and port and return a socket
        instance.

        timeout defines the number of seconds to wait for the
        connection to be established.

        In case no connection is possible, None is returned.

    """
    # Get IP address (and implement IP cache)
    hostname = host
    if ip_cache.has_key(hostname):
        host = ip_cache[hostname]
    else:
        try:
            host = socket.gethostbyname(hostname)
        except error:
            # Host not found or some other error
            return None
        else:
            ip_cache[hostname] = host
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Non-blocking mode
    s.setblocking(0)
    rc = -1
    for i in range(10):
        try:
            rc = s.connect_ex((host, DAYTIME_PORT))
        except socket.error, why:
            if _debug: print ' error: %s' % why
            return None
        if _debug: print ' received %s' % errno.errorcode.get(rc, rc)
        if rc in (errno.EAGAIN, errno.EWOULDBLOCK):
            # Try again
            continue
        if rc == errno.EINPROGRESS:
            # In progress... wait for connect
            r,w,e = select.select([],[s],[],timeout)
            if w:
                # Connect
                s.setblocking(1)
                try:
                    rc = s.connect_ex((host, DAYTIME_PORT))
                except socket.error, why:
                    # Should not happen, but does for e.g. 'host not found'
                    if _debug: print ' error: %s' % why
                    continue
                if _debug: print ' received %s' % errno.errorcode.get(rc, rc)
            else:
                if _debug: print ' timeout'
                rc = -1
        break
    else:
        return None
    if rc != 0:
        return None
    else:
        return s

def _read(socket, size, timeout,

          select=select.select):

    """ Read size at most bytes from socket.

        timeout defines the amount of time to wait for data to become
        available. In case this time is exceeded, None is returned.

    """
    r,w,e = select([socket],[],[],timeout)
    if r:
        return socket.recv(size)
    else:
        if _debug: print ' read timeout'
        return None

def _get_daytime(daytime_servers=daytime_servers, timeout=TIMEOUT,

                 strip=string.strip,_parse_datetime=_parse_datetime,
                 DateTimeFromMJD=DateTime.DateTimeFromMJD,
                 Time=DateTime.Time,time=time.time):

    """ Scans the given (NIST) daytime servers and returns a tuple:

        (DateTime instance representing the current UTC day time,
        ticks value of the time when the day time information was
        received)

        daytime_servers must be a list of servers providing the
        daytime protocol. They can be given by name or IP.

        timeout is used as timeout when connecting to each server.  It
        must be given in seconds and defaults to TIMEOUT. The total
        timeout depends on the number of servers listed in
        daytime_servers.

    """
    # We use the timeout value for connect and read, so make sure we
    # never spend more time on a single server
    timeout = timeout / 2.0
    if _debug: print 'Contacting NIST servers...'
    for host in daytime_servers:
        if _debug: print 'Trying server: %s' % host
        s = _connect(host, DAYTIME_PORT, timeout)
        if s:
            data = _read(s, 512, timeout)
            if data is None:
                continue
            daytime = strip(data)
            timestamp = time()
            s.close()
            if _debug: print ' read %s' % daytime
            try:
                daytime = _parse_datetime(daytime)
            except ValueError:
                continue
            # Check health
            if daytime[7] != 0:
                continue
            break
    else:
        raise Error,'could not get accurate daytime information'

    return (DateTimeFromMJD(daytime[0]) + \
            Time(daytime[2],daytime[3],daytime[4]-daytime[8]*0.001),
            timestamp)

### APIs for the current local and UTC time 

# Globals that inform about the current state of calibration
calibrated = 0          # Does calibration contain valid information ?
calibrating = 1         # Try to auto-calibrate whenever online, if true
calibration = 0.0       # Current calibration offset (NIST - CPU time)

# Internal globals needed for auto-calibration
_diffs = []
_min_diffs = 10

def utctime(nist_lookup=0,
    
            time=time.time,
            DateTimeDeltaFromSeconds=DateTime.DateTimeDeltaFromSeconds,
            utctime=DateTime.utctime,_diffs=_diffs):

    """ Returns the current UTC time as DateTime instance.

        Works must like the standard DateTime.now(), but tries to use
        the NIST time servers as time reference -- not only the
        computer's builtin clock.

        Note that the contructor may take several seconds to return in
        case no calibration was performed (see calibrate()). With
        calibration information, the computer's clock is used as
        reference and the offset to NIST time is compensated by the
        contructor.

        In case the NIST service is not reachable, the contructor
        falls back to using either the calibrated or uncalibrated
        computer's clock.

        Setting nist_lookup to false (default) will cause the
        contructor to prefer the calibrated CPU time over the
        expensive Internet queries. If it is true, then Internet
        lookups are always tried first before using the local clock. A
        value of 2 will cause an Error to be raised in case the NIST
        servers are not reachable.

        The constructor will use the NIST information for auto
        calibration, unless an explicit call to calibrate() takes care
        of this.

    """
    if nist_lookup or calibrating:
        try:
            if len(_diffs) >= _min_diffs:
                _update_calibration()
            nist,timestamp = _get_daytime()
            local = utctime()
            diff = (nist - local).seconds
            adj = time() - timestamp
            diff = diff - adj
            _diffs.append(diff)
            return nist - DateTimeDeltaFromSeconds(adj)
        except Error:
            if nist_lookup > 1:
                raise Error,'could not connect to NIST servers'
    return utctime(time()+calibration)

# Alias
gmtime=utctime

def localtime(nist_lookup=0,
    
              localtime=DateTime.localtime,utctime=utctime):

    """ Returns the current local time as DateTime instance.

        Same notes as for utctime().

    """
    return localtime(utctime(nist_lookup).gmticks())

# Alias
now = localtime

### Calibration APIs

def online():

    """ Return 1/0 depending on whether the NIST service is
        currently reachable or not.

        This function is expensive since it actually fetches a daytime
        packet from a NIST server.

    """
    try:
        _get_daytime()
    except Error:
        return 0
    else:
        return 1

def time_offset(iterations=10,

                utctime=DateTime.utctime,_get_daytime=_get_daytime,
                time=time.time):

    """ Returns the average offset of the computer's clock to the NIST
        time base in seconds.

        If you add the return value to the return value of
        time.time(), you will have a pretty accurate time base to use
        in your applications.

        Note that due to network latencies and the socket overhead,
        the calculated offset will include a small hopefully constant
        error.

        iterations sets the number of queries done to the NIST time
        base.  The average is taken over all queries.

    """
    diffs = []
    for i in range(iterations):
        nist,timestamp = _get_daytime()
        local = utctime()
        diff = (nist - local).seconds - (time()-timestamp)
        diffs.append(diff)
    sum = 0
    for diff in diffs:
        sum = sum + diff
    return sum / len(diffs)

def set_calibration(calibration_offset):

    """ Sets the calibration to be use by localtime() and utctime().

        This also sets the global calibrated to 1 and disables auto
        calibration.

    """
    global calibration,calibrated,calibrating
    calibration = calibration_offset
    calibrated = 1
    calibrating = 0

def calibrate(iterations=20):

    """ Calibrates the localtime() and gmtime() functions supplied
        in this module (not the standard ones in DateTime !).

        Uses the NIST time service as time base. The computer must
        have an active internet connection to be able to do
        calibration using the NIST servers.

        iterations sets the number of round to be done.

        Note: This function takes a few seconds to complete. For long
        running processes you should recalibrate every now and then
        because the system clock tends to drift (usually more than the
        hardware clock in the computer).

    """
    try:
        calibration = time_offset(iterations)
    except (ValueError,Error):
        pass
    else:
        set_calibration(calibration)

def _update_calibration(use_last=_min_diffs,

                        _diffs=_diffs):

    """ Updates the calibration from the last use_last entries in 
        the global _diffs.

        _diffs is being updated with every call to the two current
        time APIs that goes out and gets genuine information from
        NIST.

        After calibration the entries in _diffs are cleared. This
        function is automatically called by utctime() and localtime()
        when needed.

    """
    global calibration,calibrated,calibrating
    sum = 0
    diffs = _diffs[-use_last:]
    for diff in diffs:
        sum = sum + diff
    calibration = sum / len(diffs)
    _diffs[:] = []
    set_calibration(calibration)

def reset_auto_calibration():

    """ Enables and resets the auto calibration for a new round.

        This does not clear possibly available calibration
        information, so the two time APIs will continue to revert to
        the calibrated clock in case no connection to the NIST servers
        is possible.

        Auto calibration is on per default when the module is
        imported.

    """
    global calibrating
    _diffs[:] = []
    calibrating = 1

# Alias
enable_auto_calibration = reset_auto_calibration

def disable_auto_calibration():

    """ Turns auto calibration off.
    """
    global calibrating
    calibrating = 0

