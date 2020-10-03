
import sys, os, time
import doctest

from disto.problem import Problem

def test_problem() :
    '''
    >>> test_problem()
    Problem: <<Disto.Problem num_vars = 1; num_cons = 0>>
    '''
    pro = Problem(vars = {"1" : None}, cons = [])
    print(f"Problem: {pro.info()}")

if __name__ == '__main__' :
    result = doctest.testmod()
    print("-" * 50)
    print("[Problem Test] attempted/failed tests: %d/%d" % (result.attempted, result.failed))
