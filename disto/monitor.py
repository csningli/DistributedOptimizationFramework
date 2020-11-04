
import time
from multiprocessing import Process, Queue

from disto.utils import *

def run_agent(agent, in_queue, out_queue, timeout = 60) :
    start_time = time.time()
    while time.time() - start_time < timeout :
        in_msg = get_one_item_in_queue(in_queue)
        msgs = [] if in_msg is None else [in_msg]
        result = agent.process(msgs = msgs)
        out_msgs = result.get("msgs", [])
        if len(out_msgs) > 0 :
            put_items_to_queue(out_queue, items = out_msgs)

class Message(object) :
    def __init__(self, src, dest, content) :
        '''
        dest :  single id - the id of the destination agent;
                list of ids - list of ids of the destination agents;
                None - all the agents other than the one of src id.
        '''
        self.src = src
        self.dest = dest
        self.content = content

class CommMessage(Message) :
    def __init__(self, src, dest, content) :
        super(CommMessage, self).__init__(src = src, dest = dest, content = content)

class SysMessage(Message) :
    def __init__(self, src, content) :
        super(SysMessage, self).__init__(src = src, dest = None, content = content)

class Monitor(object) :
    def __init__(self) :
        self.mem = []
        self.running = False

    def run(self, agents, timeout = 60) :
        in_queues = [Queue() for i in range(len(agents))]
        out_queues = [Queue() for i in range(len(agents))]
        pool = [Process(target = run_agent, kwargs = {
            "agent" : agents[i], "in_queue": in_queues[i], "out_queue" : out_queues[i],
            "timeout" : timeout}) for i in range(len(agents))]
        for process in pool :
            process.start()

        self.running = True
        sys_msgs = []
        start_time = time.time()
        while self.running == True and time.time() - start_time < timeout :
            for i, out_queue in enumerate(out_queues) :
                msg = get_one_item_in_queue(out_queue)
                if isinstance(msg, SysMessage) :
                    # print("found msg to monitor from agent %d: %s" % (msg.src, msg.content))
                    sys_msgs.append(msg)
                elif isinstance(msg, CommMessage) :
                    # print("found msg to agent %d from agent %d." % (msg.dest, msg.src))
                    dest = []
                    if msg.dest is None :
                        dest = [agent.id for agent in agents if agent.id != msg.src]
                    elif hasattr(msg.dest, "__item__") :
                        dest = msg.dest
                    else :
                        dest.append(msg.dest)
                    for j in dest :
                        put_one_item_to_queue(in_queues[j], msg)
            if len(sys_msgs) > 0 :
                self.handle_sys_msgs(msgs = sys_msgs)
                sys_msgs = []
        for process in pool :
            process.join()

    def handle_sys_msgs(self, msgs) :
        for msg in msgs :
            if msg.content == None :
                self.running = False
            else :
                self.mem.append(msg.content)
