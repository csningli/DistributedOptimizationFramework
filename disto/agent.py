
import numpy

class Agent(object) :
    def __init__(self, id, pro) :
        self.id = id
        self.pro = pro

    def info(self) :
        return f"<<Disto.{type(self).__name__} id = {self.id}; pro = {self.pro.name if self.pro is not None else None}>>"

    def process(self, msgs) :
        msgs = []
        return {"msgs" : msgs}

class SyncBTAgent(Agent) :
    def __init__(self, id, pro) :
        super(SyncBTAgent, self).__init__(id = id, pro = pro)
        self.assign = {}
        if self.pro is not None :
            for var, domain in self.pro.vars.items() :
                self.assign[var] = domain.first_value()

    def process(self, msgs) :
        msgs = []
        return {"msgs" : msgs}
