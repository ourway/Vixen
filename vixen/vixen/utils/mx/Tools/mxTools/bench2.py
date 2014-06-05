import hack
import mx.Tools.NewBuiltins

a = trange(10000)

def f1():

    x = (a,a,a)
    for i in trange(100):
        x = lists(x)

def f2():

    x = (a,a,a)
    for i in trange(100):
        x = tuples(x)

def f3(apply=apply,map=map,tuple=tuple):

    x = (a,a,a)
    y = None
    for i in trange(100):
        x = apply(map,(y,)+tuple(x))

print 'lists:',hack.clock('f1()')
print 'tuples:',hack.clock('f2()')
print 'map:',hack.clock('f3()')
