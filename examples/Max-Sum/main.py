
import os, math, functools
import networkx as nx

from disto.problem import total_cost, GraphColoringProblem
from disto.agent import MaxSumAgent
from disto.monitor import Monitor
from disto.utils import get_var_host, print_problem, get_datetime_stamp, view_logs, get_constraint_graph, get_pseudo_tree, get_factor_nodes

# In this example, Max-Sum # (A. Farinelli, A. Rogers, A. Petcu†, and N. R. Jennings,
# "Decentralised Coordination of Low-Power Embedded Devices Using the Max-Sum Algorithm")
# is used to solve the optimization version of the graph coloring problem,
# which is modeled in a DCOP form. In the problem, the cost is defined as the number of violated constraints.

if __name__ == "__main__" :
    log_dir = "logs/%s" % get_datetime_stamp()
    if not os.path.isdir(log_dir) :
        os.mkdir(log_dir)

    n = 3 # number of variables

    # graph = nx.generators.random_graphs.fast_gnp_random_graph(n = n, p = 0.6)

    graph = nx.Graph()
    for i in range(n) :
        graph.add_node(str(i))

    d = 1
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
    # print(avars)

    var_host = get_var_host(avars = avars)
    var_nodes, fun_nodes, fun_host = get_factor_nodes(pro = pro, avars = avars, var_node_cls = MaxSumAgent.VariableNode, fun_node_cls = MaxSumAgent.FunctionNode, all_vars = pro.vars)
    for agent_var_nodes in var_nodes :
        for var_node in agent_var_nodes.values() :
            var_node.fnb_msgs = {fnb.name : [1] * len(var_node.domain.values) for fnb in var_node.fnbs}
    list(var_nodes[0].values())[0].source = ""

    sub_pros = pro.split(avars = avars)
    agents = []
    for i in range(m) :
        agents.append(MaxSumAgent(id = i, pro = sub_pros[i],
            var_nodes = var_nodes[i], fun_nodes = fun_nodes[i], limit = 10,
            var_host = var_host, fun_host = fun_host, log_dir = log_dir))

    for i, agent in enumerate(agents) :
        print("Agent: %s" % agent.info())
        print("* Sub-Problem: %d *" % i)
        print_problem(pro = agent.pro)
        print("-" * 50)

    monitor = Monitor()
    time_cost = monitor.run(agents = agents, timeout = 0.2)
    print("Time cost: %s" % time_cost)
    print("-" * 50)
    print("Monitor.mem: %s" % monitor.mem)
    print("-" * 50)
    if len(monitor.mem) > 0 :
        final = {}
        for assign in monitor.mem :
            final = {**final, **assign}
        print("Final: %s" % final)
        cost, _ = total_cost(cons = pro.cons, assign = final)
        print("Cost: %s" % cost)
        print("-" * 50)
    view_logs(log_dir = log_dir, style = "timeline")
    print("-" * 50)
