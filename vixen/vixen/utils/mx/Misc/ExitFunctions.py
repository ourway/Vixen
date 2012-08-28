""" Central Registry for sys.exitfunc()-type functions

    Copyright (c) 1997-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.
"""
import sys,traceback

__version__ = '0.1'

class ExitFunctionDispatcher:

    """ Singleton that manages exit functions. These function will be
        called upon system exit in reverse order of their registering.
    """
    def __init__(self):

        """ Install the dispatcher as sys.exitfunc()
        """
        self.exitfunc_list = []
        if hasattr(sys,'exitfunc'):
            self.old_exitfunc = sys.exitfunc
        else:
            self.old_exitfunc = None
        sys.exitfunc = self.exitfunc

    def exitfunc(self,

                 write=sys.stderr.write,print_exc=traceback.print_exc,
                 stderr=sys.stderr):

        """ This is the exitfunc that we install to dispatch the
            processing to the registered other functions
        """
        for f in self.exitfunc_list:
            try:
                f()
            except:
                write('Error while executing Exitfunction %s:\n' % f.__name__)
                print_exc(10,stderr)
        # Now that we're finished, call the previously installed exitfunc()
        if self.old_exitfunc:
            self.old_exitfunc()

    def register(self,f,position=0):
        
        """ Register f as exit function. These functions must not take
            parameters.
            - position = 0: register the function at the beginning of the
              list; these functions get called before the functions already
              in the list (default)
            - position = -1: register the function at the end of the list;
              the function will get called after all other functions
        """
        if position < 0: 
            position = position + len(self.exitfunc_list) + 1
        self.exitfunc_list.insert(position,f)

    def deregister(self,f):

        """ Remove the function f from the exitfunc list; if it is not
            found, the error is silently ignored.
        """
        try:
            self.exitfunc_list.remove(f)
        except:
            pass

# Create the singleton
ExitFunctions = ExitFunctionDispatcher()
