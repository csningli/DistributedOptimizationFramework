
import sys, os, time
import doctest
import networkx as nx

from disto.problem import Domain, BinaryDiffCost, Problem, GraphColoringProblem, total_cost, fit_assign_to_con

def test_binary_diff_cost() :
    '''
    >>> test_binary_diff_cost()
    Problem: <<Disto.Problem num_vars = 3; num_cons = 2>>
    Cost of assign {'0': 0, '1': 0}: 1
    '''
    pro = Problem(vars = {str(i) :  Domain(values = ["yes", "no"]) for i in range(3)}, cons = [BinaryDiffCost(vars = ["0", "1"]), BinaryDiffCost(vars = ["1", "2"])])
    print(f"Problem: {pro.info()}")
    assign = {"0" : 0, "1" : 0}
    cost = 0
    for con in pro.cons :
        x = fit_assign_to_con(assign, con)
        if x is not None :
            cost += con.cost(x)
    print("Cost of assign %s: %s" % (assign, cost))


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
    print("[Cost Test] attempted/failed tests: %d/%d" % (result.attempted, result.failed))
