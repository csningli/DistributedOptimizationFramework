
import sys, os, time
import doctest

from disto.problem import Domain

def test_domain() :
    '''
    >>> test_domain()
    domain.values: [1, 2, 3]
    domain.first_value(): 1
    domain.next_value(value = 1): 2
    '''
    domain = Domain(values = [1, 2, 3])
    print(f"domain.values: {domain.values}")
    first = domain.first_value()
    print(f"domain.first_value(): {first}")
    print(f"domain.next_value(value = {first}): {domain.next_value(value = first)}")

if __name__ == '__main__' :
    result = doctest.testmod()
    print("-" * 50)
    print("[Domain Test] attempted/failed tests: %d/%d" % (result.attempted, result.failed))
