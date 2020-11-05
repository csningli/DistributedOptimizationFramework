
import os, copy, json, numpy

from disto.problem import *
from disto.monitor import *
from disto.utils import *

class Agent(object) :
    def __init__(self, id, pro, log_dir = ".") :
        self.id = id
        self.pro = pro
        self.assign = {var : None for var in self.pro.vars.keys()}
        self.logs = []

    def info(self) :
        return f"<<Disto.{type(self).__name__} id = {self.id}; pro = {True if self.pro is not None else False}>>"

    def log(self, line) :
        self.logs.append("[%s]%s" % (get_current_time(), line))

    def log_msg(self, label, msg) :
        self.log("%s/%s/%s/%s/%s" % (label, type(msg).__name__, msg.src, msg.dest, msg.content))

    def process(self, msgs) :
        result = {"msgs" : []}
        return result

    def dump_logs(self) :
        filename = "%s-agent_%d.log" % (get_datetime_stamp(), self.id)
        json.dump(self.logs, open(os.path.join(self.log_dir, filename), 'w'))


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
                self.assign, u = fix_assign(pro = self.pro, assign = self.assign, order_list = self.sorted_vars)
                self.log("start/init cpa")
                if u is None :
                    result["msgs"].append(SysMessage(src = self.id, content = None))
                else :
                    if self.next is None :
                        result["msgs"].append(SysMessage(src = self.id, content = cpa))
                        result["msgs"].append(SysMessage(src = self.id, content = None))
                    else :
                        result["msgs"].append(CommMessage(src = self.id, dest = self.next, content = self.assign))
            elif len(msgs) > 0 :
                msg = msgs[0]
                self.log_msg("receive", msg)
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
                        self.log_msg("send", result["msgs"][-1])
                    else :
                        result["msgs"].append(CommMessage(src = self.id, dest = self.prev, content = cpa))
                else :
                    for var in self.assign.keys() :
                        self.assign[var] = cpa[var]
                    if self.next is None :
                        result["msgs"].append(SysMessage(src = self.id, content = cpa))
                        result["msgs"].append(SysMessage(src = self.id, content = None))
                    else :
                        result["msgs"].append(CommMessage(src = self.id, dest = self.next, content = cpa))
            for msg in result["msgs"] :
                self.log_msg("send", msg)
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
