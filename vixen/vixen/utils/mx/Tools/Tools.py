""" Tools - Add-ons for Python written in C for performance.

    Copyright (c) 2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

"""#"

# Import C extensions' symbols
from mxTools import *
from mxTools import __version__

# Needed Python imports
import operator,types,string,time,sys,os,re

#############################################################################
#
# Experimental function prototypes written in Python
#

def sortedby(sequence,*indices):

    """ sortedby(sequence,*indices)
    
        Returns a list representing the sequence sorted ascending by
        the fields pointed to by the additional arguments
        (indices). sequence must be at least two-dimensional, e.g. a
        list of tuples.

    """
    if len(sequence) == 0:
        return []
    x = apply(tuples,tuple(extract(lists(sequence),indices))+(sequence,))
    x.sort()
    return map(get,x,(-1,)*len(x))

def projection(sequence,*indices):

    """ projection(sequence,*indices)

        Experimental function that extracts columns from tables
        (sequence of sequences). If only one index is given, a list of
        all elements in that dimension is returned. For more indices,
        the list will contain tuples with entries for each given
        dimension.

    """
    if len(sequence) == 0:
        return []
    if len(indices) == 1:
        return lists(sequence)[indices[0]]
    else:
        return tuples(extract(lists(sequence),indices))

def frange(x,y,ticks):

    """frange(x,y,ticks)

       Returns a list of ticks equidistant floating point values from
       the interval [x,y] such that the first is equal to x and the
       last equal to y.

    """
    l = [x] * ticks
    fticks = float(ticks-1)
    diff = y - x
    for i,value in irange(l):
        l[i] = value + diff*(i/fticks)
    return l


def issequence(obj,

               isSequenceType=operator.isSequenceType,
               InstanceType=types.InstanceType):

    """issequence(obj)

       Returns 1 iff obj defines the sequence protocol, o
       otherwise. For instances at least __getitem__ must be defined.
    
    """
    rc = isSequenceType(obj)
    if rc and type(obj) == InstanceType:
        rc = hasattr(obj,'__getitem__')
    return rc

def defined(name):

    """ defined(name)

        Return 1/0 depending on whether name is a defined symbol
        in the caller's namespace.

    """
    frame = sys.cur_frame(1)
    # Look up the symbol name
    ok = frame.f_locals.has_key(name) or \
         frame.f_globals.has_key(name) or \
         frame.f_builtins.has_key(name)
    del frame
    return ok

def acqchain(obj):

    """ acqchain(obj)

        Returns a list of object representing the acquisition
        chain that the new builtin acquire() would scan.

        The order is top to bottom, with obj always being the
        last entry in the list.

    """
    l = []
    append = l.append
    while obj:
        append(obj)
        obj = obj.baseobj
    l.reverse()
    return l

# Truth constants
True = (1==1)
False = (1==0)

def reval(codestring,locals=None,

          eval=eval):

    """ Restricted execution eval().

        After a suggestion by Tim Peters on comp.lang.python.  locals
        can be given as local namespace to use when evaluating the
        codestring.

    """
    if locals is not None:
        return eval(codestring,{'__builtins__':{}},locals)
    else:
        return eval(codestring,{'__builtins__':{}})

def docstring():

    """ Returns the doc string of the calling function.

        Note that this only works for Python functions since it relies
        on the code object of the calling function.

    """
    return cur_frame(1).f_code.co_consts[0]

# Aliases for some of the APIs
nonzero = truth

# XXX This should probably be moved to mx.TextTools...

