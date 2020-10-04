
import sys, os, time
import doctest

from disto.monitor import Message

def test_message() :
    '''
    >>> test_message()
    msg.src: 0
    msg.dest: 1
    msg.content: Test Message
    '''
    msg = Message(src = "0", dest = "1", content = "Test Message")
    print(f"msg.src: {msg.src}")
    print(f"msg.dest: {msg.dest}")
    print(f"msg.content: {msg.content}")

if __name__ == '__main__' :
    result = doctest.testmod()
    print("-" * 50)
    print("[Message Test] attempted/failed tests: %d/%d" % (result.attempted, result.failed))
