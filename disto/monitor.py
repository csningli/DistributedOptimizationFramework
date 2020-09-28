
import time
from multiprocessing import Process

from disto.utils import *

def run_agent(agent, in_queue, out_queue, timeout = 60) :
    start_time = time.time()
    while time.time() - start_time < timeout :
        msgs = get_all_items_in_queue(q)
        agent.run()


class Monitor(object) :
    def __init__(self) :
        pass

    def run(self, agents, timeout = 60) :
        result = {"start" : get_current_time(), "finish" : None}
        pool = [Process(target = run_agent, kwargs = {"agent" : agent, "timeout" : timeout}) for agent in agents]
        for process in pool :
            process.start()
        for process in pool :
            process.join()
        result["finish"] = get_current_time()
        result["asgns"] = {agent.id : agent.asgn for agent in agents}
        return result
