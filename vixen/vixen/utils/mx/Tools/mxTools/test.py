import mx.Tools
import mx.Tools.NewBuiltins
import time, sys

# forall
t = (3,) * 10; assert forall(lambda x: x==3,t) == 1
t = t + (4,); assert forall(lambda x: x==3,t) == 0

# exists
t = (3,) * 10; assert exists(lambda x: x==4,t) == 0
t = t + (4,); assert exists(lambda x: x==4,t) == 1

# count
t = (3,) * 10; assert count(lambda x: x==3,t) == 10
t = t + (4,); assert count(lambda x: x==4,t) == 1

# index
t = (3,) * 10
try:
    index(lambda x: x!=3,t)
except ValueError:
    ok = 1
else:
    ok = 0
assert ok == 1
t = t + (4,); assert index(lambda x: x==4,t) == 10

def testkw(x,a=4):
    return x,a

def testtwoargs(a, b):
    return a + b

# napply
t = napply(10,time.time)
t = napply(10,len,(t,))
t = napply(10,testtwoargs,(0,10))
t = napply(10,testkw,(2,),{'a':3})
assert t == ((2, 3), (2, 3), (2, 3), (2, 3), (2, 3), (2, 3), 
             (2, 3), (2, 3), (2, 3), (2, 3))

# trange
t = trange(10); assert t == tuple(range(10))
t = trange(1,10); assert t == tuple(range(1,10))
t = trange(1,10,2); assert t == tuple(range(1,10,2))
t = trange(1,10,3); assert t == tuple(range(1,10,3))
t = trange(-10); assert t == tuple(range(-10))
t = trange(-1,-10); assert t == tuple(range(-1,-10))
t = trange(-10,-1); assert t == tuple(range(-10,-1))
t = trange(-10,-1,2); assert t == tuple(range(-10,-1,2))
t = trange(-10,-1,3); assert t == tuple(range(-10,-1,3))
t = trange(-1,-10,-1); assert t == tuple(range(-1,-10,-1))
t = trange(-1,-10,-2); assert t == tuple(range(-1,-10,-2))
t = trange(-1,-10,-3); assert t == tuple(range(-1,-10,-3))

# indices
l = range(10); assert indices(l) == trange(10)
t = trange(10); assert indices(t) == trange(10)
s = '0123456789'; assert indices(s) == trange(10)

# range_len
l = range(10); assert range_len(l) == range(10)
t = trange(10); assert range_len(t) == range(10)
s = '0123456789'; assert range_len(s) == range(10)

# irange
l = range(1,10,2); assert irange(l) == ((0, 1), (1, 3), (2, 5), (3, 7), (4, 9))
t = range(1,10,2); assert irange(t) == ((0, 1), (1, 3), (2, 5), (3, 7), (4, 9))
d = {0:2,1:5,2:7}; assert irange(d) == ((0, 2), (1, 5), (2, 7))
d = {'a':1,'m':2,'r':3,'c':4}; assert irange(d,'marc') == (('m', 2), ('a', 1), ('r', 3), ('c', 4))
l = range(10); assert irange(l,(1,3,5,6,7)) == ((1, 1), (3, 3), (5, 5), (6, 6), (7, 7))
t = range(10); assert irange(t,(4,1,5,2,3)) == ((4, 4), (1, 1), (5, 5), (2, 2), (3, 3))

# ifilter
c = lambda x: x>5
l = range(10); assert ifilter(c,l) == [(6, 6), (7, 7), (8, 8), (9, 9)]
t = trange(10); assert ifilter(c,t) == [(6, 6), (7, 7), (8, 8), (9, 9)] 
c = lambda x: x>='f'
s = 'abcdefghijk'; assert ifilter(c,s) == [(5, 'f'), (6, 'g'), (7, 'h'), (8, 'i'), (9, 'j'), (10, 'k')]
c = lambda x: x>5
l = range(10); assert ifilter(c,l,(2,6,7)) == [(6, 6), (7, 7)]
t = trange(10); assert ifilter(c,t,(7,6,2)) == [(7, 7), (6, 6)]
c = lambda x: x>='f'
s = 'abcdefghijk'; assert ifilter(c,s,(1,3,5,7)) == [(5, 'f'), (7, 'h')]

# mapply
class C:
    def test(self,x,y):
        return (x,y)
o = napply(10,C,()) # create 10 objects
l = map(getattr,o,('test',)*len(o)) # get test methods
r = mapply(l,(1,2)) # call each of them with (1,2)
assert r == ((1,2),)*10

# method_mapply
l = [None] * 100000
for i in indices(l):
    l[i] = []
print 'for-loop:',
start = time.clock()
for x in l:
    x.append('hi')
