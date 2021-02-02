
import os, math, functools
import networkx as nx

from disto.problem import total_cost, GraphColoringProblem
from disto.agent import AdoptAgent
from disto.monitor import Monitor
from disto.utils import get_var_host, print_problem, get_datetime_stamp, view_logs, get_constraint_graph, get_pseudo_tree

# In this example, Asynchronous Distributed Optimization - Adopt (Pragnesh Jay Modi, Wei-Min Shen,
# Milind Tambe, and Makoto Yokoo, "Adopt: Asynchronous Distributed Constraint Optimization with
# Quality Guarantees", 2005 is used to solve the optimization version of the graph coloring problem,
# which is modeled in a DCOP form. In the problem, the cost is defined as the number of violated constraints.

if __name__ == "__main__" :
    log_dir = "logs/%s" % get_datetime_stamp()
    if not os.path.isdir(log_dir) :
        os.mkdir(log_dir)

    n = 6 # number of variables

    # graph = nx.generators.random_graphs.fast_gnp_random_graph(n = n, p = 0.6)

    graph = nx.Graph()
    for i in range(n) :
        graph.add_node(str(i))

    d = 3
    for i in range(n) :
        for j in range(1, d + 1) :
            graph.add_edge(str(i), str((i + j) % n))

    # build the graph coloring problem in the DCOP format, where
    # the cost is defined as the number of violated constraintss

    pro = GraphColoringProblem(graph = graph, num_colors = 3, violation_cost = True)
    print("* Global Problem *")
    print_problem(pro = pro)
    print("-" * 50)

    m = 3 # number of the agents
    avars = [[str(j) for j in range(n) if j % m == i] for i in range(m)]
    var_host = get_var_host(avars = avars)

    cons_graph = get_constraint_graph(pro = pro, avars = avars)
    pseudo_tree = get_pseudo_tree(graph = cons_graph)

    # print(avars)

    def con_host(con, var_host) :
        ids = set([var_host(var) for var in con.vars])
        return [max(ids)]

    sub_pros = pro.split(avars = avars, con_host = functools.partial(con_host, var_host = var_host))
    agents = []
    for i in range(m) :
        agents.append(AdoptAgent(id = i, pro = sub_pros[i],
            parent = pseudo_tree[i][0], children = pseudo_tree[i][1],
            var_host = var_host, log_dir = log_dir))

    for i, agent in enumerate(agents) :
        print("Agent: %s" % agent.info())
        print("* Sub-Problem: %d *" % i)
        print_problem(pro = agent.pro)
        print("-" * 50)

    monitor = Monitor()
    time_cost = monitor.run(agents = agents, timeout = 1)
    print("Time cost: %s" % time_cost)
    print("-" * 50)
    print("Monitor.mem: %s" % monitor.mem)
    print("-" * 50)
    if len(monitor.mem) > 0 :
        final = monitor.mem[-1]
        print("Final: %s" % final)
        cost, _ = total_cost(cons = pro.cons, assign = final)
        print("Cost: %s" % cost)
        print("-" * 50)
    # view_logs(log_dir = log_dir, style = "timeline")
    print("-" * 50)
    print("Done.")
