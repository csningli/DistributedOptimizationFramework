
import os, copy, numpy, math, itertools

from disto.problem import *
from disto.monitor import *
from disto.utils import *

class Agent(object) :
    def __init__(self, id, pro, log_dir = "") :
        self.id = id
        self.pro = pro
        self.init_assign = init_assign
        self.next_assign = next_assign
        self.fix_assign = fix_assign
        self.assign = {var : None for var in self.pro.vars.keys()}
        self.log_filepath = "" if log_dir == "" else os.path.join(log_dir, "%s-agent_%d.log" % (get_datetime_stamp(), self.id))
        self.logs = []

    def info(self) :
        return f"<<Disto.{type(self).__name__} id = {self.id}; pro = {type(self.pro).__name__}>>"

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
                self.assign = self.init_assign(vars = self.pro.vars, order_list = self.sorted_vars)
                self.assign, cost, violated = self.fix_assign(pro = self.pro, assign = self.assign, order_list = self.sorted_vars)
                self.log("start/init cpa")
                if cost is None :
                    result["msgs"].append(SysMessage(src = self.id, content = None))
                else :
                    if self.next is None :
                        result["msgs"].append(SysMessage(src = self.id, content = copy.deepcopy(self.assign)))
                        result["msgs"].append(SysMessage(src = self.id, content = None))
                    else :
                        result["msgs"].append(CommMessage(src = self.id, dest = self.next, content = copy.deepcopy(self.assign)))
            elif len(msgs) > 0 :
                msg = msgs[0]
                self.log_msg("receive", msg)
                if msg.src == self.prev :
                    self.cpa = copy.deepcopy(msg.content)
                    if self.assign[self.sorted_vars[0]] is None :
                        self.assign = self.init_assign(vars = self.pro.vars, order_list = self.sorted_vars)
                elif msg.src == self.next :
                    self.assign = self.next_assign(self.assign, vars = self.pro.vars, order_list = self.sorted_vars)
                cpa = {**self.cpa, **self.assign}
                cpa, cost, violated = self.fix_assign(pro = self.pro, assign = cpa, order_list = self.sorted_vars)
                if cost is None :
                    self.assign = self.init_assign(vars = self.pro.vars, order_list = self.sorted_vars)
                    if self.prev is None :
                        result["msgs"].append(SysMessage(src = self.id, content = None))
                        self.log_msg("send", result["msgs"][-1])
                    else :
                        result["msgs"].append(CommMessage(src = self.id, dest = self.prev, content = None))
                else :
                    for var in self.assign.keys() :
                        self.assign[var] = cpa[var]
                    if self.next is None :
                        result["msgs"].append(SysMessage(src = self.id, content = copy.deepcopy(cpa)))
                        result["msgs"].append(SysMessage(src = self.id, content = None))
                    else :
                        result["msgs"].append(CommMessage(src = self.id, dest = self.next, content = copy.deepcopy(cpa)))
            for msg in result["msgs"] :
                self.log_msg("send", msg)
        return result

