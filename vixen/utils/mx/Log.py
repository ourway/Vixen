#! /usr/bin/python

""" Standard Logging Interface

    Creates an object log, that can be used for global logging
    activities. The properties can later be changed by calling
    log.setup().
    
    It is safe to do a 'from mx.Log import *'.

    Copyright (c) 1999-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

"""
# Be careful with these symbols since we want 'from mx.Log import *'
# to not clutter up the users namespace.
import sys,string,types,traceback
from mx import DateTime,Tools
_sys,_string,_DateTime,_types,_traceback = sys,string,DateTime,types,traceback
del sys,string,DateTime,types,traceback

# Load new builtins
import  mx.Tools.NewBuiltins
del mx

# Infos & Errors (lower values indicate higher importance)
SYSTEM_ALWAYS_LOG = 0
SYSTEM_FATAL = 1
SYSTEM_PANIC = 2
SYSTEM_ERROR = 10
SYSTEM_CANCEL = 11
SYSTEM_IMPORTANT = 100
SYSTEM_WARNING = 500
SYSTEM_MESSAGE = 600
SYSTEM_UNIMPORTANT = 3000
SYSTEM_INFO = 1000
SYSTEM_DEBUG = 2000
# The highest used value:
SYSTEM_ANY = 9999
# Some log level limits
SYSTEM_LOG_NOTHING = 0
SYSTEM_LOG_EVERYTHING = SYSTEM_ANY

### Helpers

_NAME_LEN_LIMIT = 80
_VALUE_LEN_LIMIT = 500
_TRACEBACK_LIMIT = 100
_DICT_LEN_LIMIT = 50
_NON_RECURSIVE = (_types.ModuleType,
                  _types.FunctionType,
                  _types.MethodType,
                  _types.BuiltinFunctionType,
                  _types.BuiltinMethodType,
                  _types.ClassType,
                  __builtins__)

def print_tb_locals(tb=None, *args, **kws):

    """ Print a listing of the traceback's locals() to file.
    """
    # Walk down the traceback
    if tb is None:
        tb = _sys.exc_info()[2]
    while tb.tb_next != None:
        tb = tb.tb_next
    # Show the local variables
    apply(print_frame_locals, (tb.tb_frame,) + args, kws)

def print_tb_globals(tb=None, *args, **kws):

    """ Print a listing of the traceback's globals() to file.
    """
    # Walk down the traceback
    if tb is None:
        tb = _sys.exc_info()[2]
    while tb.tb_next != None:
        tb = tb.tb_next
    # Show the global variables
    apply(print_frame_globals, (tb.tb_frame,) + args, kws)

def print_tb_vars(tb=None, *args, **kws):

    """ Print a listing of the traceback's locals() and globals() to file.

        If locals() and globals() are the same object, only the
        globals() are printed.

    """
    # Walk down the traceback
    if tb is None:
        tb = _sys.exc_info()[2]
    while tb.tb_next != None:
        tb = tb.tb_next
    if tb.tb_frame.f_locals is not tb.tb_frame.f_globals:
        # Show the local variables
        apply(print_frame_locals, (tb.tb_frame,) + args, kws)
    # Show the global variables
    apply(print_frame_globals, (tb.tb_frame,) + args, kws)

def filter_private_attributes(key):

    """ Filters all attributes which start with an underscore.

        For use as filter argument to one of the print_xxx() APIs.
    
    """
    if type(key) is _types.StringType and \
       key[:1] == '_':
        return 0
    return 1

def print_frame_locals(frame,file=_sys.stdout,
                       indent='#  ',
                       title='### Dump of local variables:\n',
                       levels=2,
                       nonrecursive=_NON_RECURSIVE,
                       filter=None):

    """ Print a listing of the locals() in frame to file.
    """
    if title:
        file.write(title)
    print_dict(frame.f_locals,file,indent,levels,
               nonrecursive=nonrecursive,filter=filter)

def print_frame_globals(frame,file=_sys.stdout,
                        indent='#  ',
                        title='### Dump of global variables:\n',
                        levels=2,
                        nonrecursive=_NON_RECURSIVE,
                        filter=None):

    """ Print a listing of the globals() in frame to file.
    """
    if title:
        file.write(title)
    print_dict(frame.f_globals,file,indent,levels,
               nonrecursive=nonrecursive,filter=filter)

