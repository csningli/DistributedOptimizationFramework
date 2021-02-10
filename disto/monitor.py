
import time
from multiprocessing import Process, Queue

from disto.utils import *

def run_agent(agent, in_queue, out_queue, timeout = 60) :
    start_time = time.time()
    while time.time() - start_time < timeout :
        msgs = get_all_items_in_queue(in_queue)
        result = agent.process(msgs = msgs)
        out_msgs = result.get("msgs", [])
        if len(out_msgs) > 0 :
            put_items_to_queue(out_queue, items = out_msgs)
        if agent.log_filepath != "" and len(agent.logs) > 0 :
            agent.dump_logs()
            agent.logs = []

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

class OkMessage(CommMessage) :
    def __init__(self, src, dest, content) :
        super(OkMessage, self).__init__(src = src, dest = dest, content = content)

class NogoodMessage(CommMessage) :
    def __init__(self, src, dest, content) :
        super(NogoodMessage, self).__init__(src = src, dest = dest, content = content)

class LinkMessage(CommMessage) :
    def __init__(self, src, dest, content) :
        super(LinkMessage, self).__init__(src = src, dest = dest, content = content)

class TerminateMessage(CommMessage) :
    def __init__(self, src, dest, content) :
        super(TerminateMessage, self).__init__(src = src, dest = dest, content = content)

class ThresholdMessage(CommMessage) :
    def __init__(self, src, dest, content) :
        super(ThresholdMessage, self).__init__(src = src, dest = dest, content = content)

class CostMessage(CommMessage) :
    def __init__(self, src, dest, content) :
        super(CostMessage, self).__init__(src = src, dest = dest, content = content)

class ValueMessage(CommMessage) :
    def __init__(self, src, dest, content) :
        super(ValueMessage, self).__init__(src = src, dest = dest, content = content)

class UtilMessage(CommMessage) :
    def __init__(self, src, dest, content) :
        super(UtilMessage, self).__init__(src = src, dest = dest, content = content)

class DoneMessage(CommMessage) :
    def __init__(self, src, dest, content) :
        super(DoneMessage, self).__init__(src = src, dest = dest, content = content)

class SysMessage(Message) :
    def __init__(self, src, content) :
        super(SysMessage, self).__init__(src = src, dest = None, content = content)

class Monitor(object) :
    def __init__(self) :
        self.mem = []
        self.running = False

    def run(self, agents, timeout = 60, tolerance = None) :
        in_queues = [Queue() for i in range(len(agents))]
        out_queues = [Queue() for i in range(len(agents))]
        pool = [Process(target = run_agent, kwargs = {
            "agent" : agents[i], "in_queue": in_queues[i], "out_queue" : out_queues[i],
            "timeout" : timeout}) for i in range(len(agents))]
        for process in pool :
            process.start()

        self.running = True
        t_count = tolerance
        sys_msgs = []
        start_time = time.time()
        finish_time = None
        while self.running == True and time.time() - start_time < timeout and (t_count is None or t_count > 0) :
            if t_count is not None :
                t_count -= 1
            for i, out_queue in enumerate(out_queues) :
                msg = get_one_item_in_queue(out_queue)
                if isinstance(msg, SysMessage) :
                    sys_msgs.append(msg)
                    t_count = tolerance
                elif isinstance(msg, CommMessage) :
                    dest = []
                    if msg.dest is None :
                        dest = [agent.id for agent in agents if agent.id != msg.src]
                    elif hasattr(msg.dest, "__item__") :
                        dest = msg.dest
                    else :
                        dest.append(msg.dest)
                    for j in dest :
                        put_one_item_to_queue(in_queues[j], msg)
                    t_count = tolerance
            if len(sys_msgs) > 0 :
                finish_time = time.time()
                self.handle_sys_msgs(msgs = sys_msgs)
                sys_msgs = []
        finish_time = time.time() if finish_time is None else finish_time

        for process in pool :
            process.terminate()
            process.join()

        return finish_time - start_time

    def handle_sys_msgs(self, msgs) :
        for msg in msgs :
            if msg.content == None :
                self.running = False
            else :
                self.mem.append(msg.content)