_hexcode = ("00", "01", "02", "03", "04", "05", "06", "07", "08", "09",
"0a", "0b", "0c", "0d", "0e", "0f", "10", "11", "12", "13", "14",
"15", "16", "17", "18", "19", "1a", "1b", "1c", "1d", "1e", "1f",
"20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "2a",
"2b", "2c", "2d", "2e", "2f", "30", "31", "32", "33", "34", "35",
"36", "37", "38", "39", "3a", "3b", "3c", "3d", "3e", "3f", "40",
"41", "42", "43", "44", "45", "46", "47", "48", "49", "4a", "4b",
"4c", "4d", "4e", "4f", "50", "51", "52", "53", "54", "55", "56",
"57", "58", "59", "5a", "5b", "5c", "5d", "5e", "5f", "60", "61",
"62", "63", "64", "65", "66", "67", "68", "69", "6a", "6b", "6c",
"6d", "6e", "6f", "70", "71", "72", "73", "74", "75", "76", "77",
"78", "79", "7a", "7b", "7c", "7d", "7e", "7f", "80", "81", "82",
"83", "84", "85", "86", "87", "88", "89", "8a", "8b", "8c", "8d",
"8e", "8f", "90", "91", "92", "93", "94", "95", "96", "97", "98",
"99", "9a", "9b", "9c", "9d", "9e", "9f", "a0", "a1", "a2", "a3",
"a4", "a5", "a6", "a7", "a8", "a9", "aa", "ab", "ac", "ad", "ae",
"af", "b0", "b1", "b2", "b3", "b4", "b5", "b6", "b7", "b8", "b9",
"ba", "bb", "bc", "bd", "be", "bf", "c0", "c1", "c2", "c3", "c4",
"c5", "c6", "c7", "c8", "c9", "ca", "cb", "cc", "cd", "ce", "cf",
"d0", "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d9", "da",
"db", "dc", "dd", "de", "df", "e0", "e1", "e2", "e3", "e4", "e5",
"e6", "e7", "e8", "e9", "ea", "eb", "ec", "ed", "ee", "ef", "f0",
"f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "fa", "fb",
"fc", "fd", "fe", "ff")

def hexencode(data,

              hexcode=_hexcode,ord=ord,join=string.join):

    """ HEX encode a data string.

        Encoding is done character per character using two byte
        lower-case HEX characters.

    """
    l = []
    append = l.append
    for c in data:
        append(hexcode[ord(c)])
    return join(l,'')


#############################################################################
#
# Utilities written in Python
#

def scanfiles(files, dir=None, levels=0, filefilter=None,

              filedict=None,join=os.path.join,isdir=os.path.isdir,
              listdir=os.listdir):

    """ Build a list of filenames starting with the filenames and
        directories given in files.

        The filenames in are made absolute relative to dir. dir
        defaults to the current working directory if not given.

        If levels is greater than 0, directories in the files list are
        recursed into up the given number of levels.

        If filefilter is given, as re match object, then all filenames
        (the absolute names) are matched against it. Filenames which
        do not match the criteria are removed from the list.

        Note that directories are not included in the resulting list.
        All filenames are non-directories.

    """
    if not files:
        return files

    # Make file names absolute and eliminate duplicates
    if dir is None:
        dir = os.getcwd()
    if filedict is None:
        filedict = {}
        recursing = 0
    else:
        recursing = 1
    dirs = []
    for file in files:
        abspath = join(dir, file)
        if isdir(abspath):
            dirs.append(abspath)
        elif filefilter is not None and \
             filefilter.match(abspath) is None:
            continue
        else:
            filedict[abspath] = 1

    # Recurse into subdirs
    if levels > 0:
        for dir in dirs:
            scanfiles(listdir(dir), dir, levels+1, filefilter, filedict)

    # Fast path: don't return file list inside recursion
    if not recursing:
        return filedict.keys()

class DictScan:

    """ Forward iterator for Python dictionaries.

        Note that no precaution is taken to insure that the dictionary
        is not modified in between calls to the __getitem__ method. It
        is the user's responsibility to ensure that the dictionary is
        neither modified, nor changed in size, since this would result
        in skipping entries or double occurance of items in the scan.

        The iterator inherits all methods from the underlying
        dictionary for convenience.

    """
    def __init__(self,dictionary):

        self.dictionary = dictionary
        self.position = 0

    def reset(self):

        """ Resets the iterator to its initial position.
        """
        self.position = 0

    def __getitem__(self,index,

                    dictscan=dictscan):

        """ "for x in iterator" interface.

            Note: for loops are cancelled by raising an IndexError.

        """
        # This may raise an IndexError which we *don't* catch
        # on purpose
        k,v,self.position = dictscan(self.dictionary,self.position)
        return k,v

    def __getattr__(self,name,

                    getattr=getattr):

        """ Inherit all other methods from the underlying dictionary.
        """
        return getattr(self.dictionary,name)

