
import sys, os, time
import doctest

from disto.problem import Problem
from disto.agent import Agent

def test_agent() :
    '''
    >>> test_agent()
    Agent: <<Disto.Agent id = 0; pro = Problem>>
    agent.process(msgs = [None]) -> result: {'msgs': []}
    '''
    agent = Agent(id = "0", pro = Problem(vars = {"0" : None}, cons = []))
    print(f"Agent: {agent.info()}")
    result = agent.process(msgs = [None])
    print(f"agent.process(msgs = [None]) -> result: {result}")

if __name__ == '__main__' :
    result = doctest.testmod()
    print("-" * 50)
    print("[Agent Test] attempted/failed tests: %d/%d" % (result.attempted, result.failed))
