""" NewBuiltins - Installs (most of) the mx.Tools add-ons for Python
                  as Python builtins or in the sys module.

    The installation is done upon import, so that you only need
    to include the line 'import mx.Tools.NewBuiltins' at the top of your
    script to have the add-ons available for use in the script.

    Copyright (c) 2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.
"""
import sys,types,operator
import Tools

# Optional intra-package tools
try:
    from mx.DateTime import DateTimeFrom
except ImportError:
    DateTimeFrom = None

# Enable debugging output
_debug = 0

# Helper
def install_objects(namespace, objects,

                    DictType=types.DictType):

    """ Install all the given objects in namespace.

        Doesn't overwrite anything already defined in namespace.
        
    """
    for obj in objects:
        try:
            name = obj.__name__
        except AttributeError:
            try:
                name, obj = obj
            except (TypeError, ValueError):
                name = repr(obj)
        if name[:2] != '__':
            if namespace.has_key(name):
                if _debug:
                    try:
                        import warnings
                    except ImportError:
                        pass
                    else:
                        warnings.warn('mxTools builtin %s would overwrite existing '
                                      'builtin; not installed' % name,
                                      RuntimeWarning)
            else:
                namespace[name] = obj

### Note that undocumented functions may well disappear in
### future releases !!!

# New APIs and objects that go into __builtins__
install_objects(__builtins__,
                (Tools.NotGiven,
                 ('True', Tools.True),	# already defined in Python >= 2.2.x !
                 ('False', Tools.False),# already defined in Python >= 2.2.x !
                 Tools.acquire, 
                 Tools.attrlist,
                 Tools.count, 
                 Tools.defined,
                 Tools.dict,		# already defined in Python >= 2.2.x !
                 Tools.exists,
                 Tools.extract,
                 Tools.findattr,
                 Tools.forall, 
                 Tools.frange,          # undocumented
                 Tools.get, 
                 Tools.ifilter,
                 Tools.index, 
                 Tools.indices, 
                 Tools.invdict,
                 Tools.irange, 
                 Tools.iremove,
                 Tools.issequence,      # undocumented
                 Tools.lists, 
                 Tools.mapply,
                 Tools.method_mapply, 
                 #Tools.mget,           # old
                 #Tools.mgetattr,       # old
                 Tools.napply,
                 #Tools.optimization,   # moved to sys
                 Tools.projection,      # undocumented
                 Tools.range_len,
                 Tools.reval,
                 Tools.reverse, 
                 Tools.setdict,
                 Tools.sign,
                 Tools.sizeof, 
                 Tools.sortedby,        # undocumented
                 Tools.trange,
                 #Tools.trange_len,     # old
                 Tools.truth,
                 ('boolean', Tools.truth), # defined as bool() in Python >= 2.2.x !
                 Tools.tuples,
                 #Tools.verbosity,      # moved to sys
                 #Tools.xmap,           # no longer supported
                 ('binary', buffer),
                 )
                )

# Optional additional builtins
if DateTimeFrom is not None:
    install_objects(__builtins__, (('datetime', DateTimeFrom),))

# New APIs for the sys module
install_objects(sys.__dict__,
                (Tools.optimization, 
                 Tools.verbosity,
                 Tools.debugging,
                 Tools.interactive,
                 Tools.cur_frame,
                 Tools.makeref,
                 )
                )

# All other APIs are available through the Tools package, e.g
# Tools.docstring, etc.