# Alias
DictItems = DictScan

_integerRE = re.compile('\s*(-?\d+)\s*$')
_integerRangeRE = re.compile('\s*(-?\d+)\s*-\s*(-?\d+)\s*$')

def srange(s,

           split=string.split,integer=_integerRE,
           integerRange=_integerRangeRE):

    """ Converts a textual representation of integer numbers and ranges
        to a Python list.

        Supported formats: 2,3,4,2-10,-1 - -3, 5 - -2

        Values are appended to the created list in the order specified
        in the string.

    """
    l = []
    append = l.append
    for entry in split(s,','):
        m = integer.match(entry)
        if m:
            append(int(m.groups()[0]))
            continue
        m = integerRange.match(entry)
        if m:
            start,end = map(int,m.groups())
            l[len(l):] = range(start,end+1)
    return l

def fqhostname(hostname=None, ip=None):

    """ Tries to return the fully qualified (hostname, ip) for the
        given hostname.

        If hostname is None, the default name of the local host is
        chosen. ip then defaults to '127.0.0.1' if not given.

        The function modifies the input data according to what it
        finds using the socket module. If that doesn't work the input
        data is returned unchanged.

    """
    try:
        import socket
    except ImportError:
        if hostname is None:
            hostname = os.environ.get('HOSTNAME',None)
        if ip is None:
            ip = '127.0.0.1'
        return hostname, ip
    try:
        if hostname is None:
            if ip is None:
                ip = '127.0.0.1'
            hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        hostname = socket.gethostbyaddr(ip)[0]
    except socket.error:
        pass
    return hostname,ip

def splitdomain(hostname=None):

    """ Tries to determine the domain name of the given hostname and
        returns a tuple (host, domain).

        If hostname is not given, the default name of the local host
        is chosen as reference.

    """
    hostname, ip = fqhostname(hostname)
    l = string.split(hostname, '.', 1)
    if len(l) == 1:
        return (hostname, '')
    return tuple(l)

def username(default=''):

    """ Return the user name of the user running the current process.

        If no user name can be determined, default is returned.

    """
    import getpass
    try:
        return getpass.getuser()
    except:
        return default

######################################################################
#
# Old lib/Tools.py module...
#
# XXX Some of these functions are obsolete.
#

def tb_lineno(tb):

    """ Calculate the correct line number of the
        traceback given in tb (even with -O on)
    """
    c = tb.tb_frame.f_code
    tab = c.co_lnotab
    line = c.co_firstlineno
    stopat = tb.tb_lasti
    addr = 0
    for i in range(0,len(tab),2):
        addr = addr + ord(tab[i])
        if addr > stopat:
            break
        line = line + ord(tab[i+1])
    return line

def execpyc(filename,globals=None,locals=None):

    """ Execute a byte compiled file filename in globals, locals 
    """
    import marshal
    f = open(filename,'rb')
    f.read(8) # skip header (id check omitted)
    code = marshal.load(f)
    exec code in globals,locals
    
def loadpyc(filename):

    """ Load the code from a byte compiled file filename and return it
        as code object.
    """
    import marshal
    f = open(filename,'rb')
    f.read(8) # skip header (id check omitted)
    return marshal.load(f)

def import_code(name,code):

    """ Imports a code object as module name.

        Returns the previously registered module in case the module
        name was already imported. name has to be the full package
        name (pkg.pkg.mod) for the module; package local names are not
        supported and will result in top-level modules to be created.

    """
    import imp,sys
    if sys.modules.has_key(name):
        return sys.modules[name]
    m = imp.new_module(name)
    exec code in m.__dict__
    sys.modules[name] = m
    return m

