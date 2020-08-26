
import sys, os, time
import doctest

from disto.agent import Agent

def test_agent() :
    '''
    >>> test_agent()
    Agent: <<Disto.Agent id = 0; data = NoneType; prob = NoneType; solv = NoneType>>
    '''
    agent = Agent(id = "0", data = None)
    print(f"Agent: {agent.info()}")

if __name__ == '__main__' :
    result = doctest.testmod()
    print("-" * 50)
    print("[Agent Test] attempted/failed tests: %d/%d" % (result.attempted, result.failed))
