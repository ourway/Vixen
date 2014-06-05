""" ConfigFile -- Interface to simple template based configuration files.

    The format of these files is as follows:

    globalvar = 2

    [ABC]
    a = 1
    b = abc.html
    c = text with spaces

    [DEF]
    a = 2
    b = a + 3
    c = a string

    Entries in square brackets indicate new subsections. Global
    variables may be set prior to starting any subsection. Emtpy lines
    and lines starting with '#' (comments) are ignored. Indentation is
    not necessary; lines can start at any column.

    Entries may span multiple lines by using '\' continuations
    at the line ends, e.g.

    [Continuation]
    a = first line\
        second line

    The lines are stripped of any white space before removing the
    trailing '\' and concatenating them. Comment lines are removed as
    well.

    To parse these files, a template in form of a class including
    subclasses (identifying the subsections) must be given to the
    reader. This template defines which sections and attributes are
    known. All others are rejected.  A sample template for the above
    looks like this:

    from mx.Misc.ConfigFile import *
    class Template(ConfigNamespace):

        global = IntegerEntry()

        class ABC(ConfigSection):
            a = IntegerEntry('0')
            b = StringEntry('default.html')
            c = StringEntry()

        class DEF(ConfigSection):
            a = IntegerEntry('0')
            b = EvalEntry('0')
            c = StringEntry('default value')

    The main class representing the global namespace of the ini file
    must have ConfigNamespace as baseclass. It may contain any number
    of ConfigSection subclasses each defining parsed attributes. 

    The ini file may only contain entries defined in this template.
    In case an unknown section is found, the main class is looked up
    for a ConfigSection subclass with name 'DefaultSection'. This
    section object is then taken as template for a new section
    of the given name.

    The same feature is available for attributes in sections. In case
    a given attribute is not found in the templates, the section's
    'DefaultAttribute' attribute is deepcopied and the used as
    attribute template.

    Needs mxTools to be installed.

    XXX Add support for long strings (including embedded control
        characters and spanning multiple lines)

    Copyright (c) 2000, Marc-Andre Lemburg; All Rights Reserved.
    Copyright (c) 2000-2008, eGenix.com Software GmbH; All Rights Reserved.
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

"""
import string,copy,re,types,exceptions,sys,os
import mx.Tools.NewBuiltins
from mx.Tools import freeze
import Namespace

# Print debug information ?
_debug = 0

### Errors

class Error(exceptions.StandardError):
    pass

### Helpers

shell_var = re.compile('(?:\$([a-zA-Z0-9._]+)|\${([^}]*)})')

def expand_vars(text,locals,globals,

                split=string.split,shell_var=shell_var):

    """ Expands all variables of the form $var or ${var} using
        the dictionaries locals,globals,os.environ in that order
        as database.

        Default value is the empty string, just like for shell
        environment variables.
        
    """
    while 1:
        m = shell_var.search(text)
        if not m:
            break
        g = m.groups()
        varpath = split(g[0] or g[1],'.')
        varname = varpath[0]
        # Find object with name varname
        value = locals.get(varname,None)
        if value is None:
            value = globals.get(varname,None)
            if value is None:
                value = os.environ.get(varname,'')
        # Now get the requested attribute
        for attr in varpath[1:]:
            try:
                value = getattr(value,attr)
            except AttributeError:
                raise Error,'attribute "%s" undefined' % attr
        # Reformat text by inserting value as string
        l,r = m.span()
        if isinstance(value,Entry):
            entry = value
            if entry.value is NotGiven:
                entry.parse(entry.default,locals,globals)
            value = entry.value
        text = text[:l] + str(value) + text[r:]
    return text

### Template entry fields