def pairs2tuples(tab):

    """ Format a sequence of adjacent pairs into a list
        of 2-tuples, e.g. 'abcdef' gives [('a','b'),('c','d'),
        ('e','f')]
    """
    l = map( None, tab[:-1], tab[1:], (1,0)*(len(tab)/2) )
    l = filter( lambda x:x[2], l)
    l = map( lambda x:x[:2], l)
    return l

def exec_frame(level=0,
               
               exc_info=sys.exc_info):

    """ Return the execution frame level positions up the
        execution stack (defaulting to the current frame).

        WARNING: Storing the frame in variables will cause
        circular references which could result in the frames
        and associated objects to live forever.
    """
    try:
        1/0
    except:
        frame = exc_info()[2].tb_frame.f_back
    if level:
        for i in trange(level):
            frame = frame.f_back
    return frame

def freeze(classobj):

    """ Add all known attributes of base classes to classobj's
        attribute dictionary
        - does not overwrite attributes
    """
    dict = classobj.__dict__
    if dict.has_key('__frozen__'):
        return
    # This won't overwrite anything, but still update the class
    # dictionary in place (frozen() returns a dictionary that includes
    # dict's entries among others):
    dict.update(frozen(classobj))
    dict['__frozen__'] = 1
    # XXX How to optimize unnecessary failing lookups in baseclasses ?

def frozen(classobj):

    """ Return a dictionary that contains all known attributes
        of classobj
        - uses cached versions if available
    """
    dict = {}
    for c in reverse(classobj.__bases__):
        otherdict = c.__dict__
        if not otherdict.has_key('__frozen__'):
            frozendict = frozen(c)
        else:
            frozendict = otherdict
        dict.update(frozendict)
    dict.update(classobj.__dict__)
    return dict

def attributes(obj,of_class=None,
               d=None):

    """ Find all attributes that are accessible through obj
        and return them as dictionary. 

        If of_class is given, only those attributes are returned that
        are instances of that class. The function mimics the
        inheritance scheme used by Python.

    """
    if d is None:
        d = {}
    # First the class attributes
    classobj = getattr(obj,'__class__',None)
    if classobj is not None:
        class_attributes(classobj,of_class,d)
    # Then the instance attributes
    if of_class is not None:
        for k,v in obj.__dict__.items():
            if isinstance(v,of_class):
                d[k] = v
    else:
        d.update(obj.__dict__)
    return d

def class_attributes(classobj,of_class=None,
                     d=None):

    """ Find all attributes that are accessible through classobj
        and return them as dictionary. 

        If of_class is given, only those attributes are returned that
        are instances of that class. The function mimics the
        inheritance scheme used by Python.

    """
    if d is None:
        d = {}
    # First the base classes
    bases = getattr(classobj,'__bases__',None)
    if bases is not None:
        for b in reverse(bases):
            class_attributes(b,of_class,d)
    # Then the class itself
    if of_class is not None:
        for k,v in classobj.__dict__.items():
            if isinstance(v,of_class):
                d[k] = v
    else:
        d.update(classobj.__dict__)
    return d

def inst_attributes(obj,of_class=None):

    """ Find all instance attributes of obj that are instances of
        of_class and return them as dictionary.

    """
    d = {}
    if of_class:
        for k,v in obj.__dict__.items():
            if isinstance(v,of_class):
                d[k] = v
    else:
        d.update(obj.__dict__)
    return d

def localize(instance):

    """ Add all known attributes of the instance's class and direct
        base classes to its attribute dictionary, binding methods if
        necessary
        - only one level deep
        - does not overwrite attributes

        *WARNING:* this function introduces lots of circular
        references (one for each method) !!!  Be sure to clear
        instance.__dict__ before unscoping instance !!!

    """
    classobj = instance.__class__
    classes = (classobj,) + classobj.__bases__
    dict = instance.__dict__
    for c in classes:
        for a in c.__dict__.keys():
            if not dict.has_key(a):
                dict[a] = getattr(instance,a)

