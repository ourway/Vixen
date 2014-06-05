""" Namespace objects.

    Copyright (c) 1998-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2008, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.
"""
import string,types
import mx.Tools.NewBuiltins
from mx.Tools import freeze, attributes

class Namespace:

    """ Base class for Namespaces.

        Instances of this namespace can store arbitrary attributes,
        which are stored in the instances dictionary. They are then
        available via attribute lookup, e.g. ns.attr, and index
        lookup, e.g. ns['attr'].

        The Namespaces support acquisition. To link the object to
        another object, set self.baseobj to the other
        object. Attributes not found in the Namespace instance are
        then looked up in the other object as well.

        NOTE:

        All methods and internal attributes must start with an
        underscore. Namespace attributes must *not* start with an
        underscore to prevent naming collisions with internal
        variables and methods.  Names with leading underscore can
        *not* be acquired.

    """

    def __init__(self, **kws):

        """ Initializes the namespace with the attributes given
            as keywords.
        """
        if kws:
            self.__dict__.update(kws)
    
    def _clear(self,save=(),recursive=0,

               getattr=getattr):

        """ Clears the namespace.

            The attributes named in save are not cleared. Per default
            all attributes are cleared. You may want to save the
            baseobj attribute in case you use it.

            Class variables are not cleared this way, but overriding
            instance variables do get deleted.

            If recursive is true (default is false), the namespace is
            cleared recursively, meaning that all Namespace instances
            contained in it are also cleared.

        """
        d = {}
        for attr in save:
            d[attr] = getattr(self,attr)
        # Clear the old instance dictionary (recursively) so that it
        # can be garbage collected
        if recursive:
            for obj in self.__dict__.items():
                if isinstance(obj, Namespace):
                    obj._clear()
        obj = None
        self.__dict__.clear()
        # Assing the new one
        self.__dict__ = d

    def _update(self, other_namespace,

                DictType=types.DictType,type=type):

        """ Updates the namespace dictionary with the new entries
            taken from the object other_namespace.

            other_namespace can either be a dictionary or another
            Namespace object.

        """
        if type(other_namespace) is DictType:
            self.__dict__.update(other_namespace)
        else:
            self.__dict__.update(other_namespace.__dict__)

    def _load(self, other_namespace, save=(),
              ignore_types=(types.BuiltinMethodType,
                            types.ClassType,
                            types.MethodType,
                            types.FunctionType),

              DictType=types.DictType,type=type):

        """ Updates the namespace with the updated entries taken from
            the object other_namespace provided that the entries already
            exist in the namespace dictionary

            other_namespace can either be a dictionary or another
            Namespace object.

            Attributes listed in save are not overwritten. New values
            having one of the types listed in ignore_types are also
            ignored.

        """
        if type(other_namespace) is DictType:
            items = other_namespace.items()
        else:
            items = other_namespace._items()
        d = self.__dict__
        exists = d.has_key
        for k, v in items:
            if exists(k):
                if k in save or \
                   type(v) in ignore_types:
                    continue
                d[k] = v
        exists = None
        d = None

    def _load_file(self, filename):

        """ Load the namespace from the file filename.
        """
        execfile(filename, self.__dict__)

    def _copy_to(self, other_namespace,

                 DictType=types.DictType,type=type):

        """ Copy the namespace contents into the dictionary or Namespace
            instance other_namespace.
            
        """
        if type(other_namespace) is DictType:
            other_namespace.update(self.__dict__)
        else:
            other_namespace._update(self.__dict__)

    def _format(self, template, recursive=0):

        """ Format the text template using the namespace contents.

            template must be a text using Python string placeholders,
            e.g. "%(attrname)s" or "%(attrname)r". Formatting is done
            using all available attributes of the namespace (including
            class attributes).

            If recursive is true, the formatting is applied recursively
            (as long as the string '%(' occurs in the template), i.e.
            the Namespace attributes may also contain Python string
            placeholders.
            
        """
        if not recursive:
            return template % attributes(self)
        dict = attributes(self)
        while string.find(template, '%(') >= 0:
            template = template % dict
        return template

    def _attributes(self):

        """ Return all available attributes as dictionary.

            The dictionary includes all class and instance attributes.
            
        """
        return attributes(self)

    def _dictionary(self):

        """ Returns the current namespace contents as dictionary.

            The dictionaries values should be considered read-only in
            case they are mutable.

        """
        return self.__dict__.copy()

    def _copy(self):

        """ Returns a shallow copy of the current namespace.

            See the standard Python module "copy" for details on the
            copying mechanism.

        """
        import copy
        return copy.copy(self)

    def _deepcopy(self):

        """ Returns a deep copy of the current namespace.

            See the standard Python module "copy" for details on the
            copying mechanism.

        """
        import copy
        return copy.deepcopy(self)

    def _clone(self):

        """ Returns a shallow copy of the instance.

            This is different from the ._copy() method in that
            ._update() is used to copy the contents of the instance to
            the new instance.
        
        """
        obj = self.__class__()
        obj._update(self.__dict__)
        return obj

    ### Index interface

    def __getitem__(self,name,

                    getattr=getattr):

        """ Index interface to the namespace.

            Raises IndexErrors in case an attribute is not found.

        """
        try:
            return getattr(self, name)
        except AttributeError,why:
            raise IndexError,why
        
    def __setitem__(self,name,value,

                    setattr=setattr):

        """ Index interface to the namespace.
        """
        return setattr(self,name,value)

    def __len__(self):

        """ Return the number of instance attributes stored in the
            namespace.
        """
        return len(self.__dict__)

    def __nonzero__(self):

        """ Returns 1/0 depending on whether any instance attributes
            are defined in the namespace.

            An empty Namespace is false, if it contains at least one
            entry it is true.
            
        """
        return (len(self.__dict__) > 0)

    ### Dictionary like interface to the instance dictionary

    def _items(self):

        """ Returns a list of tuples (attrname, attrvalue) for
            all (instance) attributes stored in the object.
        """
        return self.__dict__.items()

    def _keys(self):

        """ Returns a list of attribute names for
            all (instance) attributes stored in the object.
        """
        return self.__dict__.keys()

    def _values(self):

        """ Returns a list of attribute values for
            all (instance) attributes stored in the object.
        """
        return self.__dict__.values()

    def _has_key(self, key):

        """ Returns 1/0 depending on whether the object has
            an instance attribute key or not.

            Note that class attributes cannot be queried this way.
            
        """
        return self.__dict__.has_key(key)

    # Alias
    _hasattr = _has_key

    def _get(self,key,default=None):

        """ Returns the value of attribute key, or default if no
            such attribute is defined.
        """
        return self.__dict__.get(key,default)

    # Alias
    _getattr = _get

    ### Additional methods:

    def _extract(self,names,defaults=(),

                 extract=extract):

        """ Extract a list of named objects from the namespace.
        
            defaults may be given as sequence of the same size as
            names to provide default values in case names are not
            found in the namespace.

            Only the instance dictionary is scanned, the class
            variables are not available through this mechanism.

        """
        return extract(self.__dict__,names,defaults)

    def _prefixgroup(self,prefix,nonzero=0,wholename=0):

        """ Find all attributes having prefix as common prefix and return
            a dictionary mapping the attribute suffixes (the prefix
            is removed) to their values.
            
            If nonzero is set, then only fields with non-zero value
            are included in the dictionary

            If wholename is true, the prefix is not removed from the
            attribute names.

        """
        plen = len(prefix)
        d = {}
        if not nonzero and not wholename:
            # Shortcut for the default settings
            for k,v in self.__dict__.items():
                if k[:plen] == prefix:
                    d[k[plen:]] = v
        else:
            for k,v in self.__dict__.items():
                if k[:plen] == prefix:
                    if nonzero and not v:
                        continue
                    if wholename:
                        d[k] = v
                    else:
                        d[k[plen:]] = v
        return d

    ### For debugging purposes:

    def __repr__(self,

                 join=string.join,id=id):

        keys = self.__dict__.keys()
        keys.sort()
        return '<%s.%s (%s) at 0x%x>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            join(keys,','),
            id(self))

    def __str__(self,

                join=string.join,id=id):

        items = self.__dict__.items()
        items.sort()
        l = ['%s.%s at 0x%x:' % (self.__class__.__module__,
                                 self.__class__.__name__,
                                 id(self))]
        for k,v in items:
            try:
                s = repr(v)
            except (ValueError, TypeError, AttributeError):
                s = '*** repr(value) failed ***'
            else:
                if len(s) > 200:
                    s = s[:200] + '... (truncated, full length = %i)' % len(s)
            l.append('    %-10s %s' % (k + ':', s))
        return string.join(l,'\n')