class Entry:

    """ Converts the value to another datatype depending on the
        .converters attribute.

        Each of those functions is applied to the value. The first one
        to not raise an exception succeeds.
        
    """
    # Value
    value = NotGiven

    # Default value
    default = ''

    # Converters to be tried; order is important the first successful
    # one wins
    converters = (int,float,str)


    def __init__(self,default=NotGiven):

        if default is not NotGiven:
            self.default = default

    def parse(self,text,locals,globals):

        """ Parse text according to the namespace dictionaries
            locals and globals.

            Sets self.value and returns the parsed value as well.
            
        """
        text = self.pre_process(str(text),locals,globals)
        for converter in self.converters:
            try:
                value = converter(text)
                break
            except:
                lastexc = sys.exc_info()[1]
        else:
            # Reraise the last exception
            raise lastexc
        lastexc = None
        self.value = value = self.post_process(value,locals,globals)
        return value

    def pre_process(self,text,locals,globals,

                    strip=string.strip,expand_vars=expand_vars):

        """ Preprocess the text value.

            Default behaviour is to strip the text and then
            apply variable expansion.

        """
        return expand_vars(strip(text),locals,globals)

    def post_process(self,value,locals,globals):

        """ Postprocess the value after conversion has been
            applied.

            The default behaviour is to leave it as it is.
        """
        return value

    def __str__(self):
        
        """ Return a stringified version of self.value.

            The default value is parsed in case no value has yet been
            set.

        """
        if self.value is NotGiven:
            self.parse(self.default,{},{})
        return str(self.value)

###

def integer_value(value):

    """ Convert value to an integer.

        Takes base indicators into account, such as 0x for base-16,
        0 for base-7.

    """
    return int(value, 0)

class IntegerEntry(Entry):

    """ Converts the value to an integer.
    """
    converters = (integer_value,)
        
class FloatEntry(Entry):

    """ Converts the value to a float.
    """
    converters = (float,)
        
class NumericEntry(Entry):

    """ Converts the value to a number (integer or float).
    """
    converters = (integer_value, float)
        
class StringEntry(Entry):

    """ Converts the value to a string.
    """
    converters = (str,)

def comma_list(text,

               strip=string.strip,split=string.split,map=map,tuple=tuple):

    return map(strip,split(text,','))

def spaced_list(text,

                strip=string.strip,split=string.split,map=map,tuple=tuple):

    return map(strip,split(text))

class TupleEntry(Entry):

    """ Converts the value to a tuple of strings.

        value must be a string with entries separated by ','. Entries
        are split at each occurance of ',' and then stripped of
        surrounding spaces.
        
    """
    converters = (comma_list,)

    def post_process(self,value,locals,globals):

        return tuple(value)

# Alias
StringTupleEntry = TupleEntry
CommaTupleEntry = TupleEntry

class ListEntry(Entry):

    """ Converts the value to a list of strings.

        value must be a string with entries separated by ','. Entries
        are split at each occurance of ',' and then stripped of
        surrounding spaces.
        
    """
    converters = (comma_list,)

# Alias
StringListEntry = ListEntry
CommaListEntry = ListEntry

class SpacedTupleEntry(TupleEntry):

    """ Converts the value to a tuple of strings.

        value must be a string with entries separated by
        whitespace. Entries are split at each occurance of whitespace;
        surrounding spaces is removed.

    """
    converters = (spaced_list,)

class SpacedListEntry(ListEntry):

    """ Converts the value to a list of strings.

        value must be a string with entries separated by
        whitespace. Entries are split at each occurance of whitespace;
        surrounding spaces is removed.

    """
    converters = (spaced_list,)

class FileEntry(Entry):

    """ Entry field for an OS file.
    """
    converters = (str,)

class PathEntry(Entry):

    """ Entry field for an OS path.

        Paths will always end with os.sep if given.
    """
    converters = (str,)

    def post_process(self,value,locals,globals):

        if value and value[-1] != os.sep:
            value = value + os.sep
        return value

class AbsoluteFileEntry(Entry):

    """ Entry field for an absolute OS pathname.

        The pathname will always start with os.sep if given.

    """
    converters = (str,)

    def post_process(self,value,locals,globals):

        if value and value[0] != os.sep:
            value = os.sep + value
        return value