def print_dict(dict,file,indent='',levels=1,reprkeys=0,
               nonrecursive=(),filter=None):

    """ Print dictionary to file.

        reprkeys=1 will print the items using repr() for keys as well.
        indent is prepended to all lines. levels indicates the number
        of recursion levels to be printed.

        filter may be given as callable taking the dictionary key as
        input. It should then return 1 for keys which should be
        displayed and 0 for ones which should be skipped.

    """
    l = dict.items()
    l.sort()
    if len(l) > _DICT_LEN_LIMIT:
        l = l[:_DICT_LEN_LIMIT]
        l.append(('...','...truncated...'))
    for k,v in l:
        if filter is not None:
            if not filter(k):
                continue
        if reprkeys:
            try:
                n = repr(k)
            except:
                n = '*repr()-error*'
        else:
            n = str(k)
        try:
            r = repr(v)
        except:
            r = '*repr()-error*'
        # Truncate
        if len(n) > _NAME_LEN_LIMIT:
            n = n[:_NAME_LEN_LIMIT] + '...'
        if len(r) > _VALUE_LEN_LIMIT:
            r = r[:_VALUE_LEN_LIMIT] + '...'
        if reprkeys:
            file.write('%s %-15s = %s\n' % (indent,n,r))
        else:
            file.write('%s.%-15s = %s\n' % (indent,n,r))
        if levels > 1:
            print_recursive(v,file,indent + '  ',levels-1,
                            nonrecursive=nonrecursive, filter=filter)

def print_sequence(obj,file=_sys.stdout,indent='',levels=2,
                   nonrecursive=(),

                   StringType=_types.StringType):

    l = []
    unfold = 0
    try:
        length = len(obj)
    except (AttributeError, ValueError, TypeError):
        return
    for i in trange(min(length,_VALUE_LEN_LIMIT)):
        try:
            value = obj[i]
        except:
            break
        try:
            r = repr(value)
        except:
            r = '*repr()-error*'
        # Truncate
        if len(r) > _VALUE_LEN_LIMIT:
            r = r[:_VALUE_LEN_LIMIT] + '...'
        l.append((value,r))
        if type(value) != StringType or len(value) > 1:
            unfold = 1
    if len(obj) > _VALUE_LEN_LIMIT:
        l.append(('...','...truncated...'))
    if unfold:
        for i,(value,rvalue) in irange(l):
            file.write('%s%-15s = %s\n' % (indent, '[%i]' % i, rvalue))
            if levels > 1:
                print_recursive(value,file,indent + '  ',levels-1,
                                nonrecursive=nonrecursive)

def print_recursive(obj,file=_sys.stdout,indent='',levels=1,
                    nonrecursive=(),filter=None,

                    StringType=_types.StringType):

    # Filter out nonrecursive types and objects
    try:
        if type(obj) in nonrecursive or \
           obj in nonrecursive:
            return
    except:
        # Error during compares result in the object not being
        # printed
        return
    
    # Print the object depending on its interface
    if hasattr(obj,'__dict__') and \
       obj.__dict__ is not None:
        print_dict(obj.__dict__,file,indent,levels,
                   nonrecursive=nonrecursive, filter=filter)
    elif hasattr(obj,'items'):
        print_dict(obj,file,indent,levels,1,
                   nonrecursive=nonrecursive, filter=filter)
    elif issequence(obj) and not type(obj) == StringType:
        print_sequence(obj,file,indent,levels,
                       nonrecursive=nonrecursive)
    elif hasattr(obj,'__members__'):
        d = {}
        for attr in obj.__members__:
            d[attr] = getattr(obj,attr)
        print_dict(d, file, indent, levels,
                   nonrecursive=nonrecursive, filter=filter)

def print_obj(obj,file=_sys.stdout,indent='',levels=2,
              nonrecursive=(),filter=None):

    try:
        r = repr(obj)
    except:
        r = '*repr()-error*'
    # Truncate
    if len(r) > _VALUE_LEN_LIMIT:
        r = r[:_VALUE_LEN_LIMIT] + '...'
    file.write('%s%s\n' % (indent,r))
    print_recursive(obj, file, indent + '  ', levels-1, filter=filter)

def print_stack_with_locals(file=_sys.stdout,levels=100,offset=0):

    print_stack(file, levels=levels, offset=offset+1, locals=1)