def localized(instance):

    """ Add all known attributes of the instance's class and direct
        base classes to a dictionary, binding methods if necessary, and
        return it.
        - only one level deep

        *WARNING:* this function introduces lots of circular
        references !!!  Be sure to clear the returned dictionars
        before unscoping it !!!

    """
    classobj = instance.__class__
    classes = (classobj,) + classobj.__bases__
    dict = instance.__dict__.copy()
    for c in classes:
        for a in c.__dict__.keys():
            if not dict.has_key(a):
                dict[a] = getattr(instance,a)
    return dict

def ascii2int(str,base=10,

              orig_atoi=string.atoi):

    """ Convert a string to an integer.

        Works like string.atoi except that in case of an error no
        exception raised but 0 is returned; this makes it useful in
        conjunction with map().

    """
    try:
        return orig_atoi(str,base)
    except:
        return 0

def str2time(x,

             time=time,ascii2int=ascii2int):

    """ Convert a textual representation of date/time into an internal
        time.time() value using some assumptions on abbreviations.
        - returns negative numbers to indictate errors
        - knows about DST (makes small errors near the time of switching)
        - centuries can be omitted: 0-69 becomes 20xx, 70-99 19xx

        Known formats:
        - 1.1.90, 01.01.90, 1.1.1990 (date only, time defaults to 0:00:00)
        - 1.1. (current year is appended, 0:00:00)
        - 1.1.90 14:00
        - 14:00 (today is used as date)
    """
    now = time.localtime(time.time())
    ti = now[3:5]
    da = now[0:3]
    try:
        x = string.split(x)
        if len(x) == 0: return -3
        d = string.splitfields(x[0],'.')
        t = string.splitfields(x[-1],':')
        if len(t) > 1:
            # Date and time
            if len(t) < 2: return -1
            ti = map(ascii2int,t)
            if len(ti) == 2:
                ti.append(0)
            elif len(ti) > 3:
                ti = ti[:3]
            ti = tuple(ti)
        else:
            # No time given, presume 0:00:00
            ti = (0,0,0)
        if len(d) > 1:
            # Date given
            if len(d) != 3: return -2
            d.reverse()
            da = tuple(map(string.atoi,d))
            if da[0] == 0:
                # Year is missing
                da = (now[0],) + da[1:3]
            elif da[0] < 100:
                # Century is missing (note: this is bad !)
                if da[0] < 70: # XXX
                    da = (2000+da[0],) + da[1:3]
                else:
                    da = (1900+da[0],) + da[1:3]
        if 1 == len(d) == len(t): return -3
        try:
            tm = time.mktime(da+ti+(0,0,0))
        except:
            #sys.stderr.write('Wrong date: %s was converted to %s'%(x,`da+ti+(0,0,0,0)`))
            return -4
        if time.localtime(tm)[8] == 1:
            # DST is on, adjust time
            tm = tm - 3600
        return tm
    except:
        return -9

def filecontent(filename,default=''):

    """ Return the file's content as a string, default in case
        there's an error
    """
    try:
        f = open(filename,'rb')
    except IOError:
        return default
    c = f.read()
    f.close()
    return c

def long2str(x):

    """ Convert long integer x to a string.
    """
    l = ( x        & 0xff,
         (x >> 8)  & 0xff,
         (x >> 16) & 0xff,
         (x >> 24) & 0xff)
    return string.join(map(chr,l))
    
### Hack to enable module finalization

class ModuleFinalization:

    def __init__(self,function):

        self.fini = function

    def __del__(self):

        self.fini()

# example:
#def _cleanup():
#    print 'away we go...'
#_fini = ModuleFinalization(_cleanup)

