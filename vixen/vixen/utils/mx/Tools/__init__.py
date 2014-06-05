""" Tools - A collection of new builtins and misc. helpers for Python

    Copyright (c) 2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.
"""
from Tools import *
from Tools import __version__

# For backward-compatibility: auto-install the add-ons:

### You can control automatic installation with this if-statement.
### Replace the 1 with 0 to disable automatic install.
if 1:
    import NewBuiltins
