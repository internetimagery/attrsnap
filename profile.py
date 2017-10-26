# Testing different scan speeds.
from __future__ import print_function
import maya.cmds as cmds
import random

try:
    import cProfile as profile
except ImportError:
    import profile

class Tester(object):
    def __init__(s, val):
        s.val = val
    def test1(s):
        val = s.val
        val += 1
        val = val * 2

    def test2(s):
        s.val += 1
        s.val = s.val * 2


def test_lookup():
    t = Tester(0)
    t.test1()
    t.test2()

def main():
    # Create a test scene
    # cmds.file(new=True, force=True)
    # s1, _ = cmds.polySphere()
    # s2, _ = cmds.polySphere()
    # cmds.xform(s1, t=[random.randrange(-3, 3) for _ in range(3)])
    # cmds.xform(s2, t=[random.randrange(-3, 3) for _ in range(3)])

    profile.runctx("test_lookup()", globals(), locals())