###

class DefaultMixin:

    """ Mixin that provides default attribute values.

        The namespace returns _default for all undefined attributes
        (except the ones that start with an underscore, see
        __getattr__). The _default is defined as '' for this class.

        The acquisition feature is *not* available for instances of this
        class.

    """
    _default = ''

    def __getattr__(self,name):

        """ Return self._default for all undefined attributes that don't
            start with an underscore.

            For attributes that start with an underscore, raise an
            AttributeError. This is especially important if the
            objects are to be pickled, since the pickle mechanism
            queries a few methods on the objects, which it then calls.
            
        """
        if name[0] == '_':
            raise AttributeError,name
        return self._default

###

class NamespaceWithDefault(DefaultMixin,Namespace):

    """ Namespace class with an infinite number of attributes.

        The namespace returns _default for all undefined attributes
        (except the ones that start with an underscore, see
        __getattr__). The _default is defined as '' for this class.

        The acquisition feature is *not* available for instances of this
        class.

    """

freeze(NamespaceWithDefault)

###

class AcquisitionMixin:

    """ Mixin that acquires unknown attributes from a .baseobj
        (if set)

    """
    baseobj = None              # Base object ("containing" this object)

    # Implicit acquisition
    __getattr__ = acquire       # Use the (new) builtin acquire() to implement
                                # the acquisition mechanism