class SyncBBAgent(Agent) :
    def __init__(self, id, pro, prev, next, head, tail, log_dir = "") :
        super(SyncBBAgent, self).__init__(id = int(id), pro = pro, log_dir = log_dir)
        self.prev = prev
        self.next = next
        self.head = head
        self.tail = tail
        self.sorted_vars = sorted(list(self.pro.vars.keys()))
        self.cpa = {}
        self.cpa_cost = 0
        self.best = {}
        self.upper = math.inf

    def process(self, msgs) :
        result = {"msgs" : []}
        if len(self.sorted_vars) > 0 :
            if self.prev is None and self.assign[self.sorted_vars[0]] is None :
                self.assign = self.init_assign(vars = self.pro.vars, order_list = self.sorted_vars)
                self.log("start/init cpa")
                if self.assign is None :
                    result["msgs"].append(SysMessage(src = self.id, content = None))
                else :
                    self.assign, cost, violated = self.fix_assign(pro = self.pro, assign = self.assign, order_list = self.sorted_vars)
                    while self.assign is not None and self.cpa_cost + cost > self.upper :
                        self.assign = self.next_assign(self.assign, vars = self.pro.vars, order_list = self.sorted_vars)
                        self.assign, cost, violated = self.fix_assign(pro = self.pro, assign = self.assign, order_list = self.sorted_vars)
                    if self.assign is None :
                        result["msgs"].append(SysMessage(src = self.id, content = None))
                    else :
                        if self.next is None :
                            result["msgs"].append(SysMessage(src = self.id, content = (copy.deepcopy(self.assign), cost, self.upper)))
                            result["msgs"].append(SysMessage(src = self.id, content = None))
                        else :
                            result["msgs"].append(CommMessage(src = self.id, dest = self.next, content = (copy.deepcopy(self.assign), cost, self.upper)))
            elif len(msgs) > 0 :
                msg = msgs[0]
                self.log_msg("receive", msg)
                if msg.src == self.prev :
                    self.cpa = copy.deepcopy(msg.content[0])
                    self.cpa_cost = msg.content[1]
                    self.upper = msg.content[2]
                    if self.assign[self.sorted_vars[0]] is None :
                        self.assign = self.init_assign(vars = self.pro.vars, order_list = self.sorted_vars)
                elif msg.src == self.tail and msg.content is not None :
                    self.best = msg.content[0]
                    self.upper = msg.content[1]
                    self.assign = self.next_assign(self.assign, vars = self.pro.vars, order_list = self.sorted_vars)
                elif msg.src == self.next :
                    self.assign = self.next_assign(self.assign, vars = self.pro.vars, order_list = self.sorted_vars)

                if self.assign is None :
                    result["msgs"] += self.backtrack()
                else :
                    cpa = {**self.cpa, **self.assign}
                    cpa, cost, violated = self.fix_assign(pro = self.pro, assign = cpa, order_list = self.sorted_vars)
                    while self.assign is not None and self.cpa_cost + cost > self.upper :
                        self.assign = self.next_assign(self.assign, vars = self.pro.vars, order_list = self.sorted_vars)
                        cpa = {**self.cpa, **self.assign}
                        cpa, cost, violated = self.fix_assign(pro = self.pro, assign = cpa, order_list = self.sorted_vars)
                    if self.assign is None :
                        result["msgs"] += self.backtrack()
                    else :
                        for var in self.assign.keys() :
                            self.assign[var] = cpa[var]
                        if self.next is None :
                            result["msgs"].append(CommMessage(src = self.id, dest = self.head, content = (copy.deepcopy(cpa), self.cpa_cost + cost, self.upper)))
                        else :
                            result["msgs"].append(CommMessage(src = self.id, dest = self.next, content = (copy.deepcopy(cpa), self.cpa_cost + cost, self.upper)))
            for msg in result["msgs"] :
                self.log_msg("send", msg)
        return result

    def backtrack(self) :
        msgs = []
        self.assign = self.init_assign(vars = self.pro.vars, order_list = self.sorted_vars)
        if self.prev is None :
            msgs.append(SysMessage(src = self.id, content = (copy.deepcopy(self.best), self.upper, self.upper)))
            msgs.append(SysMessage(src = self.id, content = None))
            self.log_msg("send", msgs[-1])
        else :
            msgs.append(CommMessage(src = self.id, dest = self.prev, content = None))
        return msgs

