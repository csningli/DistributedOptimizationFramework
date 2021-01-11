
import sys, os, time
import doctest

from disto.problem import Domain, Constraint, Problem
from disto.utils import get_constraint_graph, get_pseudo_tree

pro = Problem(vars = {str(i) : Domain(values = [0, 1]) for i in range(4)}, cons = [
    Constraint(vars = ["0", "1"]),
    Constraint(vars = ["0", "2"]),
    Constraint(vars = ["1", "3"]),
    Constraint(vars = ["2", "3"]),
])

avars = [["0"], ["1"], ["2"], ["3"]]

def test_constraint_graph() :
    '''
    >>> test_constraint_graph()
    Constraint graph: [[1, 2], [0, 3], [0, 3], [1, 2]]
    '''
    graph = get_constraint_graph(pro = pro, avars = avars)
    print(f"Constraint graph: {graph}")

def test_pseudo_tree() :
    '''
    >>> test_pseudo_tree()
    Pseudo tree: [(None, [2]), (3, []), (0, [3]), (2, [1])]
    '''
    cons_graph = get_constraint_graph(pro = pro, avars = avars)
    tree = get_pseudo_tree(graph = cons_graph)
    print(f"Pseudo tree: {tree}")

if __name__ == '__main__' :
    result = doctest.testmod()
    print("-" * 50)
    print("[PseudoTree Test] attempted/failed tests: %d/%d" % (result.attempted, result.failed))
