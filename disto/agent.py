
import numpy, copy

from disto.problem import *
from disto.monitor import *

class Agent(object) :
    def __init__(self, id, pro) :
        self.id = id
        self.pro = pro
        self.assign = {var : None for var in self.pro.vars.keys()}

    def info(self) :
        return f"<<Disto.{type(self).__name__} id = {self.id}; pro = {True if self.pro is not None else False}>>"

    def process(self, msgs) :
        msgs = []
        return {"msgs" : msgs}

class SyncBTAgent(Agent) :
    def __init__(self, id, pro, prev, next) :
        super(SyncBTAgent, self).__init__(id = int(id), pro = pro)
        self.prev = prev
        self.next = next
        self.sorted_vars = sorted(list(self.pro.vars.keys()))
        self.cpa = {}

    def process(self, msgs) :
        result = {"msgs" : []}
        if len(self.sorted_vars) > 0 :
            if self.prev is None and self.assign[self.sorted_vars[0]] is None :
                self.assign = init_assign(vars = self.pro.vars, order_list = self.sorted_vars)
                self.assgin, u = fix_assign(pro = self.pro, assign = self.assign, order_list = self.sorted_vars)
                print(self.assign, u)
                if u is None :
                    result["msgs"].append(SysMessage(src = self.id, content = None))
                    print("agent %d send msg to monitor." % self.id)
                else :
                    if self.next is None :
                        result["msgs"].append(SysMessage(src = self.id, content = cpa))
                        result["msgs"].append(SysMessage(src = self.id, content = None))
                    else :
                        result["msgs"].append(CommMessage(src = self.id, dest = self.next, content = self.assign))
                        print("agent %d send msg to agent %d." % (self.id, self.next))
            elif len(msgs) > 0 :
                msg = msgs[0]
                print("agent %d get message from agent %d." % (self.id, msg.src))
                if msg.src == self.prev :
                    self.cpa = copy.deepcopy(msg.content)
                    if self.assign[self.sorted_vars[0]] is None :
                        self.assign = init_assign(vars = self.pro.vars, order_list = self.sorted_vars)
                elif msg.src == self.next :
                    self.assign = next_assign(self.assign, vars = self.pro.vars, order_list = self.sorted_vars)
                cpa = copy.deepcopy(self.cpa)
                cpa.update(self.assign)
                cpa, u = fix_assign(pro = self.pro, assign = cpa, order_list = self.sorted_vars)
                if u is None :
                    self.assign = init_assign(vars = self.pro.vars, order_list = self.sorted_vars)
                    if self.prev is None :
                        result["msgs"].append(SysMessage(src = self.id, content = None))
                    else :
                        result["msgs"].append(CommMessage(src = self.id, dest = self.prev, content = cpa))
                        print("agent %d send msg to agent %d." % (self.id, self.prev))
                else :
                    for var in self.assign.keys() :
                        self.assign[var] = cpa[var]
                    if self.next is None :
                        result["msgs"].append(SysMessage(src = self.id, content = cpa))
                        result["msgs"].append(SysMessage(src = self.id, content = None))
                    else :
                        result["msgs"].append(CommMessage(src = self.id, dest = self.next, content = cpa))
                        print("agent %d send msg to agent %d." % (self.id, self.next))
        return result

class AsynBTAgent(Agent) :
    def __init__(self, id, pro, last_id) :
        super(AsynBTAgent, self).__init__(id = int(id), pro = pro)
        self.last_id = last_id
        self.sorted_vars = sorted(list(self.pro.vars.keys()))
        self.assign = {var : None for var in self.sorted_vars}
        self.status = "created"

    def process(self, msgs) :
        msgs = []
        # if None in self.assign.values() :
        return {"msgs" : msgs}
