
import sys, os, time
import doctest
import networkx as nx

from disto.problem import Constraint, Problem, GraphColoringProblem, total_cost

def test_problem() :
    '''
    >>> test_problem()
    Problem: <<Disto.Problem num_vars = 2; num_cons = 1>>
    Sub Problem 0: <<Disto.Problem num_vars = 1; num_cons = 1>>
    vars: {'1': None}
    Sub Problem 1: <<Disto.Problem num_vars = 1; num_cons = 1>>
    vars: {'2': None}
    '''
    pro = Problem(vars = {"1" : None, "2" : None}, cons = [Constraint(vars = ["1", "2"])])
    print(f"Problem: {pro.info()}")
    sub_pros = pro.split([["1"], ["2"]])
    for i, sub_pro in enumerate(sub_pros) :
        print(f"Sub Problem {i}: {sub_pro.info()}")
        print(f"vars: {sub_pro.vars}")


def test_graph_coloring_problem() :
    '''
    >>> test_graph_coloring_problem()
    Graph nodes: ['1', '2']
    Graph edges: [('1', '2')]
    Graph Coloring Problem: <<Disto.GraphColoringProblem num_nodes = 2; num_edges = 1; num_colors = 2>>
    Problem: <<Disto.GraphColoringProblem num_vars = 2; num_cons = 1>>
    Cost of assignment {'1': 0, '2': 0}: None
    Cost of assignment {'1': 0, '2': 1}: 0
    '''
    graph = nx.Graph()
    graph.add_node("1")
    graph.add_node("2")
    graph.add_edge("1", "2")
    print(f"Graph nodes: {graph.nodes}")
    print(f"Graph edges: {graph.edges}")
    pro = GraphColoringProblem(graph = graph, num_colors = 2)
    print(f"Graph Coloring Problem: {pro.info()}")
    print(f"Problem: {super(GraphColoringProblem, pro).info()}")
    assign = {"1" : 0, "2" : 0}
    cost, violated = total_cost(pro.cons, assign)
    print(f"Cost of assignment {assign}: {cost}")
    assign = {"1" : 0, "2" : 1}
    cost, violated = total_cost(pro.cons, assign)
    print(f"Cost of assignment {assign}: {cost}")

def test_graph_coloring_cost() :
    '''
    >>> test_graph_coloring_cost()
    Graph nodes: ['1', '2']
    Graph edges: [('1', '2')]
    Graph Coloring Problem: <<Disto.GraphColoringProblem num_nodes = 2; num_edges = 1; num_colors = 2>>
    Problem: <<Disto.GraphColoringProblem num_vars = 2; num_cons = 1>>
    Cost of assignment {'1': 0, '2': 0}: 1
    Cost of assignment {'1': 0, '2': 1}: 0
    '''
    graph = nx.Graph()
    graph.add_node("1")
    graph.add_node("2")
    graph.add_edge("1", "2")
    print(f"Graph nodes: {graph.nodes}")
    print(f"Graph edges: {graph.edges}")
    pro = GraphColoringProblem(graph = graph, num_colors = 2, violation_cost = True)
    print(f"Graph Coloring Problem: {pro.info()}")
    print(f"Problem: {super(GraphColoringProblem, pro).info()}")
    assign = {"1" : 0, "2" : 0}
    cost, violated = total_cost(pro.cons, assign)
    print(f"Cost of assignment {assign}: {cost}")
    assign = {"1" : 0, "2" : 1}
    cost, violated = total_cost(pro.cons, assign)
    print(f"Cost of assignment {assign}: {cost}")

if __name__ == '__main__' :
    result = doctest.testmod()
    print("-" * 50)
    print("[Problem Test] attempted/failed tests: %d/%d" % (result.attempted, result.failed))
