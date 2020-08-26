
import time
from multiprocessing import Process

from disto.utils import *

# uniform solver independent problems

def run_agent(agent, rounds = 1) :
    agent.run(rounds = rounds)

def usip_deploy(agents, solv, probs, rounds = 1) :
    result = {"start" : get_current_time(), "finish" : None}
    for agent, prob in zip(agents, probs) :
        agent.prob = prob
        agent.solv = solv
    pool = [Process(target = run_agent, kwargs = {"agent" : agent, "rounds" : rounds}) for agent in agents]
    for process in pool :
        process.start()
    for process in pool :
        process.join()
    result["finish"] = get_current_time()
    result["asgns"] = {agent.id : agent.asgn for agent in agents}
    return result
