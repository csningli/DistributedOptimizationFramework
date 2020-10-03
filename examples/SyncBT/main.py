
import networkx as nx

from disto.monitor import Monitor
from disto.agent import SyncBTAgent

if __name__ == "__main__" :
    # graph = nx.generators.random_graphs.fast_gnp_random_graph(n = 5, p = 0.6)
    # result = color_graph(graph = graph, num_colors = 4)
    n = 10
    pros = [None] * n
    agents = [SyncBTAgent(id = i, pro = pros[i]) for i in range(n)]
    Monitor().run(agents = agents, timeout = 5)
    print("Done")