def print_stack(file=_sys.stdout,levels=100,offset=0,locals=0):

    # Prepare frames
    try:
        raise ValueError
    except ValueError:
        # Go back offset+1 frames...
        f = _sys.exc_info()[2].tb_frame
        for i in range(offset + 1):
            if f.f_back is not None:
                f = f.f_back
    frames = []
    while f:
        frames.append(f)
        f = f.f_back
    frames.reverse()
    # Prepare stack
    stack = _traceback.extract_stack()
    # Make output
    file.write('Stack:\n')
    for (frame,(filename, lineno, name, line)) in \
        tuples(frames,stack)[-levels:]:
        file.write(' File "%s", line %d, in %s\n' % (filename,lineno,name))
        if line:
            file.write('  %s\n' % _string.strip(line))
        if locals:
            print_frame_locals(frame,file,indent='   |',title='')

def print_loaded_modules(file=_sys.stdout,

                         string=_string,sys=_sys):

    """ Print a listing of currently loaded modules to file.
    """
    l = sys.modules.items()
    l.sort()
    file.write('Loaded modules and packages:\n')
    for k,v in l:
        p = string.split(k,'.')
        for i in range(len(p)-1):
            p[i] = '   '
        n = string.join(p,'')
        if v is not None:
            if hasattr(v,'__path__'):
                # package
                file.write(' %s[%s]\n' % (string.join(p[:-1],''),p[-1]))
            else:
                # module
                file.write(' %s\n' % (n))

def format_traceback(title='### Dump of local variables:\n',
                     filter=None):

    """ Formats a traceback of the current exception and
        returns it as string.

        Includes a listing of the locals() causing that were active
        during the exception. title is used to separate the traceback
        from the listing of variables. filter can be given to filter
        out certain variables from the listing. It takes one argument:
        the variable name and has to return 1/0.

    """
    import cStringIO
    f = cStringIO.StringIO()
    _traceback.print_exc(_TRACEBACK_LIMIT,f)
    print_tb_locals(_sys.exc_info()[2], f, title=title, filter=filter)
    return f.getvalue()

### Log class