class AbsolutePathEntry(Entry):

    """ Entry field for an absolute OS path.

        The pathname will always start and end with os.sep if given.

    """
    converters = (str,)

    def post_process(self,value,locals,globals):

        if value:
            if value[0] != os.sep:
                value = os.sep + value
            if value[-1] != os.sep:
                value = value + os.sep
        return value

class RelativePathEntry(PathEntry):

    """ Entry field for relative paths.
    
        The path stored is the result of joining the given parameter
        with a basepath. basepath is subject to variable expansion at
        parsing time.
        
    """
    def __init__(self,basepath,default=NotGiven):

        self.basepath = basepath
        PathEntry.__init__(self,default)

    def post_process(self,value,locals,globals):

        return os.path.join(expand_vars(self.basepath,locals,globals),value)

class RelativeFileEntry(FileEntry):

    """ Entry field for relative pathnames to files.
    
        The path stored is the result of joining the given parameter
        with a basepath. basepath is subject to variable expansion at
        parsing time.
        
    """
    def __init__(self,basepath,default=NotGiven):

        self.basepath = basepath
        PathEntry.__init__(self,default)

    def post_process(self,value,locals,globals):

        return os.path.join(expand_vars(self.basepath,locals,globals),value)

class ExistingPathEntry(PathEntry):

    """ Checks value to point to an existing OS path.

        Raises an exception if the path does not exist.
    """
    def post_process(self,value,locals,globals):

        if value and value[-1] != os.sep:
            value = value + os.sep
        if not os.path.exists(value):
            raise Error,'non existing path "%s"' % value
        return value

class ExistingFileEntry(FileEntry):

    """ Checks value to point to an existing file.

        Raises an exception if the file does not exist.
    """
    def post_process(self,value,locals,globals):

        if not value or not os.path.exists(value):
            raise Error,'non existing file "%s"' % value
        return value

class ExistingRelativePathEntry(RelativePathEntry):

    """ Entry field for relative paths.
    
        The path stored is the result of joining the given parameter
        with a basepath.  Raises an exception if the path does not
        exist.
        
    """
    def post_process(self,value,locals,globals):

        value = os.path.join(expand_vars(self.basepath,locals,globals),value)
        if not os.path.exists(value):
            raise Error,'non existing path "%s"' % value
        return value

class URLEntry(StringEntry):

    """ Entry field for URLs.

        The field takes a default value as argument. 

        Needs mxHTMLTools to be installed.

    """
    def post_process(self,value,locals,globals):

        from mx import HTMLTools
        return HTMLTools.URL(value)

class RelativeURLEntry(URLEntry):

    """ Entry field for relative URLs.

        A base URL can be set which is then urljoined with the
        value given. The field also takes a default value.

        Needs mxHTMLTools to be installed.

    """
    def __init__(self,baseurl='',default=NotGiven):

        self.baseurl = baseurl
        StringEntry.__init__(self,default)

    def post_process(self,value,locals,globals):

        from mx import HTMLTools
        return HTMLTools.urljoin(expand_vars(self.baseurl,locals,globals),
                                 value)

class AbsoluteURLEntry(RelativeURLEntry):

    """ Entry field for absolute URLs.

        A base URL can be set which is then urljoined with the
        value given. The field also takes a default value as second
        argument.
    """
    def post_process(self,value,locals,globals):

        url = RelativeURLEntry.post_process(self,value,locals,globals)
        if not url.absolute:
            raise Error,'need an absolute URL: "%s"' % url
        return url

class DateEntry(Entry):

    """ Date entry field.

        The value is stored using a DateTime instance. A time part is
        ignored.

        Needs mxDateTime to be installed.

    """
    def post_process(self,value,locals,globals):

        from mx.DateTime.Parser import DateFromString
        return DateFromString(value)

class DateTimeEntry(Entry):

    """ Date/time entry field.

        The value is stored using a DateTime instance.

        Needs mxDateTime to be installed.

    """
    def post_process(self,value,locals,globals):

        from mx.DateTime.Parser import DateTimeFromString
        return DateTimeFromString(value)

