
import os, math, functools
import networkx as nx

from disto.problem import total_cost, GraphColoringProblem
from disto.agent import SyncBBAgent
from disto.monitor import Monitor
from disto.utils import print_problem, get_datetime_stamp, view_logs, get_var_host

# In this example, SyncBB (Katsutoshi Hirayama and Makoto Yokoo,
# "Distributed Partial Constraint Satisfaction Problem, 2005)
# is used to solve the graph coloring problem in the DCOP format,
# where the cost is defined as the number of violated constraints.

if __name__ == "__main__" :
    n = 6 # number of variables

    # graph = nx.generators.random_graphs.fast_gnp_random_graph(n = n, p = 0.6)

    graph = nx.Graph()
    for i in range(n) :
        graph.add_node(str(i))

    d = 3
    for i in range(n) :
        for j in range(1, d + 1) :
            graph.add_edge(str(i), str((i + j) % n))

    # build the graph coloring problem in the DCSP format

    pro = GraphColoringProblem(graph = graph, num_colors = 3, violation_cost = True)
    print("* Global Problem *")
    print_problem(pro = pro)
    print("-" * 50)

    m = 3 # number of the agents
    avars = [[str(j) for j in range(n) if j % m == i] for i in range(m)]
    var_host = get_var_host(avars = avars)
    # print(avars)

    def con_host(con, var_host) :
        ids = set([var_host(var) for var in con.vars])
        return [max(ids)]

    sub_pros = pro.split(avars = avars, con_host = functools.partial(con_host, var_host = var_host))
    agents = []
    log_dir = "logs/%s" % get_datetime_stamp()
    if not os.path.isdir(log_dir) :
        os.mkdir(log_dir)
    for i in range(m) :
        prev = i - 1 if i > 0 else None
        next = i + 1 if i < m - 1 else None
        agents.append(SyncBBAgent(id = i, pro = sub_pros[i], log_dir = log_dir, prev = prev, next = next, head = 0, tail = m - 1))

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
        print("Final (assign/cost/upper): %s/%s/%s" % final)
    # view_logs(log_dir = log_dir, style = "timeline")
    print("-" * 50)
    print("Done.")