def func_info(level=1):

    """ func_info()

        Returns a tuple (name,filename) giving the name of the calling
        function (*) and the filename where it is defined.

        Note that this only works if the calling function is a Python
        function or method (because only these create new execution
        frames). When called from e.g. a builtin function like map(),
        it will return information about the function from where the
        builtin function was called.

        (*) level indicates how far up the calling stack to look for
        the information. Default is one level meaning: the calling
        function.
        
    """
    try:
        1/0
    except:
        frame = sys.exc_info()[2].tb_frame
        for i in trange(level):
            frame = frame.f_back
        name = frame.f_code.co_name
        filename = frame.f_code.co_filename
        del frame # you never know...
    return (name,filename)

def func_sig(func):

    """func_sig(func)

       Returns the signature of a Python function/method as string.
       Keyword initializers are also shown using
       repr(). Representations longer than 100 bytes are truncated.

       XXX Anonymous argument ((a,b,c)=(1,2,3)) are not supported and
           probably never will be since they require disassembling the
           byte code which is bound to fail once byte code optimizers find
           their way into every Pythoneers home...

    """
    if hasattr(func,'im_func'):
        # func is a method
        func = func.im_func
    code = func.func_code
    fname = code.co_name
    callargs = code.co_argcount
    # XXX Uses hard coded values taken from Include/compile.h
    args = list(code.co_varnames[:callargs])
    if func.func_defaults:
        i = len(args) - len(func.func_defaults)
        for default in func.func_defaults:
            try:
                r = repr(default)
            except:
                r = '<repr-error>'
            if len(r) > 100:
                r = r[:100] + '...'
            arg = args[i]
            if arg[0] == '.':
                # anonymous arguments
                arg = '(...)'
            args[i] = '%s=%s' % (arg,r)
            i = i + 1
    if code.co_flags & 0x0004: # CO_VARARGS
        args.append('*'+code.co_varnames[callargs])
        callargs = callargs + 1
    if code.co_flags & 0x0008: # CO_VARKEYWORDS
        args.append('**'+code.co_varnames[callargs])
        callargs = callargs + 1
    return '%s(%s)' % (fname,string.join(args,', '))

def func_call(level=1):

    """ func_call()

        Returns a string explaining which parameters where passed to
        the calling function (*) and from which file and line number it
        was invoked.  Same comments as for func_info(). Note that
        line number information is only correct when running Python
        in non-optimized mode (i.e. without -O). Sample return string:

        'test(a=1, b=2, c=3, args=()) # called from "Tools.py":353'

        (*) level indicates how far up the calling stack to look for
        the information. Default is one level meaning: the calling
        function.
        
    """
    try:
        1/0
    except:
        frame = sys.exc_info()[2].tb_frame
    for i in trange(level):
        frame = frame.f_back
    #import hack; hack.show(frame,5)
    code = frame.f_code
    fname = code.co_name
    l = []
    callargs = code.co_argcount
    # XXX Uses hard coded values taken from Include/compile.h
    if code.co_flags & 0x0004: # CO_VARARGS
        callargs = callargs + 1
    if code.co_flags & 0x0008: # CO_VARKEYWORDS
        callargs = callargs + 1
    for v in code.co_varnames[:callargs]:
        try:
            r = repr(frame.f_locals[v])
        except:
            r = '<repr-error>'
        if len(r) > 100:
            r = r[:100] + '...'
        l.append('%s=%s' % (v,r))
    if frame.f_back:
        where = '# called from "%s":%i' % \
                (frame.f_back.f_code.co_filename,frame.f_back.f_lineno)
    else:
        where = '# called from <toplevel>'
    del frame,code # you never know...
    return '%s(%s) %s' % (fname,string.join(l,', '), where)

def localize_builtins():

    """ Copy all builtins to the caller's locals. This is done
        in a non-overwriting fashion.
    """
    try:
        1/0
    except:
        frame = sys.exc_info()[2].tb_frame.f_back
    builtins = frame.f_builtins
    locals = frame.f_locals
    for k,v in builtins.items():
        if not locals.has_key(k):
            locals[k] = v
    del frame,builtins,locals # better safe than sorry

_basemethod_cache = {}

