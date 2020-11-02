
import sys, os, time
import doctest

from disto.agent import Agent

def test_agent() :
    '''
    >>> test_agent()
    Agent: <<Disto.Agent id = 0; pro = False>>
    agent.process(msgs = [None]) -> msgs: {'msgs': []}
    '''
    agent = Agent(id = "0", pro = None)
    print(f"Agent: {agent.info()}")
    msgs = agent.process(msgs = [None])
    print(f"agent.process(msgs = [None]) -> msgs: {msgs}")

if __name__ == '__main__' :
    result = doctest.testmod()
    print("-" * 50)
    print("[Agent Test] attempted/failed tests: %d/%d" % (result.attempted, result.failed))