class AsynBTAgent(Agent) :
    def __init__(self, id, pro, outgoings, var_host, con_host, log_dir = "") :
        super(AsynBTAgent, self).__init__(id = int(id), pro = pro, log_dir = log_dir)
        self.var_host = var_host
        self.con_host = con_host
        self.outgoings = outgoings
        self.sorted_vars = sorted(list(self.pro.vars.keys()))
        self.view = {}

    def process(self, msgs) :
        result = {"msgs" : []}
        if len(self.sorted_vars) > 0 :
            if self.assign[self.sorted_vars[0]] is None :
                self.assign = self.init_assign(vars = self.pro.vars, order_list = self.sorted_vars)
                self.assign, cost, violated = self.fix_assign(pro = self.pro, assign = self.assign, order_list = self.sorted_vars)
                self.log("init/%s" % self.assign)
                if cost is None :
                    result["msgs"].append(SysMessage(src = self.id, content = None))
                else :
                    for id in self.outgoings :
                        result["msgs"].append(OkMessage(src = self.id, dest = id, content = copy.deepcopy(self.assign)))
            elif len(msgs) > 0 :
                cpa = {**self.view, **self.assign}
                for msg in msgs :
                    self.log_msg("receive", msg)
                    if isinstance(msg, LinkMessage) and msg.src > self.id and msg.src not in self.outgings :
                        self.outgings.append(msg.src)
                    elif isinstance(msg, OkMessage) and msg.src < self.id :
                        cpa.update(msg.content)
                for msg in msgs :
                    if isinstance(msg, NogoodMessage) and msg.src > self.id :
                        vars = list(msg.content.keys())
                        forbidden_con = ForbiddenConstraint(vars = vars, values = [msg.content[var] for var in vars])
                        self.pro.cons.append(forbidden_con)
                        ids = []
                        for var in vars :
                            id = self.var_host(var)
                            if var not in self.view and var not in self.assign and id not in ids :
                                ids.append(id)
                        for id in ids :
                            result["msgs"].append(LinkMessage(src = self.id, dest = id, content = None))
                        if check_dict_compatible(cpa, msg.content) == True :
                            cpa.update(self.next_assign(self.assign, vars = self.pro.vars, order_list = self.sorted_vars))
                if cpa != {**self.view, **self.assign} :
                    cpa, cost, violated = self.fix_assign(pro = self.pro, assign = cpa, order_list = self.sorted_vars)
                    self.view.update({var : cpa[var] for var in cpa.keys() if var not in self.assign})
                    if cost is None :
                        self.assign = self.init_assign(vars = self.pro.vars, order_list = self.sorted_vars)
                        ids = []
                        for con in violated :
                            vars = [var for var in con.vars if var not in self.assign]
                            if len(vars) > 0 :
                                ids.append(max([self.var_host(var) for var in vars]))
                        if len(ids) < 1 :
                            result["msgs"].append(SysMessage(src = self.id, content = None))
                        else :
                            id = max(ids)
                            context = {}
                            for con in violated :
                                context.update({var : cpa[var] for var in con.vars if var not in self.assign})
                            result["msgs"].append(NogoodMessage(src = self.id, dest = id, content = copy.deepcopy(context)))
                    else :
                        if check_dict_compatible(self.assign, cpa) == False :
                            for var in self.assign.keys() :
                                self.assign[var] = cpa[var]
                            for id in self.outgoings :
                                result["msgs"].append(OkMessage(src = self.id, dest = id, content = copy.deepcopy(self.assign)))
                        result["msgs"].append(SysMessage(src = self.id, content = copy.deepcopy(cpa)))
            for msg in result["msgs"] :
                self.log_msg("send", msg)
        return result

