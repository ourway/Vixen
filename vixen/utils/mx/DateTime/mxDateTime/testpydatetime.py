from mx.DateTime import *

# Check compatibility with Python's datetime
try:
    import datetime
except ImportError:
    pass
else:
    # Test values
    pydt1 = datetime.datetime(2007, 1, 1, 12, 30, 13)
    pyd1 = datetime.date(2007, 1, 1)
    pyt1 = datetime.time(12, 30, 13)
    pydtd1 = datetime.timedelta(0, 12*3600 + 30*60 + 13)
    mxdt1 = DateTime(2007, 1, 1, 12, 30, 13)
    mxdt2 = DateTime(2007, 1, 1)
    mxdtd1 = DateTimeDelta(0, 12, 30, 13)

    # Comparisons
    assert pydt1 == mxdt1
    assert mxdt1 == pydt1
    assert mxdt2 == pyd1
    # Doesn't work, since datetime.time always compares false
    # against non-datetime.time types
    #assert pyt1 == mxdtd1
    #assert mxdtd1 == pyt1

    # Subtract
    assert mxdt1 - pydt1 == 0.0
    assert mxdt2 - pyd1 == 0.0
    assert mxdt1 - pyd1 == mxdtd1

    # Add
    assert mxdt1 - pydtd1 == mxdt2, (mxdt1 - pydtd1, mxdt2)
    assert pydt1 - mxdt2 == -mxdtd1, (pydt1 - mxdt2, -mxdtd1)
    assert mxdt2 + pydtd1 == mxdt1
    # Not supported by datetime module:
    #assert pydt1 - pyd1 == mxdtd1
    # Not supported by datetime module:
    #assert pydt1 - mxdtd1 == mxdt2
