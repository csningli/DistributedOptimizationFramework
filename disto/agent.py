
import time, numpy, abc

class DataAccess(object) :
    @abc.abstractmethod
    def topics(self) :
        pass

    @abc.abstractmethod
    def publish(self, topic) :
        pass

    @abc.abstractmethod
    def subscribe(self, topic) :
        pass

    @abc.abstractmethod
    def start(self) :
        pass

    @abc.abstractmethod
    def stop(self) :
        pass

    @abc.abstractmethod
    def get(self, topic, key) :
        pass

    @abc.abstractmethod
    def update(self, topic, key, value) :
        pass

class ProcessDataAccess(object) :
    def start(self) :
        pass

    def stop(self) :
        pass

class Agent(object) :
    def __init__(self, id, data, prob = None, solv = None) :
        self.id = id
        self.data = data
        self.prob = prob
        self.solv = solv
        self.asgn = None
        self.running = False
        self.round = -1

    def info(self) :
        return f"<<Disto.{type(self).__name__} id = {self.id}; data = {type(self.data).__name__}; prob = {type(self.prob).__name__}; solv = {type(self.solv).__name__}>>"

    def run(self, rounds = 1) :
        self.data.start()
        self.running = True
        self.round = 0
        while self.running == True and self.round < rounds :
            self.act()
            self.round += 1
            time.sleep(0.1)
        self.data.stop()

    def act(self) :
        print("[Agent %d] round %d." % (self.id, self.round))