class Log:

    """ Log class.
    """
    ignore_level = SYSTEM_LOG_EVERYTHING        # log level
    log_file = 'default.log'                    # name of the log file
    log_id = None                               # log id to use
    open_log_file = None                        # open file object
    line_buffer = ''                            # line buffer used by .write()
    
    # Attributes needed for file interface:
    closed = 0                                  # We can always accept data
    
    def __init__(self,ignore_level=None,log_file='stderr',
                 log_id=None,log_level=None):

        """ Setup a log object which writes its output to log_file
            using the given id marker. 

            The ignore_level indicates the level at which logging
            activities are ignored. A low value causes less important
            notices like SYSTEM_INFOs to be ignored. If it is set to
            0, no logging is done. 

            Alternatively, log_level may be specified giving the last
            level to log (all higher levels are ignored).

            The log id can be set to separate multiple
            threads/processes in the log. It defaults to the process
            id.

        """
        if ignore_level is not None:
            self.ignore_level = ignore_level
        elif log_level is not None:
            self.ignore_level = log_level + 1
        self.log_file = log_file
        import os
        if not log_id:
            self.log_id = 'p' + str(os.getpid())
        else:
            self.log_id = log_id + ':' + str(os.getpid())
        self.orig_stderr = _sys.stderr
        self.orig_stdout = _sys.stdout

    def redirect_stderr(self):

        """ Redirects stderr output to the log mechanism.
        """
        _sys.stderr = self

    def redirect_stdout(self):

        """ Redirects stdout output to the log mechanism.
        """
        _sys.stdout = self

    def disable_redirects(self):

        """ Reset stderr and stdout to their values when the log object
            was created.
        """
        _sys.stderr = self.orig_stderr
        _sys.stdout = self.orig_stdout

    def open(self,flags='a'):

        """ Open the log file. 

            This is done on-the-fly in case a log request is
            encountered and the file is still closed.  This interface
            also supports redirecting messages to stderr or stdout by
            using 'stderr' or 'stdout' as log file name.  If the log
            file cannot be opened, stderr is used instead.

        """
        filename = self.log_file
        if filename == 'stderr':
            file = self.orig_stderr
        elif filename == 'stdout':
            file = self.orig_stdout
        else:
            try:
                file = open(self.log_file,flags)
            except:
                self.open_log_file = file = self.orig_stderr
                log(SYSTEM_ERROR,
                    'Could not open log file "%s" - using stderr',
                    self.log_file)
        self.open_log_file = file
        return file

    def close(self):

        """ Close the log file.

            Note: The next logging request will automatically open the
            file again.

        """
        if self.open_log_file:
            self.open_log_file.close()
        self.open_log_file = None

    def setup(self,ignore_level=None,log_file=None,log_id=None,
              log_level=None):

        """ Change the setup after creation
            - use keywords to change only certain aspects, e.g.
              setup(log_file = 'my.log')
        """
        if ignore_level is not None:
            self.ignore_level = ignore_level
        elif log_level is not None:
            self.ignore_level = log_level + 1
        if log_file is not None:
            self.log_file = log_file
            self.open_log_file = None
        if log_id is not None:
            import os
            self.log_id = log_id + ':' + str(os.getpid())

    def __call__(self,errno,*args):

        """ Default logging mechanism: errno contains the error id and
            the remaining arguments get interpreted as:
            arg0 % (arg1,arg2,...)
        """
        if errno >= self.ignore_level: return
        if len(args) > 1:
            s = args[0] % args[1:]
        elif len(args) == 1:
            s = args[0]
        else:
            s = ''
        f = self.open_log_file or self.open()
        f.write("%04i %s [%s] %s\n" %
                (errno,_DateTime.now(),self.log_id,s))
        f.flush()

    def traceback(self,errno,*args):

        """ Write a traceback of the last exception to the log file.

        """
        if errno >= self.ignore_level: return
        if len(args) > 1:
            s = args[0] % args[1:]
        elif len(args) == 1:
            s = args[0]
        else:
            s = ''
        f = self.open_log_file or self.open()
        f.write("%04i %s [%s] %s...\n" %
                (errno,_DateTime.now(),self.log_id,s))

        # Print traceback and locals to file
        f.write(79*'-'+ '\n')
        _traceback.print_exc(_TRACEBACK_LIMIT,f)
        print_tb_locals(_sys.exc_info()[2], f,
                        title='### Dump of local variables (omitting private ones):\n',
                        filter=filter_private_attributes)
        f.write(79*'-'+'\n')
        f.flush()

    def modules(self,errno,*args):

        """ Write a list of all currently loaded modules to the log file.
        """
        if errno >= self.ignore_level: return
        if len(args) > 1:
            s = args[0] % args[1:]
        elif len(args) == 1:
            s = args[0]
        else:
            s = ''
        f = self.open_log_file or self.open()
        f.write("%04i %s [%s] %s...\n" %
                (errno,_DateTime.now(),self.log_id,s))
        
        # Print module listing
        f.write(79*'-'+ '\n')
        print_loaded_modules(f)
        f.write(79*'-'+'\n')
        f.flush()

    def stack(self,errno,*args,**kws):

        """ Write a stack dump to the log file.

            A keyword argument "levels" can be given to set the number
            of stack frames to show. It defaults to 3. Higher values
            can result in huge amounts of data to be written to the
            log file !

            If a keyword argument "locals" is given and false, no
            locals are printed in the dump. It defaults to true.

        """
        if errno >= self.ignore_level: return
        if len(args) > 1:
            s = args[0] % args[1:]
        elif len(args) == 1:
            s = args[0]
        else:
            s = ''
        levels = kws.get('levels', 3)
        locals = kws.get('locals', 1)
        f = self.open_log_file or self.open()
        f.write("%04i %s [%s] %s...\n" %
                (errno,_DateTime.now(),self.log_id,s))
        
        # Print stack and locals to file
        f.write(79*'-'+ '\n')
        print_stack(f, levels=levels, offset=1, locals=locals)
        f.write(79*'-'+'\n')
        f.flush()

    def verbatim(self,errno,*args):

        """ Write args[0] % args[1:] to the log file. This method
            is meant for multi line messages, since the logged text
            is not manipulated in any way.
        """
        if errno >= self.ignore_level: return
        if len(args) > 1:
            s = args[0] % args[1:]
        elif len(args) == 1:
            s = args[0]
        else:
            s = ''
        f = self.open_log_file or self.open()
        f.write("%04i %s [%s]\n" % (errno,_DateTime.now(),self.log_id))
        f.write(79*'-'+ '\n%s\n' % _string.strip(s) + 79*'-'+'\n')
        f.flush()

    def call(self,errno,level=1):

        """ Log a function call.

            level indicates how far up the calling stack to look for
            the call information. Default is one level meaning the
            directly calling function.

            Note: Needs mx.Tools.func_call() API.
            
        """
        if errno >= self.ignore_level: return
        from mx.Tools import func_call
        f = self.open_log_file or self.open()
        f.write("%04i %s [%s] %s\n" %
                (errno,_DateTime.now(),self.log_id, func_call(level+1)))
        f.flush()

    def error(self,errno,errorname,*args):

        """ Write errorname, args[0] % args[1:] to the log file.

            This method is meant for multi line error messages that
            hold additional data referring to the error.
            
        """
        if errno >= self.ignore_level: return
        if len(args) > 1:
            s = args[0] % args[1:]
        elif len(args) == 1:
            s = args[0]
        else:
            s = ''
        f = self.open_log_file or self.open()
        f.write("%04i %s [%s] %s\n" %
                (errno,_DateTime.now(),self.log_id, errorname))
        f.write(79*'-'+ '\n%s\n' % _string.strip(str(s)) + 79*'-'+'\n')
        f.flush()

    # Alias
    long = error

    def text(self,errno,errorname,*args):

        """ Write errorname and a line numbered version of args[0] %
            args[1:] to the log file.

            This method is meant for multi line error messages that
            hold additional data referring to the error.

            Needs mx.TextTools to be installed.
            
        """
        if errno >= self.ignore_level: return
        if len(args) > 1:
            s = args[0] % args[1:]
        elif len(args) == 1:
            s = args[0]
        else:
            s = ''
        from mx.TextTools import splitlines
        l = splitlines(s)
        for i in range(len(l)):
            l[i] = '%04i %s' % (i+1,l[i])
        f = self.open_log_file or self.open()
        f.write("%04i %s [%s] %s\n" %
                (errno,_DateTime.now(),self.log_id, errorname))
        f.write(79*'-'+ '\n%s\n' % _string.join(l,'\n') + 79*'-'+'\n')
        f.flush()

    def object(self,errno,objname,object,levels=2):

        """ Write objname plus a dump of object to the log file.

            levels indicates how many levels of the object hierarchy
            should be written.
            
        """

        if errno >= self.ignore_level: return
        f = self.open_log_file or self.open()
        f.write("%04i %s [%s] %s\n" %
                (errno, _DateTime.now(), self.log_id, objname))
        f.write(79*'-'+'\n')
        print_obj(object,f,levels=levels)
        f.write(79*'-'+'\n')
        f.flush()
        
    def write(self,data):

        """ File interface, so that the object can be used as
            sys.stderr replacement.

            Errorcode 0 is used. The output is line buffered.
            
        """
        if self.ignore_level == 0: return
        self.line_buffer = buffer = self.line_buffer + data
        if '\n' not in buffer:
            return

        # Write out all complete lines stored in line_buffer
        lines = _string.split(buffer,'\n')
        if buffer[-1:] != '\n':
            # last line is incomplete
            self.line_buffer = lines[-1]
            lines = lines[:-1]
        else:
            self.line_buffer = ''

        f = self.open_log_file or self.open()
        now = _DateTime.now()
        id = self.log_id
        fwrite = f.write
        for line in lines:
            if not _string.strip(line):
                # avoid emtpy lines
                continue
            fwrite("%04i %s [%s] %s\n" % (0,now,id,line))
        f.flush()

    def flush(self):

        """ Flush the underlying log stream.
        """
        if self.open_log_file:
            self.open_log_file.flush()

    def exception(self,errno,*args):

        """ Log a real exception in the log file.
        """
        if errno >= self.ignore_level: return
        exc_class,exc_inst,exc_traceback = _sys.exc_info()
        if exc_class is None:
            return
        if len(args) > 1:
            s = args[0] % args[1:]
        elif len(args) == 1:
            s = args[0]
        else:
            s = ''
        # go down the traceback
        tb = exc_traceback
        while tb.tb_next is not None:
            tb = tb.tb_next
        frame = tb.tb_frame

        f = self.open_log_file or self.open()
        f.write("%04i %s [%s] %s (at '%s':%i - %s:'%s')\n" % 
                (errno,_DateTime.now(),self.log_id,s,
                 frame.f_code.co_filename,
                 _traceback.tb_lineno(tb),
                 exc_class,exc_inst))
        f.flush()
        # Cleanup to avoid circ. refs
        del exc_class,exc_inst,exc_traceback

# Create a main log object
if __debug__ and Tools.debugging():
    log = Log(SYSTEM_LOG_EVERYTHING)
else:
    log = Log(SYSTEM_INFO+1)