class TimeEntry(Entry):

    """ Time entry field.

        The value is stored using a DateTimeDelta instance. A date
        part is ignored.

        Needs mxDateTime to be installed.

    """
    def post_process(self,value,locals,globals):

        from mx.DateTime.Parser import TimeFromString
        return TimeFromString(value)

class DateTimeDeltaEntry(Entry):

    """ Date/time delta entry field.

        The value is stored using a DateTimeDelta instance.

        Needs mxDateTime to be installed.

    """
    def post_process(self,value,locals,globals):

        from mx.DateTime.Parser import DateTimeDeltaFromString
        return DateTimeDeltaFromString(value)

class RelativeDateTimeEntry(Entry):

    """ Relative date/time entry field.

        The value is stored using a RelativeDateTime instance.

        Needs mxDateTime to be installed.

    """
    def post_process(self,value,locals,globals):

        from mx.DateTime.Parser import RelativeDateTimeFromString
        return RelativeDateTimeFromString(value)

class EvalEntry(Entry):

    """ Allows simple calculations to be done using the
        current locals (the symbols defined in the class
        where the entry is located) and globals.

    """
    def parse(self,text,locals,globals,

              eval=eval):

        self.value = eval(text,locals,globals)
        return self.value
        
class SafeEvalEntry(Entry):

    """ Allows simple calculations to be done using the
        current locals (the symbols defined in the class
        where the entry is located) and globals.

        Builtins are not available.

    """
    def parse(self,text,locals,globals,

              reval=reval):

        self.value = reval(text,locals,globals)
        return self.value
        
class DictEntry(Entry):

    """ Allows the construction of a Python dictionary.

        The entries value is taken as list of key: value pairs which
        are evaluated in the current locals (the symbols defined in
        the class where the entry is located) and globals.

        Parsing is left to the Python interpreter. The needed curly
        brackets {} are added by the parsing method.

        Sample:

        dict = 'a': (1,2,3), 'b': (3,4,5)

    """
    def parse(self,text,locals,globals):

        self.value = eval('{' + text + '}',locals,globals)
        return self.value

### Namespace containers

class ConfigNamespace(Namespace.Namespace):
    
    # This attribute may be set to allow new sections to be
    # created by the ini-file editor. The parser will use this
    # class to instantiate those sections.
    DefaultSection = None

    # This attribute may be set to allow new attributes to be
    # created by the ini-file editor. The parser will use this
    # object as template for the new attributes by deepcopying
    # it.
    DefaultAttribute = None

    def __init__(self,

                 getattr=getattr,
                 skip_types=(types.ModuleType,
                             types.IntType,
                             types.StringType,
                             types.NoneType,
                             ),
                 del_types=(types.FunctionType,
                            types.MethodType,
                            types.BuiltinFunctionType,
                            types.BuiltinMethodType,),
                 deepcopy=copy.deepcopy,ClassType=types.ClassType):

        # Localize class attributes in the instance dict
        classobj = self.__class__
        freeze(classobj)
        dict = self.__dict__
        dict.update(classobj.__dict__)

        # Fixup attributes
        for name,obj in dict.items():

            if name[:1] == '_ ':
                # Delete all special attributes
                del dict[name]
            
            objtype = type(obj)
            
            if objtype is ClassType:
                # Handle classes
                if name != 'DefaultSection' and \
                   issubclass(obj,ConfigSection):
                    # Instantiate ConfigSections
                    dict[name] = obj()
                # leave all others as classes

            elif objtype in del_types:
                # Delete these types
                del dict[name]

            elif objtype in skip_types:
                # Skip these types
                pass

            else:
                # Deepcopy everything else
                try:
                    dict[name] = deepcopy(obj)
                except copy.error,why:
                    raise Error,\
                          'namespace entry "%s" could not be copied: %s' % \
                          (name,why)

    #
    # Dictionary like interface (we hide the internally used attributes)
    #
                
    def _items(self):

        items = []
        append = items.append
        for k,v in self.__dict__.items():
            if k[:1] == '_' or \
               k in ('DefaultSection', 'DefaultAttribute', 'baseobj'):
                continue
            append((k,v))
        return items

    def _keys(self):

        items = []
        append = items.append
        for k,v in self.__dict__.items():
            if k[:1] == '_' or \
               k in ('DefaultSection', 'DefaultAttribute', 'baseobj'):
                continue
            append(k)
        return items

    def _values(self):

        items = []
        append = items.append
        for k,v in self.__dict__.items():
            if k[:1] == '_' or \
               k in ('DefaultSection', 'DefaultAttribute', 'baseobj'):
                continue
            append(v)
        return items

    def _dictionary(self):

        d = {}
        d.update(self.__dict__)
        # Remove internal attributes
        for k in d.keys():
            if k[:1] == '_' or \
               k in ('DefaultSection', 'DefaultAttribute', 'baseobj'):
                del d[k]
        return d

