
import os, math
import networkx as nx

from disto.problem import total_cost, GraphColoringProblem
from disto.agent import AsynWCSAgent
from disto.monitor import Monitor
from disto.utils import print_problem, get_datetime_stamp, view_logs

# In this example, Asynchronous Weak-Commitment Search (Makoto Yokoo,
# "Asynchronous Weak-commitment Search for Solving Distributed Constraint Satisfaction Problems", 1995)
# is used to solve the graph coloring problem, which is modeled in a DCSP form.

if __name__ == "__main__" :
    print("Done")