class AsynWCSAgent(Agent) :
    def __init__(self, id, pro, neighbors, var_host, log_dir = "") :
        super(AsynWCSAgent, self).__init__(id = int(id), pro = pro, log_dir = log_dir)
        self.neighbors = neighbors
        self.var_host = var_host
        self.fix_assign = fix_assign_min_conflict
        self.priority = 0
        self.sorted_vars = sorted(list(self.pro.vars.keys()))
        self.view = {}
        self.neighbor_priorities = {}

    def process(self, msgs) :
        result = {"msgs" : []}
        if len(self.sorted_vars) > 0 :
            if self.assign[self.sorted_vars[0]] is None :
                self.assign = self.init_assign(vars = self.pro.vars, order_list = self.sorted_vars)
                pro, cons = self.split_pro_with_priorities()
                self.assign, num_conflicts, violated = self.fix_assign(pro = pro, conflict_cons = cons, assign = self.assign, order_list = self.sorted_vars)
                self.log("init/%s" % self.assign)
                if num_conflicts is None :
                    result["msgs"].append(SysMessage(src = self.id, content = None))
                else :
                    for id in self.neighbors :
                        result["msgs"].append(OkMessage(src = self.id, dest = id, content = (self.priority, copy.deepcopy(self.assign))))
            elif len(msgs) > 0 :
                cpa = {**self.view, **self.assign}
                for msg in msgs :
                    self.log_msg("receive", msg)
                    if isinstance(msg, OkMessage) :
                        cpa.update(msg.content[1])
                        self.neighbor_priorities[msg.src] = msg.content[0]
                for msg in msgs :
                    if isinstance(msg, NogoodMessage) and msg.src > self.id :
                        vars = list(msg.content.keys())
                        forbidden_con = ForbiddenConstraint(vars = vars, values = [msg.content[var] for var in vars])
                        self.pro.cons.append(forbidden_con)
                        if check_dict_compatible(cpa, msg.content) == True :
                            cpa.update(self.next_assign(self.assign, vars = self.pro.vars, order_list = self.sorted_vars))
                if cpa != {**self.view, **self.assign} :
                    pro, cons = self.split_pro_with_priorities()
                    cpa, num_conflicts, violated = self.fix_assign(pro = pro, conflict_cons = cons, assign = cpa, order_list = self.sorted_vars)
                    self.view.update({var : cpa[var] for var in cpa.keys() if var not in self.assign})
                    if num_conflicts is None :
                        self.assign = self.init_assign(vars = self.pro.vars, order_list = self.sorted_vars)
                        nogood = {}
                        max_priority = 0
                        ids = []
                        for con in violated :
                            for var in con.vars :
                                id = self.var_host(var)
                                max_priority = max(max_priority, self.neighbor_priorities[id])
                                if var not in self.assign :
                                    nogood[var] = cpa[var]
                                    if id not in ids :
                                        ids.append(id)
                        if len(ids) < 1 : # in such case, there is no element in the nogood.
                            result["msgs"].append(SysMessage(src = self.id, content = None))
                        else :
                            for id in self.neighbors :
                                if len(nogoods[id]) > 0 :
                                    result["msgs"].append(NogoodMessage(src = self.id, dest = id, content = copy.deepcopy(nogood)))
                            self.priority = max_priority + 1
                            for var in self.assign.keys() :
                                self.assign[var] = cpa[var]
                            for id in self.neighbors :
                                result["msgs"].append(OkMessage(src = self.id, dest = id, content = (self.priority, copy.deepcopy(self.assign))))
                    else :
                        if check_dict_compatible(self.assign, cpa) == False :
                            for var in self.assign.keys() :
                                self.assign[var] = cpa[var]
                            for id in self.neighbors :
                                result["msgs"].append(OkMessage(src = self.id, dest = id, content = (self.priority, copy.deepcopy(self.assign))))
                        result["msgs"].append(SysMessage(src = self.id, content = copy.deepcopy(cpa)))
            for msg in result["msgs"] :
                self.log_msg("send", msg)
        return result

    def split_pro_with_priorities(self) :
        pro = Problem(vars = self.pro.vars, cons = [])
        cons = []
        for con in self.pro.cons :
            if max([(-self.neighbor_priorities.get(self.var_host(var), 0), self.var_host(var)) for var in con.vars]) >= (-self.priority, self.id) :
                cons.append(con)
            else :
                pro.cons.append(con)
        return pro, cons

