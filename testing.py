# Create a few test situations.
from __future__ import print_function
import maya.cmds as cmds
import time
import groups

import match_walk

DEBUG = False

def sphere(*pos):
    """ Create a sphere and place it somewhere """
    obj, _ = cmds.polySphere()
    cmds.xform(obj, t=pos)
    return obj

def scene_setup():
    """ Set up a test scene! """
    cmds.file(new=True, force=True)
    s1 = sphere(2, 0, 2)
    s2 = sphere(-2, 2, 0)
    s3 = sphere(0, 3, 1)
    cmds.parent(s3, s2)
    return s1, s2, s3

def equals(obj, xyz):
    """ Check position is right within tolerance """
    tolerance = 0.05
    for XYZ, ax in zip(xyz, cmds.xform(obj, q=True, t=True, ws=True)):
        if abs(ax - XYZ) > tolerance:
            return False
    return True

def update(dist):
    """ Update callback """
    if DEBUG:
        cmds.refresh()

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

matches = {
    "walk": match_walk.match
    }

tests = {}

# Ideal matching situation. Linear movement and can 100% match.
tests["match"] = (
    lambda s1, s2, s3: groups.Group("pos", (s1, s2), (s1, "tx"), (s1, "ty"), (s1, "tz")),
    lambda s1, s2, s3: equals(s1, (-2, 2, 0))) # Object should match

# Match is possible. But certain combinations can lead to a cat/mouse chase.
tests["chase"] = (
    lambda s1, s2, s3: groups.Group("pos", (s1, s2), (s1, "tx"), (s1, "ty"), (s1, "tz"), (s2, "tx"), (s2, "ty"), (s2, "tz")),
    lambda s1, s2, s3: equals(s1, cmds.xform(s2, q=True, t=True))) # Objects should match somewhere in space.

# Parallel movement. Distance will never close.
tests["parallel"] = (
    lambda s1, s2, s3: groups.Group("pos", (s1, s2), (s1, "tx"), (s2, "tx")),
    lambda s1, s2, s3: equals(s1, (2,0,2))) # No result works. Should stay where we are.

# Cannot reach target, but can reach a point of minimal distance.
tests["lookat"] = (
    lambda s1, s2, s3: groups.Group("pos", (s1, s3), (s2, "rx"), (s2, "ry")),
    lambda s1, s2, s3: equals(s3, (0, 1, 1)))

# Many possibilities exist.
tests["possibilities"] = (
    lambda s1, s2, s3: groups.Group("pos", (s1, s3), (s1, "tx"), (s1, "ty"), (s1, "tz"), (s2, "rx"), (s2, "ry"), (s2, "rz")),
    lambda s1, s2, s3: equals(s3, cmds.xform(s1, q=True, t=True)))

# No movement at all.
tests["zero"] = (
    lambda s1, s2, s3: groups.Group("pos", (s1, s2), (s1, "rx"), (s1, "ry"), (s1, "rz")),
    lambda s1, s2, s3: equals(s1, (2,0,2)))


def main():
    """ Run tests! """
    for match_name, match in matches.items():
        for name, (test, result) in tests.items():
            scene = scene_setup()
            match_group = test(*scene)
            print("Running match \"{}\" on \"{}\"...".format(match_name, name), end="")
            if DEBUG:
                cmds.refresh()
                time.sleep(1)
            start = time.time()
            match(match_group, update)
            try:
                assert result(*scene)
                print("OK! - {}".format(time.time() - start))
            except AssertionError:
                print("Failed!")
            if DEBUG:
                cmds.refresh()
                time.sleep(2)
