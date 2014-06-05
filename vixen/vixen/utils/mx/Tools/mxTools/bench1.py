import hack
import mx.Tools.NewBuiltins

k = range(10000)
l = range(1,10001)
loops = trange(100)

def f(k=k,l=l,tuples=tuples,loops=loops):
    for i in loops:
        for a,b in tuples(k,l):
            pass

def f1(k=k,l=l,lists=lists,loops=loops):
    for i in loops:
        for a,b in lists(k,l):
            pass

def g(k=k,l=l,map=map,loops=loops):
    for i in loops:
        for a,b in map(None,k,l):
            pass

def h(k=k,l=l,indices=indices,len=len,loops=loops):
    for i in loops:
        for i in indices(k):
            a,b = k[i], l[i]

print 'with tuples():',
hack.clock('f()')
print 'with lists():',
hack.clock('f1()')
print 'with map():',
hack.clock('g()')
print 'indexed:',
hack.clock('h()')
print 'map(None,...):',
hack.clock('apply(map,(None,)+(k,)*100)')
print 'tuples(...):',
hack.clock('tuples((k,)*100)')
print 'lists(...):',
hack.clock('lists((k,)*100)')

# Check
assert apply(map,(None,)+(k,)*100) == tuples((k,)*100)
