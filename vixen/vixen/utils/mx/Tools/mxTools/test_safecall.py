""" Test safecall() mxTools API.

"""
import mxTools, os, signal

def simulate_segfault():
    os.kill(os.getpid(), signal.SIGSEGV)
    # Make sure Python catches the signal
    for i in range(10000):
        pass

def real_segfault(errtype=0):
    mxTools.segfault(errtype)

print 'Simulating programming errors ...'
for i in range(5):
    print ' Try %i' % i
    try:    
        mxTools.safecall(simulate_segfault)
    except RuntimeError, reason:
        print '  RuntimeError: %s' % reason
    else:
        print '  No RuntimeError ?!'
print

print 'Real world programming errors ...'
for errtype in range(5):
    print ' Error type %i' % errtype
    try:    
        mxTools.safecall(real_segfault, (errtype,))
    except RuntimeError, reason:
        print '  RuntimeError: %s' % reason
    else:
        print '  No RuntimeError ?!'
        
print
print 'Works.'
