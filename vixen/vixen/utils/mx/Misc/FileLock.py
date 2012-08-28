#! /usr/bin/python -u

""" FileLock - Implements a file lock mechanism that does not depend
               on fcntl.

    Copyright (c) 1997-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2008, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

"""
from mx.Misc.ExitFunctions import ExitFunctions
import os,exceptions,time,string

# Version
__version__ = '1.0'

# Get fully qualified hostname
def _fqhostname(hostname=None,default=('localhost','127.0.0.1')):

    """ Returns fully qualified (hostname, ip) for the given hostname.

        If hostname is not given, the default name of the local host
        is chosen.

        Defaults to default in case an error occurs while trying to
        determine the data.

    """
    try:
        import socket
    except ImportError:
        return default
    try:
        if hostname is None:
            hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        hostname = socket.gethostbyaddr(ip)[0]
    except socket.error:
        return default
    else:
        return hostname,ip

hostname,ip = _fqhostname()

### Errors

class Error(exceptions.StandardError):
    pass

# Backward compatibility:
FileLockError = Error

### File lock using symbolic links

class SymbolicFileLock:

    """ Implements a file lock mechanism.

        The base class implements the locking mechanism using symbolic
        links.

        Note that since the mechanism does not use file system
        function calls this may not always work in the desired
        way.

        The lock is acquired per process, not per thread.

        Instancevariables:
         filename - file the lock applies to
         lockfilename - name of the lock file
         locked - indicator if the lock is in position (1) or not (0)

    """
    # Do we hold the lock ?
    locked = 0

    # Lock timeout in seconds (0 = never)
    locktimeout = 0

    def __init__(self, filename):

        self.filename = filename
        self.lockfilename = filename + '.locked'
        self.locked = 0
        # Avoid deadlocks
        ExitFunctions.register(self.unlock)

    def __del__(self):

        if self.locked:
            self.unlock(0)
        try:
            ExitFunctions.deregister(self.unlock)
        except:
            pass

    def lock(self,timeout=500,sleeptime=0.0001,

             sleep=time.sleep,Error=Error,time=time.time,error=os.error,
             hostname=hostname,ip=ip):

        """ Try to lock the file for this process, waiting 
            timeout ms if necessary.

            Raises an exception if a timeout occurs. Multiple locking
            by the same process is not an error. 

            Note that a non existent path to the file will also result
            in a timeout.

            If the lock is held by a process running on our host, a
            timeout will first invoke a check of the locking
            process. If it is not alive anymore, the lock is removed
            and granted to the current process.
            
        """
        if self.locked:
            return
        lockfilename = self.lockfilename
        lockinfo = '%s:%i' % (hostname,os.getpid())
        stop = time() + timeout * 0.001
        # Localize these for speed
        islink=os.path.islink
        makelink=os.symlink
        readlink=os.readlink
        while 1:
            # These are rather time-critical
            if not islink(lockfilename):
                try:
                    makelink(lockinfo,lockfilename)
                except error:
                    # A non existent path will result in a time out.
                    pass
                else:
                    break
            sleep(sleeptime)
            if time() > stop:
                # Timeout... check whether it's a valid lock
                if not self.validate_lock():
                    continue
                host, locking_pid = self.lock_info()
                raise Error,\
                      'file "%s" is locked by process %s:%i' % \
                      (self.filename, host, locking_pid)
        self.locked = 1

    def unlock(self,sleeptime=0.0001,

               unlink=os.unlink,Error=Error,sleep=time.sleep,error=os.error):

        """ Release the lock, letting other processes using this
            mechanism access the file. 

            Multiple unlocking is not an error. Raises an exception if
            the lock file was already deleted by another process.

            After having unlocked the file the process sleeps for
            sleeptime seconds to give other processes a chance to
            acquire the lock too. If the lock will only be used every
            once in a while by the process, it is safe to set it to 0.

        """
        if not self.locked: 
            return
        self.locked = 0
        try:
            unlink(self.lockfilename)
        except error:
            raise Error,'file lock "%s" is already gone' % \
                  self.lockfilename
        # Give other processes a chance too
        if sleeptime:
            sleep(sleeptime)
        return 1

    def has_lock(self):

        """ Returns the current state of the file lock: 1 - a lock
            exists, 0 - no lock exists.

            Note that in case a lock exists, this lock is not checked
            for being valid.
        
        """
        if self.locked:
            return 1
        if os.path.islink(self.lockfilename):
            return 1
        return 0

    def lock_info(self):

        """ Returns a tuple (hostname, PID integer) indicating the
            host and process id currently holding the lock.

            An Error is raised if no lock exists.

        """
        try:
            host,locking_pid = string.split(os.readlink(self.lockfilename),':')
        except os.error,why:
            raise Error,\
                  'file "%s" could not be locked: %s' % \
                  (self.filename,why)
        locking_pid = int(locking_pid)
        return (host, locking_pid)

    def validate_lock(self):

        """ Validates a lock on the file and return 1 for a valid lock,
            0 for an invalid one.

            Note that it is only possible to check for valid locks
            which are owned by the same host. This method removes any
            invalid locks it may find.

            An Error is raised if no lock exists.

        """
        # Check for lock timeouts
        if self.locktimeout:
            ctime = self.lock_time()
            if ctime < time.time() - self.locktimeout:
                # Timed out
                try:
                    os.unlink(self.lockfilename)
                except os.error, why:
                    # We probably don't have proper permissions.
                    return 1
                else:
                    return 0

        # Check process
        host, locking_pid = self.lock_info()
        if host != hostname:
            # Ok, then compare via IPs
            other_ip = _fqhostname(host, default=('???','???'))[1]
            samehost = (ip == other_ip)
        else:
            samehost = 1
        if samehost:
            # Check whether the locking process is still alive
            try:
                os.kill(locking_pid, 0)
            except os.error, why:
                # It's gone without a trace...
                try:
                    os.unlink(self.lockfilename)
                except os.error:
                    # We probably don't have proper permissions.
                    pass
                else:
                    return 0

        return 1

    def lock_time(self):

        """ Returns a Unix time value indicating the time when the
            current lock was created.

            An Error is raised if no lock exists.

        """
        try:
            ctime = os.lstat(self.lockfilename)[9]
        except os.error, why:
            raise Error,\
                  'could not read file lock info for "%s": %s' % \
                  (self.filename, why)
        return ctime

    def remove_lock(self,

                    unlink=os.unlink):

        """ Remove any existing lock on the file.
        """
        self.locked = 0
        try:
            unlink(self.lockfilename)
        except:
            pass

    def __repr__(self):

        return '<%s for "%s" at %x>' % (self.__class__.__name__,
                                        self.filename,
                                        id(self))

