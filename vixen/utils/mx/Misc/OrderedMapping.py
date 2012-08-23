#! /usr/bin/python

""" OrderedMapping - A compromise between a dictionary and a list.

    Copyright (c) 1998-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.
"""
import types,string,operator
from mx.Tools import freeze
import mx.Tools.NewBuiltins

class OrderedMapping:

    """ OrderedMapping - A compromise between a dictionary and a list.

        The object stores the keys in a list and a the items (key,value)
        in a dictionary. Order in the dictionary is implied by the key
        list. New dictionary keys are appended to the key list and thus
        newer keys have higher order.

        Note that you can manipulate the ordering with several methods.
        Also, assignment, retrieval and deletion using the order integers
        is possible.

        The object differentiates between queries referring to order and
        ones referring to keys by checking the query index's
        type. Integers are interpreted as order index and all other types
        as keys.

    """
    def __init__(self, presets=None):

        """ Create an OrderedMapping object.

            presets may be given as list of tuples to initialize the
            object with (key,value) pairs. The objects are inserted in
            order given by in presets object.

        """
        self.list = []          # list of keys
        self.dict = {}          # dict
        # init
        if presets is not None:
            if hasattr(presets, 'items'):
                items = presets.items()
            else:
                items = presets
            self.additems(items)

    def additems(self, items):

        """ Adds the (key, value) pairs in items to the object
            in the order they are specified.

        """
        l = self.list
        append = l.append
        d = self.dict
        has_key = d.has_key
        for key, value in items:
            if has_key(key):
                raise ValueError,\
                      'more than one value for key %s' % repr(key)
            append(key)
            d[key] = value

    def __repr__(self): 

        """ Returns a string representation of the object comparable to
            to the dictionary built-in object.

        """
        l = []
        for key in self.list:
            value = self.dict[key]
            l.append(repr(key)+': '+repr(value))
        return '{' + string.join(l,', ') + '}'

    def __cmp__(self, other):

        """ Compares the object against another OrderedMapping object
            or dictionary.

            Ordering of the contents is important when comparing
            OrderedMapping objects. It is not when comparing to
            dictionaries.

        """
        if isinstance(other,OrderedMapping):
            return cmp((self.list,self.dict), (other.list,other.dict))
        else:
            return cmp(self.dict,other)

    def __len__(self):

        """ Returns the number of object stored.
        """
        return len(self.list)

    def __getitem__(self, keyindex,

                    IntType=types.IntType): 

        """ Returns the object at position keyindex.

            keyindex may either be an integer to index an object by
            position or an arbitrary key object which is then used for
            dictionary like lookup.

        """
        # runtime O(1)
        if type(keyindex) is IntType:
            # om[0]
            return self.dict[self.list[keyindex]]
        else:
            # om['bar']
            return self.dict[keyindex]

    def __setitem__(self, keyindex, value,

                    IntType=types.IntType):

        """ Sets the position keyindex to value.

            keyindex may either be an integer to index an object by
            position or an arbitrary key object which is then used for
            dictionary like lookup.

            In the latter case, if no key is found, value is appended
            to the object.

        """
        # runtime O(1)
        if type(keyindex) is IntType:
            # om[0] = 'foo': update value
            self.dict[self.list[keyindex]] = value
        else:
            # om['bar'] = 'foo'
            if self.dict.has_key(keyindex):
                # update value
                self.dict[keyindex] = value
            else:
                # append/add value
                self.dict[keyindex] = value
                self.list.append(keyindex)

    def __delitem__(self, keyindex,

                    IntType=types.IntType): 
        
        """ Deletes the object at position keyindex.

            keyindex may either be an integer to index an object by
            position or an arbitrary key object which is then used for
            dictionary like lookup.

        """
        if type(keyindex) is IntType:
            # del om[0]; runtime O(1)
            key = self.list[keyindex]
            del self.dict[key]
            del self.list[keyindex]
        else:
            # del om['foo']; runtime O(n)
            del self.dict[keyindex]
            self.list.remove(keyindex)

    def __getslice__(self, i, j):

        """ Return the slice [i:j] of the object as OrderedMapping
            instance.
        
        """
        # om[1:3]; runtime O(j-i)
        om = OrderedMapping()
        om.list = keys = self.list[i:j]
        for key in keys:
            om.dict[key] = self.dict[key]
        return om

    def __setslice__(self, i, j, other):

        """ Set the slice [i:j] of the object to the contents of the
            OrderedMapping object other.
        
        """
        # om[1:3] = other OrderedMapping
        if not isinstance(other,OrderedMapping):
            raise TypeError,'assigned object must be an OrderedMapping'
        # del om[1:3]
        keys = self.list[i:j]
        for key in keys:
            del self.dict[key]
        # insert new mappings
        otherkeys = other.list
        self.list[i:j] = otherkeys
        for key in otherkeys:
            self.dict[key] = other.dict[key]

    def __delslice__(self, i, j):

        """ Delete the slice [i:j] of the object.
        
        """
        # del om[1:3]
        keys = self.list[i:j]
        for key in keys:
            del self.dict[key]
        del self.list[i:j]

    def __add__(self, other):

        """ Concatenate the contents of an OrderedMapping object other
            to self and return the result as new OrderedMapping object.
                    
        """
        # self + other OrderedMapping
        if not isinstance(other,OrderedMapping):
            raise TypeError,'other object must be an OrderedMapping'
        om = OrderedMapping()
        om.dict = self.dict.copy()
        for key in other.list:
            if om.has_key(key):
                raise ValueError,\
                  'result would have more than one value for key ' + repr(key)
        om.dict.update(other.dict)
        om.list = self.list + other.list
        return om
    __radd__ = __add__

    def append(self, item):
        
        """ Append an item (key, value) to the object and return
            the position of the new value.

            The item is addressable under key and the position
            returned by the method.
        
        """
        # runtime O(1)
        key,value = item
        if self.dict.has_key(key):
            raise ValueError,'more than one value for key ' + repr(key)
        self.list.append(key)
        self.dict[key] = value
        return len(self.list) - 1

    def insert(self, keyindex, item):
        
        """ Returns the object at position keyindex.

            keyindex may either be an integer to index an object by
            position or an arbitrary key object which is then used for
            dictionary like lookup.

        """
        key,value = item
        if self.dict.has_key(key):
            raise ValueError,'more than one value for key ' + repr(key)
        if type(keyindex) == types.IntType:
            # om.insert(0,('a','b'))
            self.list.insert(keyindex,key)
            self.dict[key] = value
        else:
            # om.insert('a',('b','c'))
            index = self.list.index(key)
            self.list.insert(index,key)
            self.dict[key] = value

    def remove(self, value):

        """ Remove all occurrences of value from the object.
        """
        for i,key in reverse(irange(self.list)):
            if self.dict[key] == value:
                del self.list[i]
                del self.dict[key]

    def count(self, value):

        """ Count all occurrences of value from the object.
        """
        count = 0
        for key in self.list:
            if self.dict[key] == value:
                count = count + 1
        return count

    def index(self, value):

        """ Return the index of the first occurrences of value in the
            object.
        
        """
        for index,key in irange(self.list):
            if self.dict[key] == value:
                return index
        raise ValueError,repr(value) + ' not as value in OrderedMapping'
            
    def keyindex(self, key):

        """ Returns the object at position keyindex.

            keyindex may either be an integer to index an object by
            position or an arbitrary key object which is then used for
            dictionary like lookup.

        """
        return self.list.index(key)

    def reverse(self):

        """ Reverses the order of the keys.
        """
        self.list.reverse()

    def sort(self, *args): 

        """ Sorts the keys.

            This changes the order of the stored items.

        """
        apply(self.list.sort, args)

    def clear(self):

        """ Clear the object.
        """
        self.list = []
        self.dict.clear()

    def copy(self):

        """ Return a shallow copy of the object.
        """
        import copy
        return copy.copy(self)

    def key(self,index):

        """ Returns the key at position index.
        """
        return self.list[index]

    def keys(self):

        """ Returns a list of keys in the order they are maintained
            by the object.
        """
        return self.list

    def items(self):

        """ Returns a list of (key,value) tuples in the order they are
            maintained by the object.
        """
        keys = self.list
        values = extract(self.dict,keys)
        return tuples(keys,values)

    def values(self):

        """ Returns a list of values in the order they are maintained
            by the object.
        """
        keys = self.list
        values = extract(self.dict, keys)
        return values

    def has_key(self, key):

        """ Returns 1/0 depending on whether the given key exists
            or not.
        """
        return self.dict.has_key(key)

    #def update(self, other):
    #   raise RuntimeError,'not implemented'

    def get(self, key, default=None):

        """ Return the value for key or default in case it is not found.

            This only works for non-index keys.

        """
        return self.dict.get(key,default)

    def filter(self,filterfct):

        """ Filters the mapping's keys and values according to
            a filterfct.

            The filterfct is called with (k,v) for each key value pair
            in the current order. If its return value is non-None, it
            is appended to the result list.

            The list is returned to the caller.

        """
        dict = self.dict
        l = []
        append = l.append
        for k in self.list:
            v = dict[k]
            result = filterfct(k,v)
            if result is not None:
                append(result)
        return l

###

class OrderedMappingWithDefault(OrderedMapping):

    """ OrderedMapping with default values.

        This version returns self._default in case a lookup fails.
        self._default is set to '' for this base class.

    """
    _default = ''

    def __getitem__(self, keyindex,

                    IntType=types.IntType,type=type): 

        """ Returns the object at position keyindex.

            If not found, ._default is returned.

            keyindex may either be an integer to index an object by
            position or an arbitrary key object which is then used for
            dictionary like lookup.

        """
        # runtime O(1)
        if type(keyindex) is IntType:
            # om[0]
            try:
                key = self.list[keyindex]
            except IndexError:
                return self._default
            else:
                return self.dict[key]
        else:
            # om['bar']
            try:
                return self.dict[keyindex]
            except KeyError:
                return self._default

freeze(OrderedMappingWithDefault)

###

if __name__ == '__main__':
    o = OrderedMapping()
    o['a'] = 'b'
    o['b'] = 'c'
    o['c'] = 'd'
    p = OrderedMapping()
    p['A'] = 'B'
    p['B'] = 'C'
    r = OrderedMapping(('1',1),('2',2),('3',3))
