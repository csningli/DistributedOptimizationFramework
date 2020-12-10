
import sys, os, time
import doctest

from disto.problem import Domain

def test_domain() :
    '''
    >>> test_domain()
    domain.values: [1, 2, 3]
    domain.first_value(): 1
    domain.next_value(value = 1): 2
    domain.next_value(value = 2): 3
    domain.next_value(value = 3): None
    domain.start_index = 1
    domain.first_value(): 2
    domain.next_value(value = 2): 3
    domain.next_value(value = 3): 1
    domain.next_value(value = 1): None
    '''
    domain = Domain(values = [1, 2, 3])
    print(f"domain.values: {domain.values}")
    first = domain.first_value()
    print(f"domain.first_value(): {first}")
    current = first
    for i in range(3) :
        next = domain.next_value(value = current)
        print(f"domain.next_value(value = {current}): {next}")
        current = next
    domain.start_index = domain.values.index(2)
    print(f"domain.start_index = {domain.start_index}")
    first = domain.first_value()
    print(f"domain.first_value(): {first}")
    current = first
    for i in range(3) :
        next = domain.next_value(value = current)
        print(f"domain.next_value(value = {current}): {next}")
        current = next


if __name__ == '__main__' :
    result = doctest.testmod()
    print("-" * 50)
    print("[Domain Test] attempted/failed tests: %d/%d" % (result.attempted, result.failed))