print time.clock() - start,'seconds'
print 'map:',
start = time.clock()
map(lambda x: x.append('hi'),l)
print time.clock() - start,'seconds'
print 'method_mapply:',
start = time.clock()
method_mapply(l,'append',('hi',))
print time.clock() - start,'seconds'

print 'checking...'
for x,y,z in l:
    assert x == y == z

# get
l = range(10)
assert get(l,2) == 2
assert get(l,20,2) == 2

# extract
l = range(10)
assert extract(l,(1,2,3)) == [1,2,3]
assert extract(l,(1,20,30),(1,20,30)) == [1,20,30]

# findattr
l = []
d = {}
assert findattr((l,d),'count')
assert findattr((l,d),'items')

# tuples
a = range(1,10)
b = range(2,12)
c = range(3,14)
assert tuples(a,b,c) == [(1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6), 
                         (5, 6, 7), (6, 7, 8), (7, 8, 9), (8, 9, 10),
                         (9, 10, 11)]
assert tuples(c,b,a,b,c) == \
       [(3, 2, 1, 2, 3), (4, 3, 2, 3, 4), (5, 4, 3, 4, 5), (6, 5, 4, 5, 6),
        (7, 6, 5, 6, 7), (8, 7, 6, 7, 8), (9, 8, 7, 8, 9), (10, 9, 8, 9, 10), 
        (11, 10, 9, 10, 11), (12, 11, None, 11, 12), 
        (13, None, None, None, 13)]

# lists
a = range(1,10)
b = range(2,11)
c = range(3,12)
assert (a,b,c) == lists(tuples(a,b,c))
assert lists(b,c,a) == ([2, 3, 1], [3, 4, 2], [4, 5, 3], [5, 6, 4],
                        [6, 7, 5], [7, 8, 6], [8, 9, 7], [9, 10, 8],
                        [10, 11, 9])
assert lists(b[:3],a,c) == ([2, 1, 3], [3, 2, 4], [4, 3, 5])

# dict
items = tuples(a,b)
d = dict(items)
assert d == {9: 10, 8: 9, 7: 8, 6: 7, 5: 6, 4: 5, 3: 4, 2: 3, 1: 2}

# invdict
assert invdict(d) == {10: 9, 9: 8, 8: 7, 7: 6, 6: 5, 5: 4, 4: 3, 3: 2, 2: 1}

# acquire
class C:
        baseobj = None
        def __init__(self,baseobj=None):
                self.baseobj = baseobj
        __getattr__ = acquire

class B:
        a = 1

b = B()
c = C(baseobj=b)
assert c.a == 1

if 0:
    # xmap
    import xmap
    m = xmap(lambda x: 2*x, xrange(sys.maxint))
    assert list(m[0:10]) == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
    assert list(m[10000:10010]) == [20000, 20002, 20004, 20006, 20008, 20010,
                                    20012, 20014, 20016, 20018]
    try:
            m[sys.maxint-1]
    except OverflowError:
            pass
    else:
            raise AssertionError,'should have received an OverflowError'

# iremove
l = range(10)
iremove(l,(1,2,3))
assert l == [0, 4, 5, 6, 7, 8, 9]
d = dict(tuples(range(10),range(1,11)))
iremove(d,(1,2,3))
assert d == {9: 10, 8: 9, 7: 8, 6: 7, 5: 6, 4: 5, 0: 1}

# verscmp
verscmp = mx.Tools.verscmp
assert verscmp('1.0','1.1') < 0
assert verscmp('1.0','1.0') == 0
assert verscmp('1.0','1.2') < 0
assert verscmp('1.1','1.0') > 0
assert verscmp('1.1a','1.0') > 0
assert verscmp('1.1a','1.0a') > 0
assert verscmp('1.0a','1.0a') == 0
assert verscmp('1.0b','1.0a') > 0
assert verscmp('1.0a','1.0b') < 0
assert verscmp('1.0a','1.0c') < 0
assert verscmp('1.0a','1.0d') < 0
assert verscmp('1.0a','1.0a.1') < 0
assert verscmp('1.0a.1','1.0a') > 0
assert verscmp('1.0a.2','1.0a') > 0
assert verscmp('1.0a','1.0.0b') < 0
assert verscmp('1.0','1.0.0b') > 0
assert verscmp('1.0alpha','1.0.0') < 0
assert verscmp('1.alpha','1.0') < 0
assert verscmp('1.2alpha','1.2') < 0
assert verscmp('1.2alpha.1','1.2.1') < 0
assert verscmp('1alpha.2.1','1.0') < 0
assert verscmp('1alpha.','1alpha') == 0
assert verscmp('1.0.0.0.0','1.0') == 0
assert verscmp('1.0.0.0.1','1.0') > 0

# interactive
print 'Python is operating in %sinteractive mode' % \
      ('non-' * (not mx.Tools.interactive()))

print 'Works.'
