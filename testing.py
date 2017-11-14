# Create a few test situations.
from __future__ import print_function
import maya.cmds as cmds
import time
import groups

try:
    import cProfile as profile
except ImportError:
    import profile

import match_walk
import match_prediction

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

def equals(obj, xyz, rotation=False):
    """ Check position is right within tolerance """
    tolerance = 0.05
    pos = cmds.xform(obj, q=True, ro=True, ws=True) if rotation else cmds.xform(obj, q=True, t=True, ws=True)
    for XYZ, ax in zip(xyz, pos):
        if abs(ax - XYZ) > tolerance:
            return False
    return True

def update(dist):
    """ Update callback """
    if DEBUG:
        cmds.refresh()

matches = {
    "walk": match_walk.match,
    "prediction": match_prediction
    }

tests = {}

# Ideal matching situation. Linear movement and can 100% match.
tests["match"] = (
    lambda s1, s2, s3: groups.Group(groups.POSITION, (s1, s2), (s1, "tx"), (s1, "ty"), (s1, "tz")),
    lambda s1, s2, s3: equals(s1, (-2, 2, 0))) # Object should match

# Match is possible. But certain combinations can lead to a cat/mouse chase.
tests["chase"] = (
    lambda s1, s2, s3: groups.Group(groups.POSITION, (s1, s2), (s1, "tx"), (s1, "ty"), (s1, "tz"), (s2, "tx"), (s2, "ty"), (s2, "tz")),
    lambda s1, s2, s3: equals(s1, cmds.xform(s2, q=True, t=True))) # Objects should match somewhere in space.

# Parallel movement. Distance will never close.
tests["parallel"] = (
    lambda s1, s2, s3: [cmds.parentConstraint(s1, s2, mo=True), groups.Group(groups.POSITION, (s1, s2), (s1, "tx"))][1],
    lambda s1, s2, s3: equals(s1, (2,0,2))) # No result works. Should stay where we are.

# Cannot reach target, but can reach a point of minimal distance.
tests["lookat"] = (
    lambda s1, s2, s3: groups.Group(groups.POSITION, (s1, s3), (s2, "rx"), (s2, "ry")),
    lambda s1, s2, s3: equals(s3, (0, 1, 1)))

# Many possibilities exist.
tests["possibilities"] = (
    lambda s1, s2, s3: groups.Group(groups.POSITION, (s1, s3), (s1, "tx"), (s1, "ty"), (s1, "tz"), (s2, "rx"), (s2, "ry"), (s2, "rz")),
    lambda s1, s2, s3: equals(s3, cmds.xform(s1, q=True, t=True)))

# No movement at all.
tests["zero"] = (
    lambda s1, s2, s3: groups.Group(groups.POSITION, (s1, s2), (s1, "rx"), (s1, "ry"), (s1, "rz")),
    lambda s1, s2, s3: equals(s1, (2,0,2)))

# Match rotation
tests["match rotation"] = (
    lambda s1, s2, s3: [cmds.xform(s2, ro=(10,10,-10)), groups.Group(groups.ROTATION, (s1, s2), (s1, "rx"), (s1, "ry"), (s1, "rz"))][1],
    lambda s1, s2, s3: equals(s1, (10, 10, -10), True))

# Unable to match rotation, get closest
tests["lookat rotation"] = (
    lambda s1, s2, s3: [cmds.xform(s2, ro=(10,10,-10)), groups.Group(groups.ROTATION, (s1, s2), (s1, "rx"))][1],
    lambda s1, s2, s3: equals(s1, (10, 0, 0), True))


def prof():
    """ Profile match functionality """
    cmds.refresh(su=True)
    try:
        for name, func in matches.items():
            scene = scene_setup()
            group = tests["possibilities"][0](*scene)
            print("STARTING PROFILE FOR \"{}\"".format(name))
            profile.runctx("func(group, update)", globals(), locals())
            print("-"*20)
    finally:
        cmds.refresh(su=False)

def main():
    """ Run tests! """
    failed = {}
    for match_name, match in matches.items():
        for name, (test, result) in tests.items():
            times = []
            print("Running match \"{}\" on \"{}\"...".format(match_name, name), end="")
            try:
                for i in range(10): # Times to run test!
                    scene = scene_setup()
                    match_group = test(*scene)
                    start = time.time()
                    match(match_group, update)
                    times.append(time.time() - start)
                    assert result(*scene)
                print("OK! - {}".format(sum(times)))
            except AssertionError:
                print("Failed!")
                failed[match_name, name] = {
                    scene[0]: cmds.xform(scene[0], q=True, matrix=True, ws=True),
                    scene[1]: cmds.xform(scene[1], q=True, matrix=True, ws=True),
                    scene[2]: cmds.xform(scene[2], q=True, matrix=True, ws=True)}
            if DEBUG:
                cmds.refresh()
                time.sleep(2)

    # Failed tests recreate for inspection
    cmds.file(new=True, force=True)
    for (match_name, name), scene in failed.items():
        grp = cmds.group(name="{}_{}_State".format(match_name, name), em=True)
        for obj, matrix in scene.items():
            o, _ = cmds.polySphere()
            cmds.parent(o, grp)
            cmds.xform(o, ws=True, matrix=matrix)
