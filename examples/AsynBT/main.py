
import os, math, functools
import networkx as nx

from disto.problem import GraphColoringProblem
from disto.agent import AsynBTAgent
from disto.monitor import Monitor
from disto.utils import get_var_mapping, print_problem, get_datetime_stamp, view_logs

# In this example, AsynBT (Makoto Yokoo and Toru Ishida, "The Distributed
# Constraint Satisfaction Problem: Formalization and Algorithms") is used
# to solve the graph coloring problem, which is modeled in a DCSP form.

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

    m = 3 # number of the agents
    avars = [[str(j) for j in range(n) if j % m == i] for i in range(m)]
    var_mapping = get_var_mapping(avars = avars)
    # print(avars)

    def con_host(con, var_mapping) :
        ids = set([var_mapping[var] for var in con.vars])
        return [max(ids)]

    sub_pros = pro.split(avars = avars, con_host = functools.partial(con_host, var_mapping = var_mapping))
    agents = []
    log_dir = "logs/%s" % get_datetime_stamp()
    if not os.path.isdir(log_dir) :
        os.mkdir(log_dir)

    outgoings = {i : [] for i in range(m)}
    for con in pro.cons :
        ids = set([var_mapping[var] for var in con.vars])
        max_id = max(ids)
        for id in ids :
            if id != max_id and max_id not in outgoings[id] :
                outgoings[id].append(max_id)

    for i in range(m) :
        agents.append(AsynBTAgent(id = i, pro = sub_pros[i], log_dir = log_dir, outgoings = outgoings[i], var_mapping = var_mapping))

    for i, agent in enumerate(agents) :
        print("Agent: %s" % agent.info())
        print("* Sub-Problem: %d *" % i)
        print_problem(pro = agent.pro)
        print("-" * 50)

    monitor = Monitor()
    # print("Running output:")
    time_cost = monitor.run(agents = agents, timeout = 1)
    # print("-" * 50)
    print("Time cost: %s" % time_cost)
    print("-" * 50)
    print("Monitor.mem: %s" % monitor.mem)
    print("-" * 50)
    final = {}
    for assign in monitor.mem :
        final.update(assign)
    print("Final: %s" % final)
    print("-" * 50)
    view_logs(log_dir = log_dir, style = "timeline")
    print("-" * 50)
    print("Done.")
