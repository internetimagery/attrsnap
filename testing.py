# Create a few test situations.
from __future__ import print_function
import maya.cmds as cmds
import random


def test_match():
    """ Test ideal conditions. We can reach the end result, and it's a linear path to get there. """
    s1, _ = cmds.polySphere()
    s2, _ = cmds.polySphere()
    cmds.xform(s1, t=(1,1,0))
    cmds.xform(s2, t=(0,-1,-1))
    return (s1, s2), ((o, at) for o in (s1, s2) for at in ["tx", "ty", "tz"])

def position(min_, max_):
    """ Return random position """
    return [random.randrange(min_, max_) for a in range(3)]

def sphere():
    """ Create a sphere and place it somewhere """
    obj, _ = cmds.polySphere()
    cmds.xform(obj, t=position(-5, 5))
    return obj

def scene_setup():
    """ Set up a test scene! """
    cmds.file(new=True, force=True)
    s1 = sphere()
    s2 = sphere()
    s3 = sphere()
    cmds.parent(s3, s2)
    return s1, s2, s3

def main():
    """ Run tests! """
    scene_setup()
