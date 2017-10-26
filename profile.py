# Testing different scan speeds.
from __future__ import print_function

import maya.cmds as cmds
try:
    import cProfile as profile
except ImportError:
    import profile


def test():
    return "something"


def main():
    profile.runctx("test()", globals(), locals())
