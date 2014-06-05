""" Cache - Generic cache implementation

    Copyright (c) 1998-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.
"""
import sys
import mx.Tools.NewBuiltins

# Weight table
MAXLOCALITY = 256
_weights = [1] * MAXLOCALITY

# maximal history size (must somewhat larger than MAXLOCALITY)
HISTORYLIMIT = 2 * MAXLOCALITY

# Cut goal that has to be reached (self.max_cachesize * float(DENOM / NOM))
DENOM = 3
NOM = 4

# Print debugging info ?
_debug = 0

# Init globals
class _modinit:
    import math
    l = frange(0,1,MAXLOCALITY)
    for i,factor in irange(l):
        _weights[i] = int((math.exp(factor) - 1.0) * 8192)
        if _debug:
            print i,'. weight =',_weights[i]
del _modinit

### Classes

class NotCached:

    """ A singleton that can be used in conjunction with the .get()
        method of Cache. It behaves like None.
    """
    def __nonzero__(self):
        return 0
    __len__ = __nonzero__

NotCached = NotCached()

###

class Cache:

    """ Tunable cache implementation

        The following parameters influence the cache behaviour:
        - max_cachesize:        the cache will be cut smaller when this limit
                                is reached
        - max_elementsize:      elements with size greate than this limit
                                will not be cached
        - locality:             these many elements will be looked at in
                                the hit statistics to determine how important
                                a specific entry is
    """
    data = None                 # Dict. of id:value cache entries
    put_history = None          # Reverse list of id puts; last is most
                                # recent access; contains id for each access
    get_history = None          # Reverse list of id gets; last is most
                                # recent access; contains id for each access

    def __init__(self,max_cachesize=200,
                      max_elementsize=4096,
                      locality=50):

        self.max_cachesize = max_cachesize
        self.max_elementsize = max_elementsize
        if locality > MAXLOCALITY:
            raise ValueError,'locality must be <= %i' % MAXLOCALITY
        self.locality = locality

        self.cachesize = 0
        self.cuts = 0
        self.misses = 0
        self.hits = 0

        self.data = {}
        self.put_history = []
        self.get_history = []

    def cut(self,

            NOM=NOM,DENOM=DENOM):

        """ Force a cut of the cache's contents.

            This will make room for at least one new entry.
        """
        if _debug:
            print '  Cutting down cache size...'
        cachesize = self.cachesize
            
        # Cut the cache down to the entries in recent get history
        newdata = {}
        known_key = newdata.has_key
        data = self.data
        for id in self.get_history[-self.locality:]:
            if known_key(id):
                continue
            try:
                newdata[id] = data[id]
            except KeyError:
                pass

        cachesize = len(newdata)
        if _debug:
            print '   Size after cut to recent history:',cachesize

        # Check
        if cachesize * NOM >= self.max_cachesize * DENOM:

            # Calculate weights
            d = {}
            weights = _weights
            d_get = d.get
            for i,id in irange(self.get_history[-self.locality:]):
                if not known_key(id):
                    continue
                d[id] = d_get(id,0) + weights[i]

            # Delete all entries left from median
            ranking = sortedby(d.items(),1)
            if _debug:
                print '   Ranking:',ranking
            for id,weight in ranking[:len(d)/2]:
                if _debug:
                    print '   Deleting',id,'with weight =',weight
                del newdata[id]

            # Check
            cachesize = len(newdata)

            if cachesize * NOM >= self.max_cachesize * DENOM:
                # Ok, so the smart way didn't work...
                if _debug:
                    print '   Did not work, going the hard way...'
                newdata.clear()
                cachesize = 0

        self.data = newdata
        self.cachesize = cachesize
        self.cuts = self.cuts + 1

    def clear(self):

        """ Clear the cache.
        """
        self.cachesize = 0
        self.data = {}
        self.history = []

    def get(self,id,default=NotCached,

            HISTORYLIMIT=HISTORYLIMIT):

        """ Get a value from the cache or return default if it is
            not cached.
        """
        item = self.data.get(id,None)
        if item is None:
            self.misses = self.misses + 1
            return default

        # Add "hit"
        self.get_history.append(id)
        if len(self.get_history) > HISTORYLIMIT:
            del self.get_history[-self.locality:]
        self.hits = self.hits + 1

        return item

    def put(self,id,value,sizeof=sizeof,

            HISTORYLIMIT=HISTORYLIMIT):

        """ Add a value to the cache or update an existing one.
        """
        size = sizeof(value)
        if size > self.max_elementsize:
            return

        # Adding a new entry: make sure there is room
        if not self.data.has_key(id):
            if _debug:
                print '  Adding',id
            self.cachesize = cachesize = self.cachesize + 1
            if cachesize > self.max_cachesize:
                self.cut()

        self.data[id] = value
        self.put_history.append(id)
        if len(self.put_history) > HISTORYLIMIT:
            del self.put_history[-self.locality:]


    # Aliases
    add = put
    update = put

    def delete(self,id):

        """ Delete an entry from the cache.

            It is not an error, if the entry is not currently in the cache.
        """
        try:
            del self.data[id]
        except KeyError:
            pass

    # Aliases
    remove = delete

###

if __name__ == '__main__':
    c = Cache(10,100,locality=17)
    i = 1
    while 1:
        print 'Round',i,c.cachesize,c.cuts,c.misses,c.data.keys(); i = i + 1
        c.put(1,2)
        c.get(1)
        c.get(1)
        c.put(5,2)
        c.get(5)
        c.put(2,2)
        c.put(3,2)
        c.get(2)
        c.get(3)
        c.put(2,3)
        c.put(3,'x'*200)
        c.get(2)
        c.get(3)
        c.get(2)
        c.put(4,2)
        c.get(4,2)
        c.get(4,2)
        c.get(4,2)
        # Add noise
        c.put(i,'x')
        c.put(i * 2,'x')
        c.put(i * 3,'x')
        c.get(i)

