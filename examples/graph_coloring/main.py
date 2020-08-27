
import networkx as nx

from disto.agent import Agent, ProcessDataAccess
from disto.deploy import usip_deploy

def color_graph(graph, num_colors) :
    n = graph.number_of_nodes()
    probs = [{"graph" : nx.Graph(), "num_colors" : num_colors} for i in range(n)]
    for i in range(n) :
        probs[i]["graph"].add_node(i)
        for j in graph.adj[i] :
            probs[i]["graph"].add_node(j)
    for edge in graph.edges :
        for i in range(n) :
            if edge[0] in probs[i]["graph"].nodes and edge[1] in probs[i]["graph"].nodes :
                probs[i]["graph"].add_edge(*edge)

    print("Global graph: %s" % graph.edges)
    for i in range(n) :
        print("Subgraph at node %d: %s" % (i, probs[i]["graph"].edges))
    print("-" * 50)

    agents = [Agent(id = i, data = ProcessDataAccess()) for i in range(n)]
    result = usip_deploy(agents = agents, solv = None, probs = probs, rounds = 5)
    return result

if __name__ == "__main__" :
    graph = nx.generators.random_graphs.fast_gnp_random_graph(n = 5, p = 0.6)
    result = color_graph(graph = graph, num_colors = 4)
    print("-" * 50)
    print("Start:   %s" % result["start"])
    print("Finish:  %s" % result["finish"])
    print("-" * 50)
    for id in sorted(list(result["asgns"].keys())) :
        print("Agent %s's assignment: %s" % (id, result["asgns"][id]))
