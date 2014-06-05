


import os
import datetime
import threading
from pymel.all import *
try:
    from maya.utils import executeInMainThreadWithResult
except:
    executeInMainThreadWithResult = None


class Timer(threading.Thread):
    def __init__(self, interval, function, args=[], kwargs={}, repeat=True):
        self.interval = interval
        self.function = function
        self.repeat = repeat
        self.args = args
        self.kwargs = kwargs
        self.event = threading.Event()
        threading.Thread.__init__(self)

    def run(self):
        def _mainLoop():
            self.event.wait(self.interval)
            if not self.event.isSet():
                if executeInMainThreadWithResult:
                    executeInMainThreadWithResult(self.function, *self.args, **self.kwargs)
                else:
                    self.function(*self.args, **self.kwargs)
        if self.repeat:
            while not self.event.isSet():
                _mainLoop()
        else:
            _mainLoop()
            self.stop()

    def start(self):
        self.event.clear()
        threading.Thread.start(self)

    def stop(self):
        self.event.set()
        threading.Thread.__init__(self)


def which(program):
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    def ext_candidates(fpath):
        yield fpath
        for ext in os.environ.get("PATHEXT", "").split(os.pathsep):
            yield fpath + ext

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            for candidate in ext_candidates(exe_file):
                if is_exe(candidate):
                    return candidate
    return None


def prettydate(d, T=lambda x: x):
    try:
        dt = datetime.datetime.now() - d
    except:
        return ''
    if dt.days >= 2 * 365:
        return T('%d years ago') % int(dt.days / 365)
    elif dt.days >= 365:
        return T('1 year ago')
    elif dt.days >= 60:
        return T('%d months ago') % int(dt.days / 30)
    elif dt.days > 21:
        return T('1 month ago')
    elif dt.days >= 14:
        return T('%d weeks ago') % int(dt.days / 7)
    elif dt.days >= 7:
        return T('1 week ago')
    elif dt.days > 1:
        return T('%d days ago') % dt.days
    elif dt.days == 1:
        return T('1 day ago')
    elif dt.seconds >= 2 * 60 * 60:
        return T('%d hours ago') % int(dt.seconds / 3600)
    elif dt.seconds >= 60 * 60:
        return T('1 hour ago')
    elif dt.seconds >= 2 * 60:
        return T('%d minutes ago') % int(dt.seconds / 60)
    elif dt.seconds >= 60:
        return T('1 minute ago')
    elif dt.seconds > 1:
        return T('%d seconds ago') % dt.seconds
    elif dt.seconds == 1:
        return T('1 second ago')
    else:
        return T('now')


if __name__ == '__main__':
    #print which('mayapy')
    print prettydate('0001-02-03 00:00:00')
