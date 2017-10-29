# Create a few test situations.
from __future__ import print_function
import maya.cmds as cmds
import random

def position(min_, max_):
    """ Return random position """
    return [random.randrange(min_, max_) for a in range(3)]

def sphere():
    """ Create a sphere and place it somewhere """
    obj, _ = cmds.polySphere()
    cmds.xform(obj, t=position(-5, 5), ro=position(-30, 30))
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
