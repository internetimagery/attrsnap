# Create a few test situations.
from __future__ import print_function
import maya.cmds as cmds
import random
import groups
from match_path import match

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

#
# You could use the progressWindow() to cancel loops with ESC, might involve some more lines but does not slow down loops while accessing and checking files.
# import maya.cmds as cmds
#
# cmds.progressWindow(isInterruptable=1)
# while 1 :
# print "kill me!"
# if cmds.progressWindow(query=1, isCancelled=1) :
# break
#
# cmds.progressWindow(endProgress=1)
#
# And if you dont want to see the tiny window you could instead use mayas own progress bar inside the main windows help line with progressBar()

def test_match(s1, s2, s3):
    """ Ideal matching situation. Linear movement and can 100% match."""
    return groups.Group(
        "pos",
        (s1, s2),
        ((s1, "tx"), (s1, "ty"), (s1, "tz")))

def test_chase(s1, s2, s3):
    """ Match is possible. But certain combinations can lead to a cat/mouse chase. """
    return groups.Group(
        "pos",
        (s1, s2),
        ((s1, "tx"), (s1, "ty"), (s1, "tz"), (s2, "tx"), (s2, "ty"), (s2, "tz")))

def test_parallel(s1, s2, s3):
    """ Parallel movement. Distance will never close. """
    return groups.Group(
        "pos",
        (s1, s2),
        ((s1, "tx"), (s2, "tx")))

def test_lookat(s1, s2, s3):
    """ Cannot reach target, but can reach a point of minimal distance. """
    return groups.Group(
        "pos",
        (s1, s3),
        ((s2, "rx"), (s2, "ry")))

def test_possibilities(s1, s2, s3):
    """ Many possibilities exist. """
    return groups.Group(
        "pos",
        (s1, s3),
        ((s1, "tx"), (s1, "ty"), (s1, "tz"), (s2, "rx"), (s2, "ry"), (s2, "rz")))


def main():
    """ Run tests! """
    match_group = test_match(*scene_setup())
    match(match_group)