class ConfigSection(ConfigNamespace):
    pass

###

parse_section = re.compile('\[([a-zA-Z_][a-zA-Z_0-9]*)\]')
parse_setattr = re.compile('([a-zA-Z_][a-zA-Z_0-9]*)[ \t]*=[ \t]*(.*)')

class ConfigFile:

    """ Configuration file reader.

        Takes a template (a ConfigNamespace subclass) as input which
        defines sections using classes. Sections may include instances
        of Entry as attributes. These are then used to process the
        file input.

        The template is (deep-)copied and placed into the instance
        variable .data (a ConfigNamespace instance) prior to reading
        the file. Section classes are replaced with ConfigSection
        instances.

        After successful reading the file, the configuration
        information is available through this variable.

        Errors are indicated by exceptions of type Error. These always
        have values (line_number, explanation) where line_number is 0
        for errors which do not refer to one specific line in the
        file.
        
    """
    data = None                         # configuration namespace

    def __init__(self,template):

        self.template = template
        self.reset()

    def reset(self,

              deepcopy=copy.deepcopy,ClassType=types.ClassType,
              ModuleType=types.ModuleType):

        """ Reset the object to its initial state.

            This initializes self.data to a template instance.

        """
        self.data = self.template()

    def read(self,file,

             strip=string.strip,deepcopy=copy.deepcopy):

        """ Read and parse the open file.

            The configuration is stored in the instance variable
            .data.

        """
        context = {}
        sectionname = ''
        data = self.data                # Configuration object
        section = data                  # Current section object
        globals = data.__dict__         # Global namespace
        locals = globals                # Local namespace
        lineno = 0
        if _debug:
            print 'Reading config file:'
        while 1:
            line = file.readline()
            lineno = lineno + 1
            if not line:
                break
            line = strip(line)
            if not line or line[0] == '#':
                # Comment or emtpy line: ignore
                continue

            if _debug:
                print ' read %s' % repr(line)

            # Continuation
            current_lineno = lineno
            while line[-1] == '\\':
                nextline = file.readline()
                lineno = lineno + 1
                if not nextline:
                    # EOF: end of continuation
                    line = line[:-1]
                    break
                nextline = strip(nextline)
                if not nextline:
                    # Empty line: end of continuation
                    line = line[:-1]
                    break
                if nextline[0] == '#':
                    # Comment: ignore
                    continue
                if _debug:
                    print ' read continuation %s' % repr(nextline)
                # Add nextline to line
                line = line[:-1] + nextline

            if _debug:
                print ' processing %s' % repr(line)

            m = parse_section.match(line)
            if m:
                # Start a new section
                sectionname = m.groups()[0]
                section = getattr(data,sectionname,None)
                if section is None:
                    if data.DefaultSection:
                        # Instantiate default section for use as
                        # section object and register in data
                        section = data.DefaultSection()
                        setattr(data,sectionname,section)
                    else:
                        raise Error,(current_lineno,
                                     'unknown section "%s"' % 
                                     sectionname)
                #print 'Switched to section:',sectionname
                locals = section.__dict__
                continue

            m = parse_setattr.match(line)
            if m:
                # Add a new attribute
                name,value = m.groups()
                entry = locals.get(name,None)
                if sectionname:
                    attrname = sectionname + '.' + name
                else:
                    attrname = name
                if entry is None:
                    if section.DefaultAttribute:
                        # Instantiate default attribute for use as
                        # attribute object and register in section
                        entry = deepcopy(section.DefaultAttribute)
                        setattr(section,name,entry)
                    else:
                        raise Error,(current_lineno,
                                     'unknown attribute: "%s"' % attrname)
                if not isinstance(entry, Entry):
                    # Since we replace the parsed entries with their parsed
                    # value any occurance of non-Entry instances point
                    # to a duplicate definition of an entry
                    raise Error,(current_lineno,
                                 'duplicate attribute definition for "%s"' %
                                 attrname)
                try:
                    entry.parse(value,locals,globals)
                except:
                    raise Error,(current_lineno,
                                 'invalid attribute value for "%s" (%s: %s)' %
                                 (attrname,
                                  sys.exc_info()[0],sys.exc_info()[1]))
                # Replace with parsed value
                locals[name] = entry.value
                continue

            # The line doesn't have a valid syntax: ignore it
            if _debug:
                print 'Ignoring invalid config file line %i: %s' % \
                      (current_lineno,
                       repr(line))

        # Check for missing entries and replace with parsed values
        for name,obj in globals.items():

            if isinstance(obj,Entry):
                if obj.value is not NotGiven:
                    globals[name] = obj.value
                else:
                    try:
                        obj.parse(obj.default,locals,globals)
                        globals[name] = obj.value
                    except:
                        raise Error,\
                              (0,
                               'invalid default attribute '
                               'value for global "%s" (%s)' %
                               (name,str(sys.exc_info()[1])))

            elif isinstance(obj,ConfigSection):
                locals = obj.__dict__
                sectionname = name
                for name,obj in locals.items():
                    if isinstance(obj,Entry):
                        if obj.value is not NotGiven:
                            locals[name] = obj.value
                        else:
                            try:
                                obj.parse(obj.default,locals,globals)
                                locals[name] = obj.value
                            except:
                                import traceback; traceback.print_exc()
                                raise Error,\
                                      (0,
                                       'invalid default attribute '
                                       'value for local "%s" (%s)' %
                                       (name,str(sys.exc_info()[1])))


