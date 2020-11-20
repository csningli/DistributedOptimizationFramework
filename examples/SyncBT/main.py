
import os, math
import networkx as nx

from disto.problem import total_cost, GraphColoringProblem
from disto.agent import SyncBTAgent
from disto.monitor import Monitor
from disto.utils import print_problem, get_datetime_stamp, view_logs

# In this example, SyncBT (Makoto Yokoo and Toru Ishida, "The Distributed
# Constraint Satisfaction Problem: Formalization and Algorithms", 1998)
# is used to solve the graph coloring problem, which is modeled in a DCSP form.

if __name__ == "__main__" :
    n = 6 # number of variables

    # graph = nx.generators.random_graphs.fast_gnp_random_graph(n = n, p = 0.6)

    graph = nx.Graph()
    for i in range(n) :
        graph.add_node(str(i))

    d = 2
    for i in range(n) :
        for j in range(1, d + 1) :
            graph.add_edge(str(i), str((i + j) % n))

    # build the graph coloring problem in the DCSP format

    pro = GraphColoringProblem(graph = graph, num_colors = 4)
    print("* Global Problem *")
    print_problem(pro = pro)
    print("-" * 50)

    m = 2 # number of the agents
    avars = [[str(j) for j in range(n) if j % m == i] for i in range(m)]
    # print(avars)

    sub_pros = pro.split(avars = avars)
    agents = []
    log_dir = "logs/%s" % get_datetime_stamp()
    if not os.path.isdir(log_dir) :
        os.mkdir(log_dir)
    for i in range(m) :
        prev = i - 1 if i > 0 else None
        next = i + 1 if i < m - 1 else None
        agents.append(SyncBTAgent(id = i, pro = sub_pros[i], log_dir = log_dir, prev = prev, next = next))

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
    view_logs(log_dir = log_dir, style = "timeline")
    print("-" * 50)
    print("Done.")
