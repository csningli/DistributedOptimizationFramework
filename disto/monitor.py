
import time
from multiprocessing import Process

from disto.utils import *

def run_agent(agent, in_queue, out_queue, timeout = 60) :
    start_time = time.time()
    while time.time() - start_time < timeout :
        msg = get_one_item_in_queue(in_queue)
        result = agent.process(msgs = [msg])
        put_items_to_queue(out_queue, result.get("msgs", []))

class Message(object) :
    def __init__(self, src, dest, content) :
        self.src = src
        self.dest = dest
        self.content = content

class Monitor(object) :
    def __init__(self) :
        pass
    def run(self, agents, timeout = 60) :
        in_queues = [queue.Queue() for i in range(len(agents))]
        out_queues = [queue.Queue() for i in range(len(agents))]
        pool = [Process(target = run_agent, kwargs = {
            "agent" : agents[i], "in_queue": in_queues[i], "out_queue" : out_queues[i],
            "timeout" : timeout}) for i in range(len(agents))]
        for process in pool :
            process.start()
        start_time = time.time()
        while time.time() - start_time < timeout :
            for i, out_queue in enumerate(out_queues) :
                msg = get_one_item_in_queue(out_queue)
                if msg is not None :
                    dest = []
                    if msg.dest is None :
                        dest = list(range(len(agents)))
                    elif hasattr(msg.dest, "__item__") :
                        dest = msg.dest
                    else :
                        dest.append(msg.dest)
                    for i in dest :
                        put_one_item_to_queue(in_queues[i], msg)
        for process in pool :
            process.join()