###

class NamespaceWithAcquisition(AcquisitionMixin, Namespace):

    """ Namespace class with acquisition mechanism.

        The namespace fetches values for all undefined attributes
        (except the ones that start with an underscore, see
        __getattr__) from the .baseobj, if defined.

    """
    
freeze(NamespaceWithAcquisition)

###

class _NotFound:
    pass
_NotFound = _NotFound()

class FormatNamespaceMixin:

    """ This mixin makes a Namespace class conform to the Python
        format string mechanism.

        The following format specifiers are supported:

        %(attribute)s		- gives the string representation
        			  of .attribute
        %(<eval-string>)s	- evaluates the <eval-string> in the
        			  Namespace dictionary and returns
                                  the string representation

        All standard Python string formatting output types are
        supported, provided that the attribute or evaluation result
        can be converted to these types.
                                  
    """

    def __getitem__(self, item,

                    _NotFound=_NotFound):

        obj = getattr(self, item, _NotFound)
        if obj is not _NotFound:
            return obj
        return eval(item, self.__dict__)

###

class FormatNamespace(FormatNamespaceMixin,
                      Namespace):

    """ Namespace class which supports the Python format string
        lookup mechanism.

        These Namespaces can be used in 'format string' % namespace
        formatting.

        The following format specifiers are supported:

        %(attribute)s		- gives the string representation
        			  of .attribute
        %(<eval-string>)s	- evaluates the <eval-string> in the
        			  Namespace dictionary and returns
                                  the string representation
                                  
        All standard Python string formatting output types are
        supported, provided that the attribute or evaluation result
        can be converted to these types.
                                  
    """
    pass

freeze(FormatNamespace)
