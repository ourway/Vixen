""" Hacking Tools for Python

    (c) 1997-2000, Copyright by Marc-Andre Lemburg (mal@lemburg.com); 

         All Rights Reserved.

    Permission to use, copy, modify, and distribute this software and
    its documentation for any purpose and without fee or royalty is
    hereby granted, provided that the above copyright notice appear in
    all copies and that both the copyright notice and this permission
    notice appear in supporting documentation or portions thereof,
    including modifications, that you make.

    THE AUTHOR MARC-ANDRE LEMBURG DISCLAIMS ALL WARRANTIES WITH REGARD
    TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS, IN NO EVENT SHALL THE AUTHOR BE
    LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
    DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
    WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
    ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
    PERFORMANCE OF THIS SOFTWARE !

"""

__version__ = '0.5'

__package_info__ = """
BEGIN PYTHON-PACKAGE-INFO 1.0
Title:                  Hacking tools for Python
Current-Version:        0.5
Home-Page:              http://www.lemburg.com/python
Primary-Site:           http://www.lemburg.com/python/hack.py

This module includes some tools that I find useful to examine
code from inside an interactive interpreter session. It includes
functions to display doc strings, dictionaries, sequences, etc.
in a more or less nice format and common stuff like disassembly
routines, timing gadgets and exception helpers.
END PYTHON-PACKAGE-INFO
"""

import types,sys,time,string,re

INDENT = '    ' # string used to indent one level in show,docs,...

def docs(c,

         INDENT=INDENT):

    """ doc(c) -- print c's doc-strings """

    try:
        showobject(c,'',0)
        showdocstring(c.__doc__,1)
        if hasattr(c,'__version__'):
            print
            print INDENT+'[Version: %s]' % c.__version__
    except AttributeError:
        pass
    print
    items = []
    try:
        items = c.__dict__.items()
    except AttributeError:
        items = []
    try:
        for m in  c.__methods__:
            items.append((m,getattr(c,m)))
    except AttributeError:
        pass
    if items:
        items.sort()
        for name,obj in items:
            if hasattr(obj,'__doc__') and obj.__doc__:
                showobject(obj,name, 1)
                showdocstring(obj.__doc__, 2)

# Helper for docs:

