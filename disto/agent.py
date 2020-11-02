
import numpy

class Agent(object) :
    def __init__(self, id, pro) :
        self.id = id
        self.pro = pro

    def info(self) :
        return f"<<Disto.{type(self).__name__} id = {self.id}; pro_size = ({len(self.pro.vars)}, {len(self.pro.cons)})>>"

    def process(self, msgs) :
        msgs = []
        return {"msgs" : msgs}

class SyncBTAgent(Agent) :
    def __init__(self, id, pro, num_agents) :
        super(SyncBTAgent, self).__init__(id = int(id), pro = pro)
        self.num_agents = num_agents
        self.sorted_vars = sorted(list(self.pro.vars.keys()))
        self.assign = {var : None for var in self.sorted_vars}
        self.status = "created"

    def next_assign(self) :
        for var, domain in self.pro.vars.items() :
            self.assign[var] = domain.first_value()

    def collect_utility(self) :
        total = 0
        return total

    def fix_assign(self, var = None) :
        result = False
        # if var is None and len(self.sorted_vars) > 0 :
        #     var = self.sorted_vars[0]
        # if var is not None and None not in self.assign.values() :
        return result

    def process(self, msgs) :
        msgs = []
        # if None in self.assign.values() :
        return {"msgs" : msgs}

class AsynBTAgent(Agent) :
    def __init__(self, id, pro, last_id) :
        super(AsynBTAgent, self).__init__(id = int(id), pro = pro)
        self.last_id = last_id
        self.sorted_vars = sorted(list(self.pro.vars.keys()))
        self.assign = {var : None for var in self.sorted_vars}
        self.status = "created"

    def next_assign(self) :
        for var, domain in self.pro.vars.items() :
            self.assign[var] = domain.first_value()

    def collect_utility(self) :
        total = 0
        return total

    def fix_assign(self, var = None) :
        result = False
        # if var is None and len(self.sorted_vars) > 0 :
        #     var = self.sorted_vars[0]
        # if var is not None and None not in self.assign.values() :
        return result

    def process(self, msgs) :
        msgs = []
        # if None in self.assign.values() :
        return {"msgs" : msgs}