def basemethod(object,method=None,

               cache = _basemethod_cache,InstanceType=types.InstanceType,
               ClassType=types.ClassType):

    """ Return the unbound method that is defined *after* method in the
        inheritance order of object with the same name as method
        (usually called base method or overridden method).

        object can be an instance, class or bound method. method, if
        given, may be a bound or unbound method. If it is not given,
        object must be bound method.

        Note: Unbound methods must be called with an instance as first
        argument.

        The function uses a cache to speed up processing. Changes done
        to the class structure after the first hit will not be noticed
        by the function.

        XXX Rewrite in C to increase performance.

    """
    if method is None:
        method = object
        object = method.im_self
    defclass = method.im_class
    name = method.__name__
    if type(object) is InstanceType:
        objclass = object.__class__
    elif type(object) is ClassType:
        objclass = object
    else:
        objclass = object.im_class

    # Check cache
    cacheentry = (objclass, name)
    basemethod = cache.get(cacheentry, None)
    if basemethod is not None:
        if not issubclass(objclass, basemethod.im_class):
            if __debug__:
                sys.stderr.write(
                    'basemethod(%s, %s): cached version (%s) mismatch: '
                    '%s !-> %s\n' %
                    (object, method, basemethod,
                     objclass, basemethod.im_class))
        else:
            return basemethod

    # Find defining class
    path = [objclass]
    while 1:
        if not path:
            raise AttributeError,method
        c = path[0]
        del path[0]
        if c.__bases__:
            # Prepend bases of the class
            path[0:0] = list(c.__bases__)
        if c is defclass:
            # Found (first occurance of) defining class in inheritance
            # graph
            break
        
    # Scan rest of path for the next occurance of a method with the
    # same name
    while 1:
        if not path:
            raise AttributeError,name
        c = path[0]
        basemethod = getattr(c, name, None)
        if basemethod is not None:
            # Found; store in cache and return
            cache[cacheentry] = basemethod
            return basemethod
        del path[0]
    raise AttributeError,'method %s' % name
    
def lookup_path(classobj):

    """ Return a list representing the lookup path taken by getattr()
        whenever an attribute from classobj is requested.

        The path consists of all class objects passed during lookup in
        the right order.
        
    """
    path = [classobj]
    for i,c in reverse(irange(path)):
        if c.__bases__:
            l = []
            for bc in c.__bases__:
                l[len(l):] = lookup_path(bc)
            path[i+1:i+1] = l
    return path

hexcode = tuple('0123456789abcdefghijklmnopqrstuvwxyz')
code64 = tuple('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'
               '0123456789+/')
code256 = tuple(map(chr,range(256)))

def base(x,b,code=hexcode,
         # Locals:
         join=string.join,divmod=divmod):
    
    """ Return a string representation of integer x in base b.

        Uses code as encoding table (defaults to an extended HEX
        table).
        
    """
    if x == 0: return '0'
    l = []
    append = l.append
    while x > 0:
        x,y = divmod(x,b)
        append(code[y])
    l.reverse()
    return join(l,'')

def filedate(path,

             stat=os.stat):

    """ Return the modification date/time as DateTime instance.

        Needs mxDateTime to be installed.

    """
    from mx import DateTime
    return DateTime.localtime(stat(path)[8])

def filesize(path,

             stat=os.stat):

    """ Return the file size in bytes
    """
    return stat(path)[6]

def abspath(path,

            expandvars=os.path.expandvars,expanduser=os.path.expanduser,
            join=os.path.join,getcwd=os.getcwd):

    """ Return the corresponding absolute path for path.

        path is expanded in the usual shell ways before
        joining it with the current working directory.

    """
    try:
        path = expandvars(path)
    except AttributeError:
        pass
    try:
        path = expanduser(path)
    except AttributeError:
        pass
    return join(getcwd(),path)