def func_sig(func):

    """func_sig(func)

       Returns the signature of a Python function/method as string.
       Keyword initializers are also shown using
       repr(). Representations longer than 100 bytes are truncated.

       XXX Anonymous arguments ((a,b,c)=(1,2,3)) are not supported and
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

spaces = re.compile('([ ]*)[^ ]')

def showdocstring(doc,level=0,

                  split=re.split,INDENT=INDENT,join=string.join,
                  strip=string.strip,expandtabs=string.expandtabs,
                  spaces=spaces):

    try:
        l = split(strip(doc),'\n\|\r\|\r\n')
    except:
        #print '%sno doc string available' % (INDENT*level)
        return
    if len(l) > 1:
        # Try to even out the indents
        indent = sys.maxint
        l = map(expandtabs,l)
        for i in range(1,len(l)):
            m = spaces.match(l[i])
            if m:
                sp = m.regs[1][1]
                if sp < indent:
                    indent = sp
            else:
                # Blank line
                pass
        l = [strip(l[0])] + map(lambda x,indent=indent: x[indent:],l[1:])
    else:
        l = map(strip,l)
    l = map( lambda x,n=level,INDENT=INDENT: INDENT*n + x, l)
    s = join(l,'\n')+'\n'
    print s

def showobject(obj,name='',level=0):

    if type(obj) in (types.FunctionType,types.MethodType):
        try:
            objrepr = func_sig(obj)
        except AttributeError:
            objrepr = name
    elif type(obj) is types.ModuleType:
        objrepr = 'Module ' + name
    elif type(obj) is types.ClassType:
        objrepr = 'Class ' + name
    else:
        objrepr = name
    if not objrepr:
        try:
            objrepr = obj.__name__
        except AttributeError:
            objrepr = repr(obj)
    print INDENT*level + objrepr,':'

###

def info(c):

    """ info(c) -- print all the information known about c """

    print 'Documentation:'
    print '-'*72
    docs(c)
    print
    print 'Attributes, Internals, etc.:'
    print '-'*72
    show(c,2)

def show(c,maxdepth=2,level=0,
         INDENT=INDENT):

    """ show(c) -- print all the internals of c """

    try:
#       print '%srepr:' % (INDENT*level)
        r = repr(c)
        if len(r) > 40:
            r = r[:40]+' ...'
        print '%s%s' % (INDENT*(level),r)
    except:
        return
    level = level + 1
    if level > maxdepth:
        #print
        return
    showobj(c,'__name__',maxdepth,level)
    showobj(c,'__class__',maxdepth,level)
    showseq(c,'__bases__',maxdepth,level)
    showattr(c,'__methods__',maxdepth,level)
    showattr(c,'__members__',maxdepth,level)
    showattr(c,'__attributes__',maxdepth,level)
    showdict(c,'__dict__',maxdepth,level)
#    print

# Helpers for show:

def showattr(c,name,maxdepth=1,level=0,
             INDENT=INDENT):

    """ showattr(c,name) -- for a in c.name: print c.a """

    try:
        items = getattr(c,name)
        items.sort()
    except AttributeError:
        return

    print '%s%s :' % (INDENT*level,name)
    level = level + 1
    if level > maxdepth:
        return

    for x in items:
        try:
            a = getattr(c,x)
            r = repr(a)
        except:
            a = None
            r = '*exception*'
        if len(r) > 40:
            r = r[:40]+' ...'
        if level < maxdepth and a is not None:
            print '%s%s :' % (INDENT*level,x)
            show(a,maxdepth,level+1)
        else:
            print '%s%s : %s' % (INDENT*level,x,r)

def showobj(c,name,maxdepth=1,level=0,
            INDENT=INDENT):

    """ showobj(c,name) -- print object c.name """

    try:
        x = getattr(c,name)
    except AttributeError:
        return

    print '%s%s :' % (INDENT*level,name)
    level = level + 1
    if level > maxdepth:
        return

    show(x,maxdepth,level)

def showseq(c,name,maxdepth=1,level=0,
            INDENT=INDENT):

    """ showseq(c,name) -- print sequence c.name """

    try:
        items = getattr(c,name)
    except AttributeError:
        return

    print '%s%s :' % (INDENT*level,name)
    level = level + 1
    if level > maxdepth:
        return

    if not items:
        print '%s%s' % (INDENT*level,items)
        return

    for x in items:
        try:
            r = repr(x)
        except:
            x = None
            r = '*exception*'
        if len(r) > 40:
            r = r[:40]+' ...'
        if level < maxdepth and x is not None:
            print '%s%s :' % (INDENT*level,r)
            show(x,maxdepth,level+1)
        else:
            print '%s%s' % (INDENT*level,r)

def showdict(c,name,maxdepth=1,level=0,
             INDENT=INDENT):
    
    """ showdict(c,name) -- print c.name.items() """

    try:
        dict = getattr(c,name)
        items = dict.items()
        items.sort()
    except AttributeError:
        return

    print '%s%s :' % (INDENT*level,name)
    level = level + 1
    if level > maxdepth:
        return

    if not items:
        print '%s%s' % (INDENT*level,dict)
        return

    for key,value in items:
        try:
            k = str(key)
        except:
            k = '*exception*'
        if len(k) > 40:
            k = k[:40]+' ...'
        try:
            v = repr(value)
        except:
            v = '*exception*'
            value = None
        if len(v) > 40:
            v = v[:40]+' ...'
        if level < maxdepth and value is not None:
            print '%s%s :' % (INDENT*level,k)
            show(value,maxdepth,level+1)
        else:
            print '%s%s : %s' % (INDENT*level,k,v)

# End of show helpers

def dis(c):

    """ dis(c) -- disassemble c; can be a code-string, -object a function
        or a method
    """
    if type(c) == types.StringType:
        c = compile(c,'hacking','exec')
    elif type(c) == types.FunctionType:
        c = c.func_code
    elif type(c) == types.MethodType or type(c) == types.UnboundMethodType:
        c = c.im_func.func_code
    import dis
    dis.disco(c)

def clock(code,namespace=None):

    """ clock(code[,namespace]) -- clock the code executed in namespace which
        defaults to the top level namespace __main__.
    """

    code =  """import time;hack_timer=time.time(),time.clock()\n"""+\
            code+\
            """\nhack_timer=time.time()-hack_timer[0],time.clock()-hack_timer[1]; print '%.3fabs %.3fusr sec.' % hack_timer\n"""
    c = compile(code,'hack.clock-code','exec')
    if namespace:
        exec c in namespace
    else:
        import __main__
        exec c in __main__.__dict__
    return ''

class timer:

    """ timer class with a quite obvious interface
        - .start() starts a fairly accurate CPU-time timer plus an
          absolute timer
        - .stop() stops the timer and returns a tuple: the CPU-time in seconds
          and the absolute time elapsed since .start() was called
    """

    utime = 0
    atime = 0

    def start(self,
              clock=time.clock,time=time.time):
        self.atime = time()
        self.utime = clock()

    def stop(self,
             clock=time.clock,time=time.time):
        self.utime = clock() - self.utime
        self.atime = time() - self.atime
        return self.utime,self.atime

    def usertime(self,
                 clock=time.clock,time=time.time):
        self.utime = clock() - self.utime
        self.atime = time() - self.atime
        return self.utime

    def abstime(self,
                clock=time.clock,time=time.time):
        self.utime = clock() - self.utime
        self.atime = time() - self.atime
        return self.utime

    def __str__(self):

        return '%0.2fu %0.2fa sec.' % (self.utime,self.atime)

def profile(code,namespace=None):

    """ profile(code[,namespace]) -- profile the code executed in namespace
        which defaults to the top level namespace __main__.
    """
    code = 'import profile;profile.run("'+code+'")'
    c = compile(code,'profiling','exec')
    if namespace:
        exec c in namespace
    else:
        import __main__
        exec c in __main__.__dict__

def why():

    """ why() -- show locals that caused the last exception """

    if hasattr(sys,'last_traceback'):
        tb = sys.last_traceback
        while tb.tb_next != None: tb = tb.tb_next
        frame = tb.tb_frame
        print 'locals() of the last exception:'
        dict(frame.f_locals)
        #return(frame.f_locals)
    else:
        print 'no exception available !'

def dict(d,maxindent=3,indent=0,
         INDENT=INDENT):

    """ dict(d,maxindent,indent) -- show dict d with given indentation (=0)
    """

    if hasattr(d,'items'):
        print indent*INDENT+'{'
        if indent < maxindent:
            items = d.items()
            items.sort()
            for k,v in items:
                print indent*INDENT+' ',k,':'
                try:
                    print_here = dict(v,maxindent,indent+1)
                    if print_here:
                        s = repr(v)
                        if len(s) > 40: s = s[:40] + '...'
                        print (indent+1)*INDENT,s
                except: 
                    print (indent+1)*INDENT,'*exception*'
        else:
            print indent*INDENT,'...'
        print indent*INDENT+'}'
        return None
    else:
        return 'Error: no items-method'

def seq(l,maxindent=10,indent=0):

    """ seq(l,maxindent=10,indent=0) 
        -- show sequence l with given indentation (=0), limiting
            the indent-depth at maxindent (=10)
    """

    try:
        len(l)
        if type(l) == type('') or indent > maxindent: 
            raise TypeError
        for i in l:
            try:
                seq(i,maxindent,indent+1)
            except ValueError: 
                print '*exception*',
        print indent*' |'
        return
    except TypeError:
        print indent*' |',
        s = repr(l)
        if len(s) > 40: s = s[:40] + '...'
        print s

#t = (1,2,3,(4,5,6),(3,(4,5,6),(3,4)))
#t = t + t
#seq(t)

def modules():

    """ modules() -- pretty print a list of loaded modules and packages;
        cached miss entries in sys.modules are not shown.
    """
    l = sys.modules.items()
    l.sort()
    print 'Loaded modules and packages:'
    for k,v in l:
        p = string.split(k,'.')
        for i in range(len(p)-1):
            p[i] = '   '
        n = string.join(p,'')
        if v is not None:
            if hasattr(v,'__path__'):
                print ' %s[%s]' % (string.join(p[:-1],''),p[-1])
            else:
                print ' %s' % (n)

