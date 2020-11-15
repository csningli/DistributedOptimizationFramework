
import sys, os, time
import doctest

from disto.problem import Constraint, DiffConstraint, BinaryDiffConstraint

def test_constraint() :
    '''
    >>> test_constraint()
    con.vars: ['1', '2', '3']
    con.cost(x = [1, 2, 3]): 0
    '''
    con = Constraint(vars = ["1", "2", "3"])
    print(f"con.vars: {con.vars}")
    print(f"con.cost(x = [1, 2, 3]): {con.cost(x = [1, 2, 3])}")

def test_diff_constraint() :
    '''
    >>> test_diff_constraint()
    con.vars: ['1', '2', '3']
    con.cost(x = [1, 1, 1]): None
    con.cost(x = [1, 2, 1]): None
    con.cost(x = [1, 2, 3]): 0
    '''
    con = DiffConstraint(vars = ["1", "2", "3"])
    print(f"con.vars: {con.vars}")
    print(f"con.cost(x = [1, 1, 1]): {con.cost(x = [1, 1, 1])}")
    print(f"con.cost(x = [1, 2, 1]): {con.cost(x = [1, 2, 1])}")
    print(f"con.cost(x = [1, 2, 3]): {con.cost(x = [1, 2, 3])}")

def test_binary_diff_constraint() :
    '''
    >>> test_binary_diff_constraint()
    con.vars: ['1', '2']
    con.cost(x = [1, 1]): None
    con.cost(x = [1, 2]): 0
    '''
    con = BinaryDiffConstraint(vars = ["1", "2"])
    print(f"con.vars: {con.vars}")
    print(f"con.cost(x = [1, 1]): {con.cost(x = [1, 1])}")
    print(f"con.cost(x = [1, 2]): {con.cost(x = [1, 2])}")

if __name__ == '__main__' :
    result = doctest.testmod()
    print("-" * 50)
    print("[Constraint Test] attempted/failed tests: %d/%d" % (result.attempted, result.failed))