def _addlinebreaks(data, column, linebreak='\012'):

    """ Break data into multiple lines at column.

        Uses linebreak as end-of-line indicator (defaults to LF).
        
    """
    from cStringIO import StringIO
    infile = StringIO(data)
    outfile = StringIO()
    read = infile.read
    write = outfile.write
    chunk = read(column)
    while chunk:
        write(chunk)
        write(linebreak)
        chunk = read(column)
    return outfile.getvalue()

def _uu_encode(data, filename='<data>', mode=0666):
    
    from cStringIO import StringIO
    from binascii import b2a_uu
    infile = StringIO(data)
    outfile = StringIO()
    read = infile.read
    write = outfile.write
    # Encode
    write('begin %o %s\n' % (mode & 0777, filename))
    chunk = read(45)
    while chunk:
        write(b2a_uu(chunk))
        chunk = read(45)
    write(' \nend\n')
    return outfile.getvalue()

def _uu_decode(data):
    
    from cStringIO import StringIO
    from binascii import a2b_uu
    infile = StringIO(input)
    outfile = StringIO()
    readline = infile.readline
    write = outfile.write

    # Find start of encoded data
    while 1:
        s = readline()
        #print '...',s,
        if not s:
            raise ValueError, 'Missing "begin" line in input data'
        if s[:5] == 'begin':
            break

    # Decode
    while 1:
        s = readline()
        if not s or \
           s == 'end\n':
            break
        try:
            data = a2b_uu(s)
        except binascii.Error, v:
            # Workaround for broken uuencoders by /Fredrik Lundh
            nbytes = (((ord(s[0])-32) & 63) * 4 + 5) / 3
            data = a2b_uu(s[:nbytes])
            #sys.stderr.write("Warning: %s\n" % str(v))
        write(data)
    if not s:
        raise ValueError, 'Truncated input data'

    return outfile.getvalue()

def encodedata(data, encoding,

               lower=string.lower):

    """ Encode data using the given encoding.

        Possible values for encoding include:
        'base64'   - BASE 64 encoding
        'hex'      - HEX encoding (no line breaks)
        'hexlines' - HEX encoding (with CR line breaks)

        In Python 2.0 and up, encoding may also be an encoding
        supported natively by Python via the codec registry.
    
    """
    encoding = lower(encoding)
    
    if encoding == 'base64':
        import base64
        return base64.encodestring(data)
    
    elif encoding == 'hex' or \
         encoding == 'hexlines':
        from mx.TextTools import str2hex
        import cStringIO
        result = str2hex(data)
        if encoding == 'hexlines':
            return _addlinebreaks(result, 72)
        return result

    elif encoding == 'uu':
        import binascii
        
        out_file.write('begin %o %s\n' % ((mode&0777),name))
        str = in_file.read(45)
        while len(str) > 0:
            out_file.write(binascii.b2a_uu(str))
            str = in_file.read(45)
        out_file.write(' \nend\n')

        return base64.encodestring(data)
    
    else:
        # This works in Python >=2.0 only
        try:
            return data.encode(encoding)
        except AttributeError:
            raise ValueError, 'unknown encoding "%s"' % encoding

def decodedata(data, encoding,

               lower=string.lower):

    """ Decode data using the given encoding.

        Possible values for encoding include:
        'base64'   - BASE 64 encoding
        'hex'      - HEX encoding (no line breaks)
        'hexlines' - HEX encoding (with CR line breaks)

        In Python 2.0 and up, encoding may also be an encoding
        supported natively by Python via the codec registry.
    
    """
    encoding = lower(encoding)
    
    if encoding == 'base64':
        import base64
        return base64.decodestring(data)
    
    elif encoding == 'hex' or \
         encoding == 'hexlines':
        from mx.TextTools import hex2str
        # Remove whitespace
        l = string.split(data)
        data = string.join(l, '')
        # Decode
        return hex2str(data)

    else:
        # This works in Python >=2.0 only
        try:
            from codecs import lookup
        except ImportError:
            raise ValueError, 'unknown encoding "%s"' % encoding
        else:
            decode = lookup(encoding)[1]
            return decode(data)
