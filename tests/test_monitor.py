
import sys, os, time
import doctest

from disto.monitor import Monitor

def test_monitor() :
    '''
    >>> test_monitor()
    '''
    monitor = Monitor()
    monitor.run(agents = [], timeout = 1)

if __name__ == '__main__' :
    result = doctest.testmod()
    print("-" * 50)
    print("[Monitor Test] attempted/failed tests: %d/%d" % (result.attempted, result.failed))
