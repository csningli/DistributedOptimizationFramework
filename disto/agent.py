
import os, copy, numpy

from disto.problem import *
from disto.monitor import *
from disto.utils import *

class Agent(object) :
    def __init__(self, id, pro, log_dir = "") :
        self.id = id
        self.pro = pro
        self.assign = {var : None for var in self.pro.vars.keys()}
        self.logs = []
        self.log_filepath = ""
        if log_dir != "" :
            self.log_filepath = os.path.join(log_dir, "%s-agent_%d.log" % (get_datetime_stamp(), self.id))

    def info(self) :
        return f"<<Disto.{type(self).__name__} id = {self.id}; pro = {True if self.pro is not None else False}>>"

    def log(self, line) :
        self.logs.append("[%s] %s" % (get_current_time(), line))

    def log_msg(self, label, msg) :
        self.log("%s/%s/%s/%s/%s" % (label, type(msg).__name__, msg.src, msg.dest, msg.content))

    def process(self, msgs) :
        result = {"msgs" : []}
        return result

    def dump_logs(self) :
        filename = "%s-agent_%d.log" % (get_datetime_stamp(), self.id)
        with open(self.log_filepath, 'a') as f :
            f.writelines([line + "\n" for line in self.logs])

class SyncBTAgent(Agent) :
    def __init__(self, id, pro, prev, next, log_dir = "") :
        super(SyncBTAgent, self).__init__(id = int(id), pro = pro, log_dir = log_dir)
        self.prev = prev
        self.next = next
        self.sorted_vars = sorted(list(self.pro.vars.keys()))
        self.cpa = {}

    def process(self, msgs) :
        result = {"msgs" : []}
        if len(self.sorted_vars) > 0 :
            if self.prev is None and self.assign[self.sorted_vars[0]] is None :
                self.assign = init_assign(vars = self.pro.vars, order_list = self.sorted_vars)
                self.assign, u, violated = fix_assign(pro = self.pro, assign = self.assign, order_list = self.sorted_vars)
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
                cpa, u, violated = fix_assign(pro = self.pro, assign = cpa, order_list = self.sorted_vars)
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
    def __init__(self, id, pro, outgoings, var_mapping, log_dir = "") :
        super(AsynBTAgent, self).__init__(id = int(id), pro = pro, log_dir = log_dir)
        self.outgoings = outgoings
        self.var_mapping = var_mapping
        self.sorted_vars = sorted(list(self.pro.vars.keys()))
        self.view = {}

    def process(self, msgs) :
        result = {"msgs" : []}
        if len(self.sorted_vars) > 0 :
            if self.assign[self.sorted_vars[0]] is None :
                self.assign = init_assign(vars = self.pro.vars, order_list = self.sorted_vars)
                self.assign, u, violated = fix_assign(pro = self.pro, assign = self.assign, order_list = self.sorted_vars)
                self.log("init", self.assign)
                if u is None :
                    result["msgs"].append(SysMessage(src = self.id, content = None))
                else :
                    for id in self.outgoings :
                        result["msgs"].append(OkMessage(src = self.id, dest = id, content = self.assign))
            elif len(msgs) > 0 :
                for msg in msgs :
                    self.log_msg("receive", msg)
                    assign_updated = False
                    if isinstance(msg, OkMessage) and msg.src < self.id :
                        self.view.update(msg.content)
                        if self.assign[self.sorted_vars[0]] is None :
                            self.assign = init_assign(vars = self.pro.vars, order_list = self.sorted_vars)
                    elif isinstance(msg, NogoodMessage) and msg.src > self.id :
                        vars = list(self.content.keys())
                        forbidden_con = ForbiddenConstraint(vars = vars, values = [self.content[var] for var in vars])
                        self.pro.cons.append(forbidden_con)
                        ids = []
                        for var in vars :
                            id = var_mapping(var)
                            if var not in self.view and id not in ids :
                                ids.append(id)
                        for id in ids :
                            result["msgs"].append(LinkMessage(src = self.id, dest = id, content = None))
                        consistent = True
                        for var, value in msg.content.items() :
                            if (var not in self.vars and var not in self.view) or
                                    (var in self.vars and value != self.assign[var]) or
                                    (var in self.view and value != self.view[var]) :
                                consistent = False
                                break
                        if consistent == True :
                            self.assign = next_assign(self.assign, vars = self.pro.vars, order_list = self.sorted_vars)
                    elif isinstance(msg, LinkMessage) and msg.src > self.id :
                        if msg.src not in self.outgings :
                            self.outgings.append(msg.src)
                            
                    if assign_updated == True :
                        cpa = copy.deepcopy(self.view)
                        cpa.update(self.assign)
                        cpa, u, violated = fix_assign(pro = self.pro, assign = cpa, order_list = self.sorted_vars)
                        if u is None :
                            self.assign = init_assign(vars = self.pro.vars, order_list = self.sorted_vars)
                            min_var = min([min([var for var in con.vars if var not in self.sorted_vars]) for con in violated])
                            id = self.var_mapping[min_var]
                            context = {}
                            for con in vioalted :
                                context.update({var : self.view[var] for var in con.vars if var not in self.vars})
                            result["msgs"].append(NogoodMessage(src = self.id, dest = id, content = context))
                        else :
                            for var in self.assign.keys() :
                                self.assign[var] = cpa[var]
                            for id in self.outgoings :
                                result["msgs"].append(OkMessage(src = self.id, dest = id, content = self.assign))
            for msg in result["msgs"] :
                self.log_msg("send", msg)
        return result