class AdoptAgent(Agent) :
    def __init__(self, id, pro, parent, children, var_host, log_dir = "") :
        super(AdoptAgent, self).__init__(id = int(id), pro = pro, log_dir = log_dir)
        self.parent = parent
        self.children = children
        self.var_host = var_host
        self.sorted_vars = sorted(list(self.pro.vars.keys()))
        self.children_done = {id : False for id in self.children}
        self.backtrack_needed = False    # True if backtrack is needed
        self.done = False       # True if the agent stops renewing the local assignment
        self.terminate = False  # True if received TERMINATE message from the parent
        self.threshold = 0
        self.current_context = {}
        self.lb = {}
        self.ub = {}
        self.t = {}
        self.context = {}
        for d in itertools.product(*[self.pro.vars[var].values for var in self.sorted_vars]) :
            for child in self.children :
                self.lb[(d, child)] = 0
                self.ub[(d, child)] = math.inf
                self.t[(d, child)] = 0
                self.context[(d, child)] = {}
        self.assign = self.update_assign(bound_func = self.get_LB)
        self.backtrack_needed = True
        self.log("init/%s" % self.assign)

    def process(self, msgs) :
        result = {"msgs" : []}
        if len(self.sorted_vars) > 0 :
            if len(msgs) > 0 :
                for msg in msgs :
                    self.log_msg("receive", msg)
                    if isinstance(msg, TerminateMessage) and msg.src == self.parent :
                        self.terminate = True
                        self.current_context = msg.content
                        self.backtrack_needed = True
                    elif isinstance(msg, ThresholdMessage) :
                        self.threshold = msg.content[0]
                        self.maintainThresholdInvariant()
                        self.backtrack_needed = True
                    elif isinstance(msg, DoneMessage) :
                        self.children_done[msg.src] = True
                        if False not in self.children_done.values() :
                            if self.parent is None :
                                result["msgs"].append(SysMessage(src = self.id, content = None))
                            else :
                                result["msgs"].append(DoneMessage(src = self.id, dest = self.parent, content = None))
                for msg in msgs :
                    if isinstance(msg, ValueMessage) and self.terminate == False :
                        for var, value in msg.content.items() :
                            self.current_context[var] = value
                        for d in itertools.product(*[self.pro.vars[var].values for var in self.sorted_vars]) :
                            for child in self.children :
                                if check_dict_compatible(self.context[(d, child)], self.current_context) == False :
                                    self.lb[(d, child)] = 0
                                    self.t[(d, child)] = 0
                                    self.ub[(d, child)] = math.inf
                                    self.context[(d, child)] = {}
                        self.maintainThresholdInvariant()
                        self.backtrack_needed = True
                    if isinstance(msg, CostMessage) :
                        d = tuple([msg.content[1].get(var, self.assign[var]) for var in self.sorted_vars])
                        for var in self.sorted_vars :
                            if var in msg.content[1].keys() :
                                del msg.content[1][var]
                        if self.terminate == False :
                            for var, value in msg.content[1].items() :
                                if self.var_host(var) not in self.children + [self.parent] :
                                    self.current_context[var] = value
                            for dd in itertools.product(*[self.pro.vars[var].values for var in self.sorted_vars]) :
                                for child in self.children :
                                    if check_dict_compatible(self.context[(dd, child)], self.current_context) == False :
                                        self.lb[(dd, child)] = 0
                                        self.t[(dd, child)] = 0
                                        self.ub[(dd, child)] = math.inf
                                        self.context[(dd, child)] = {}
                        if check_dict_compatible(msg.content[1], self.current_context) == True :
                            self.lb[(d, msg.content[0])] = msg.content[2]
                            self.ub[(d, msg.content[0])] = msg.content[3]
                            self.context[(d, msg.content[0])] = msg.content[1]
                            self.maintainChildThresholdInvariant()
                            self.maintainThresholdInvariant()
                        self.backtrack_needed = True

            if self.done == False and self.backtrack_needed == True :
                UB = self.get_UB()
                LB = self.get_LB()
                if self.threshold > UB - 1e-6 :
                    self.assign = self.update_assign(bound_func = self.get_UB)
                elif self.threshold < LB + 1e-6 :
                    self.assign = self.update_assign(bound_func = self.get_LB)
                self.log("update/%s/%s" % (self.id, self.assign))
                for id in self.children :
                    result["msgs"].append(ValueMessage(src = self.id, dest = id, content = self.assign))
                result["msgs"] += self.maintainAllocationInvariant()
                if self.threshold > UB - 1e-6 :
                    if self.terminate == True or self.parent is None :
                        self.done = True
                        result["msgs"].append(SysMessage(src = self.id, content = self.assign))
                        if len(self.children) > 0 :
                            for id in self.children :
                                result["msgs"].append(TerminateMessage(src = self.id, dest = id, content = {**self.current_context, **self.assign}))
                        else :
                            if self.parent is None :
                                result["msgs"].append(SysMessage(src = self.id, content = None))
                            else :
                                result["msgs"].append(DoneMessage(src = self.id, dest = self.parent, content = None))
                if self.parent is not None :
                    result["msgs"].append(CostMessage(src = self.id, dest = self.parent, content = (self.id, self.current_context, LB, UB)))
                self.backtrack_needed = False
            for msg in result["msgs"] :
                self.log_msg("send", msg)
        return result

    def get_delta(self, d) :
        delta = 0
        assign = {self.sorted_vars[i] : d[i] for i in range(len(self.sorted_vars))}
        cpa = {**self.current_context, **assign}
        for con in self.pro.cons :
            x = fit_assign_to_con(cpa, con)
            if x is not None :
                delta += con.cost(x)
        return delta

    def get_LB(self, d = None) :
        LB = math.inf
        if d is not None :
            LB = self.get_delta(d = d)
            if LB < math.inf :
                for child in self.children :
                    LB += self.lb[(d, child)]
        else :
            for d in itertools.product(*[self.pro.vars[var].values for var in self.sorted_vars]) :
                LB_d = self.get_delta(d = d)
                for child in self.children :
                    if LB_d < LB :
                        LB_d += self.lb[(d, child)]
                    else :
                        break
                if LB_d < LB :
                    LB = LB_d
        return LB

    def get_UB(self, d = None) :
        UB = math.inf
        if d is not None :
            UB = self.get_delta(d = d)
            if UB < math.inf :
                for child in self.children :
                    UB += self.ub[(d, child)]
        else :
            for d in itertools.product(*[self.pro.vars[var].values for var in self.sorted_vars]) :
                UB_d = self.get_delta(d = d)
                for child in self.children :
                    if UB_d < UB :
                        UB_d += self.ub[(d, child)]
                    else :
                        break
                if UB_d < UB :
                    UB = UB_d
        return UB

    def update_assign(self, bound_func) :
        assign = {}
        d_min = None
        bound_d_min = math.inf
        for d in itertools.product(*[self.pro.vars[var].values for var in self.sorted_vars]) :
            bound = bound_func(d = d)
            if bound < bound_d_min :
                bound_d_min = bound
                d_min = d
        if d_min is not None :
            assign = {self.sorted_vars[i] : d_min[i] for i in range(len(self.sorted_vars))}
        else :
            assign = {var : self.pro.vars[var].first_value() for var in self.sorted_vars}
        return assign

    def maintainThresholdInvariant(self) :
        LB = self.get_LB()
        if self.threshold < LB :
            self.threshold = LB
        UB = self.get_UB()
        if self.threshold > UB :
            self.threshold = UB

    def maintainAllocationInvariant(self) :
        msgs = []
        d = tuple([self.assign[var] for var in self.sorted_vars])
        delta = self.get_delta(d = d)
        while self.threshold > delta + sum([self.t[(d, child)] for child in self.children]) :
            updated = False
            for child in self.children :
                if self.ub[(d, child)] > self.t[(d, child)] :
                    inc = min(self.ub[(d, child)] - self.t[(d, child)], self.threshold - delta - sum([self.t[(d, child)] for child in self.children]))
                    self.t[(d, child)] += inc
                    updated = True
                    break
            if updated == False :
                break
        while self.threshold < delta + sum([self.t[(d, child)] for child in self.children]) :
            updated = False
            for child in self.children :
                if self.lb[(d, child)] < self.t[(d, child)] :
                    dec = min(self.t[(d, child)] - self.lb[(d, child)],  delta + sum([self.t[(d, child)] for child in self.children]) - self.threshold)
                    self.t[(d, child)] -= dec
                    updated = True
                    break
            if updated == False :
                break
        for child in self.children :
            msgs.append(ThresholdMessage(src = self.id, dest = child, content = (self.t[(d, child)], self.current_context)))
        return msgs

    def maintainChildThresholdInvariant(self) :
        for d in itertools.product(*[self.pro.vars[var].values for var in self.sorted_vars]) :
            for child in self.children :
                if self.t[(d, child)] < self.lb[(d, child)] :
                    self.t[(d, child)] = self.lb[(d, child)]
            for child in self.children :
                if self.t[(d, child)] > self.ub[(d, child)] :
                    self.t[(d, child)] = self.ub[(d, child)]