# Alias
BaseFileLock = SymbolicFileLock

### File lock using directories

class DirectyFileLock(BaseFileLock):

    """ This class implements a file lock mechanism that uses
        temporary directories for locking.

        See FileLock for documentation of the various methods.

        Thanks to Thomas Heller for this idea !

    """

    def lock(self,timeout=500,sleeptime=0.0001,

             sleep=time.sleep,Error=Error,time=time.time,error=os.error,
             hostname=hostname,ip=ip,mkdir=os.mkdir):

        if self.locked:
            return
        lockfilename = self.lockfilename
        lockinfo = '%s:%i' % (hostname,os.getpid())
        stop = time() + timeout * 0.001
        while 1:
            # These are rather time-critical
            try:
                mkdir(lockfilename)
            except error:
                # A non existent path will result in a time out.
                pass
            else:
                break
            sleep(sleeptime)
            if time() > stop:
                # Timeout... check whether it's a valid lock
                if not self.validate_lock():
                    continue
                raise Error,\
                      'file "%s" is currently locked' % self.filename
        self.locked = 1

    def unlock(self,sleeptime=0.0001,

               rmdir=os.rmdir,Error=Error,sleep=time.sleep,error=os.error):

        if not self.locked: 
            return
        self.locked = 0
        try:
            rmdir(self.lockfilename)
        except error:
            raise Error,'file lock "%s" is already gone' % \
                  self.lockfilename
        # Give other processes a chance too
        if sleeptime:
            sleep(sleeptime)
        return 1

    def has_lock(self):

        if self.locked:
            return 1
        if os.path.isdir(self.lockfilename):
            return 1
        return 0

    def validate_lock(self):

        # Check for lock timeouts
        if self.locktimeout:
            ctime = self.lock_time()
            if ctime < time.time() - self.locktimeout:
                # Timed out
                try:
                    os.rmdir(self.lockfilename)
                except os.error, why:
                    # We probably don't have proper permissions.
                    return 1
                else:
                    return 0

        return 1

    def lock_info(self):

        """ Locking info is not available for DirectyFileLocks.

            A TypeError is raised in case this method is called.

        """
        raise TypeError, \
              '.lock_info() is not implemented for DirectyFileLocks'

    def lock_time(self):

        try:
            ctime = os.stat(self.lockfilename)[9]
        except os.error, why:
            raise Error,\
                  'could not read file lock info for "%s": %s' % \
                  (self.filename, why)
        return ctime

    def remove_lock(self,

                    rmdir=os.rmdir):

        self.locked = 0
        try:
            rmdir(self.lockfilename)
        except:
            pass

### Generic file lock mechanism

if hasattr(os, 'symlink'):
    FileLock = SymbolicFileLock
else:
    FileLock = DirectyFileLock

def _test():
    
    #lock = SymbolicFileLock('test-lock')
    #lock = DirectyFileLock('test-lock')
    lock = FileLock('test-lock')
    starttime = time.time()
    try:
        for i in range(10000):
            print '%i\r'%i,
            lock.lock()
            time.sleep(i/100000.0)
            lock.unlock()
            #time.sleep(i/100000.0)
    except KeyboardInterrupt:
        lock.unlock()
    totaltime = time.time() - starttime
    print '%i lock/release cycles in %5.2f sec. = %i cycles/sec.' % \
          (i,  totaltime, i / totaltime)

if __name__ == '__main__':
    _test()