### Test
        
if __name__ == '__main__':

    class Template(ConfigNamespace):

        import sys

        globalvar = IntegerEntry(1)

        # New attributes in the global section are strings
        DefaultAttribute = StringEntry('')

        class ABC(ConfigSection):
            a = IntegerEntry('0')
            b = StringEntry('default.html')
            c = StringEntry()
            d = StringTupleEntry('a,b')
            path = ExistingPathEntry('.')

            # Use this as template for new attributes
            DefaultAttribute = RelativePathEntry('..','')

        class DEF(ConfigSection):
            a = IntegerEntry('0')
            b = EvalEntry('0')
            c = StringEntry('default value')
            d = RelativePathEntry('$ABC.b','HOME')
            g = IntegerEntry('0')
            continuation = CommaTupleEntry('')
            databases = DictEntry('')
            timeout = TimeEntry('0:15:00.23')

        # Default section
        DefaultSection = ABC

    text = """\
    # Luckily we don't have to pay attention to proper indentation
    # or whether strings have quotes or not... the template knows
    # what to do.

    globalvar = 2

    # New global attribute
    test = text

    [ABC]
    a = 1
    b = abc.html
    c = text with spaces
    d = heinz, kunz, philipp
    path = /tmp

    # A new attribute
    new = .cshrc

    [DEF]
    a = 2
    b = a + 3
    c = $PWD
    d = home

    continuation = first line, \\
                   # Comment should not hurt
                   second line, \\

                   # Invalid syntax:
                   third line \\

    databases = 'iODBC': (sys,sys.exit,('c',1,2)), \\
                'Adabas': (sys,sys.exit,('x','y','z'))

    [NewSection]
    a = 3

    """

    import cStringIO

    f = cStringIO.StringIO(text)
    cf = ConfigFile(Template)
    cf.read(f)
    
