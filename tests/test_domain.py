
import sys, os, time
import doctest

from disto.problem import Domain

def test_domain() :
    '''
    >>> test_domain()
    domain.values: [1, 2, 3]
    '''
    domain = Domain(values = [1, 2, 3])
    print(f"domain.values: {domain.values}")

if __name__ == '__main__' :
    result = doctest.testmod()
    print("-" * 50)
    print("[Domain Test] attempted/failed tests: %d/%d" % (result.attempted, result.failed))