class DpopAgent(Agent) :
    def __init__(self, id, pro, parent, children, var_host, log_dir = "") :
        super(DpopAgent, self).__init__(id = int(id), pro = pro, log_dir = log_dir)
        self.parent = parent
        self.children = children
        self.var_host = var_host
        self.sorted_vars = sorted(list(self.pro.vars.keys()))
        self.children_done = {False for i in range(len(self.children))}
        self.backtrack_needed = False    # True if backtrack is needed
        self.done = False       # True if the agent stops renewing the local assignment
        self.terminate = False  # True if received TERMINATE message from the parent
        self.threshold = 0
        self.current_context = {}
        self.lb = {}
        self.ub = {}
        self.t = {}
        self.context = {}
        for d in itertools.product(*[self.pro.vars[var].values for var in self.sorted_vars]) :
            for child in self.children :
                self.lb[(d, child)] = 0
                self.ub[(d, child)] = math.inf
                self.t[(d, child)] = 0
                self.context[(d, child)] = {}
        self.assign = self.update_assign(bound_func = self.get_LB)
        self.backtrack_needed = True
        self.log("init/%s" % self.assign)

    def process(self, msgs) :
        result = {"msgs" : []}
        if len(self.sorted_vars) > 0 :
            if len(msgs) > 0 :
                for msg in msgs :
                    self.log_msg("receive", msg)
                    if isinstance(msg, TerminateMessage) and msg.src == self.parent :
                        self.terminate = True
                        self.current_context = msg.content
                        self.backtrack_needed = True
                    elif isinstance(msg, ThresholdMessage) :
                        self.threshold = msg.content[0]
                        self.maintainThresholdInvariant()
                        self.backtrack_needed = True
                    elif isinstance(msg, DoneMessage) :
                        self.children_done[msg.src] = True
                        if False not in self.children_done :
                            if self.parent is None :
                                result["msgs"].append(SysMessage(src = self.id, content = None))
                            else :
                                result["msgs"].append(DoneMessage(src = self.id, dest = self.parent, content = None))
                for msg in msgs :
                    if isinstance(msg, ValueMessage) and self.terminate == False :
                        self.current_context = {**self.current_context, **msg.content}
                        for d in itertools.product(*[self.pro.vars[var].values for var in self.sorted_vars]) :
                            for child in self.children :
                                if check_dict_compatible(self.context[(d, child)], self.current_context) == False :
                                    self.lb[(d, child)] = 0
                                    self.t[(d, child)] = 0
                                    self.ub[(d, child)] = math.inf
                                    self.context[(d, child)] = {}
                        self.maintainThresholdInvariant()
                        self.backtrack_needed = True
                    if isinstance(msg, CostMessage) :
                        d = tuple([msg.content[1].get(var, self.assign[var]) for var in self.sorted_vars])
                        for var in self.sorted_vars :
                            if var in msg.content[1].keys() :
                                del msg.content[1][var]
                        if self.terminate == False :
                            for var, value in msg.content[1].items() :
                                if self.var_host(var) not in self.children + [self.parent] :
                                    self.current_context[var] = value
                            for dd in itertools.product(*[self.pro.vars[var].values for var in self.sorted_vars]) :
                                for child in self.children :
                                    if check_dict_compatible(self.context[(dd, child)], self.current_context) == False :
                                        self.lb[(dd, child)] = 0
                                        self.t[(dd, child)] = 0
                                        self.ub[(dd, child)] = math.inf
                                        self.context[(dd, child)] = {}
                        if check_dict_compatible(msg.content[1], self.current_context) == True :
                            self.lb[(d, msg.content[0])] = msg.content[2]
                            self.ub[(d, msg.content[0])] = msg.content[3]
                            self.context[(d, msg.content[0])] = msg.content[1]
                            self.maintainChildThresholdInvariant()
                            self.maintainThresholdInvariant()
                        self.backtrack_needed = True
            if self.done == False and self.backtrack_needed == True :
                UB = self.get_UB()
                LB = self.get_LB()
                if self.threshold > UB - 1e-6 :
                    self.assign = self.update_assign(bound_func = self.get_UB)
                elif self.threshold > LB + 1e-6 :
                    self.assign = self.update_assign(bound_func = self.get_LB)
                for id in self.children :
                    result["msgs"].append(ValueMessage(src = self.id, dest = id, content = self.assign))
                result["msgs"] += self.maintainAllocationInvariant()
                if self.threshold > UB - 1e-6 :
                    if self.terminate == True or self.parent is None :
                        self.done = True
                        result["msgs"].append(SysMessage(src = self.id, content = self.assign))
                        if len(self.children) > 0 :
                            for id in self.children :
                                result["msgs"].append(TerminateMessage(src = self.id, dest = id, content = {**self.current_context, **self.assign}))
                        else :
                            if self.parent is None :
                                result["msgs"].append(SysMessage(src = self.id, content = None))
                            else :
                                result["msgs"].append(DoneMessage(src = self.id, dest = self.parent, content = None))
                if self.parent is not None :
                    result["msgs"].append(CostMessage(src = self.id, dest = self.parent, content = (self.id, self.current_context, LB, UB)))
                self.backtrack_needed = False
            for msg in result["msgs"] :
                self.log_msg("send", msg)
        return result

    def get_delta(self, d) :
        delta = 0
        assign = {self.sorted_vars[i] : d[i] for i in range(len(self.sorted_vars))}
        cpa = {**self.current_context, **assign}
        for con in self.pro.cons :
            x = fit_assign_to_con(cpa, con)
            if x is None :
                delta = math.inf
                break
            else :
                delta += con.cost(x)
        return delta

    def get_LB(self, d = None) :
        LB = math.inf
        if d is not None :
            LB = self.get_delta(d = d)
            if LB < math.inf :
                for child in self.children :
                    LB += self.lb[(d, child)]
        else :
            for d in itertools.product(*[self.pro.vars[var].values for var in self.sorted_vars]) :
                LB_d = self.get_delta(d = d)
                for child in self.children :
                    if LB_d < LB :
                        LB_d += self.lb[(d, child)]
                    else :
                        break
                if LB_d < LB :
                    LB = LB_d
        return LB

    def get_UB(self, d = None) :
        UB = math.inf
        if d is not None :
            UB = self.get_delta(d = d)
            if UB < math.inf :
                for child in self.children :
                    UB += self.ub[(d, child)]
        else :
            for d in itertools.product(*[self.pro.vars[var].values for var in self.sorted_vars]) :
                UB_d = self.get_delta(d = d)
                for child in self.children :
                    if UB_d < UB :
                        UB_d += self.ub[(d, child)]
                    else :
                        break
                if UB_d < UB :
                    UB = UB_d
        return UB

    def update_assign(self, bound_func) :
        assign = {}
        d_min = None
        bound_d_min = math.inf
        for d in itertools.product(*[self.pro.vars[var].values for var in self.sorted_vars]) :
            bound = bound_func(d = d)
            if bound < bound_d_min :
                bound_d_min = bound
                d_min = d
        if d_min is not None :
            assign = {self.sorted_vars[i] : d_min[i] for i in range(len(self.sorted_vars))}
        else :
            assign = {var : self.pro.vars[var].first_value() for var in self.sorted_vars}
        return assign

    def maintainThresholdInvariant(self) :
        LB = self.get_LB()
        if self.threshold < LB :
            self.threshold = LB
        UB = self.get_UB()
        if self.threshold > UB :
            self.threshold = UB

    def maintainAllocationInvariant(self) :
        msgs = []
        d = tuple([self.assign[var] for var in self.sorted_vars])
        delta = self.get_delta(d = d)
        while self.threshold > delta + sum([self.t[(d, child)] for child in self.children]) :
            updated = False
            for child in self.children :
                if self.ub[(d, child)] > self.t[(d, child)] :
                    inc = min(self.ub[(d, child)] - self.t[(d, child)], self.threshold - delta - sum([self.t[(d, child)] for child in self.children]))
                    self.t[(d, child)] += inc
                    updated = True
                    break
            if updated == False :
                break
        while self.threshold < delta + sum([self.t[(d, child)] for child in self.children]) :
            updated = False
            for child in self.children :
                if self.lb[(d, child)] < self.t[(d, child)] :
                    dec = min(self.t[(d, child)] - self.lb[(d, child)],  delta + sum([self.t[(d, child)] for child in self.children]) - self.threshold)
                    self.t[(d, child)] -= dec
                    updated = True
                    break
            if updated == False :
                break
        for child in self.children :
            msgs.append(ThresholdMessage(src = self.id, dest = child, content = (self.t[(d, child)], self.current_context)))
        return msgs

    def maintainChildThresholdInvariant(self) :
        for d in itertools.product(*[self.pro.vars[var].values for var in self.sorted_vars]) :
            for child in self.children :
                if self.t[(d, child)] < self.lb[(d, child)] :
                    self.t[(d, child)] = self.lb[(d, child)]
            for child in self.children :
                if self.t[(d, child)] > self.ub[(d, child)] :
                    self.t[(d, child)] = self.ub[(d, child)]
