
from disto.agent import Agent, ProcessDataAccess
from disto.deploy import usip_deploy

def graph_coloring(n) :
    agents = [Agent(id = i, data = ProcessDataAccess()) for i in range(n)]
    probs = [None] * n
    result = usip_deploy(agents = agents, solv = None, probs = probs, rounds = 5)
    return result

if __name__ == "__main__" :
    result = n_queens(n = 2)
    print("-" * 50)
    print("Start:   %s" % result["start"])
    print("Finish:  %s" % result["finish"])
    print("-" * 50)
    for id in sorted(list(result["asgns"].keys())) :
        print("Agent %s's assignment: %s" % (id, result["asgns"][id]))
