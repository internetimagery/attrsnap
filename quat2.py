# Find failed rotations for examination
from __future__ import division
import maya.cmds as cmds
import element_maya as em
reload(em)
import groups
reload(groups)
reload(groups.element)
import random
import match
reload(match)



def test():
    cmds.file(new=True, force=True)

    p1, _ = cmds.polyCube()
    p2, _ = cmds.polyCube()

    template = groups.Template(
        match_type=groups.ROTATION,
        markers=[p1, p2],
        attributes=[(p2, a) for a in ["rx","ry","rz"]]
        )
    group = groups.Group(template)

    failed = []
    total_times = 300
    for _ in range(total_times):
        # Random rotation
        try:
            cmds.xform(p1, ro=[random.randrange(-180, 180) for _ in range(3)])
            for dist, values in match.search(group):
                pass
            assert dist < -20
        except AssertionError:
            pos = cmds.xform(p1, q=True, ro=True)
            print "Failed:", dist, pos
            failed.append(pos)
    for i, f in enumerate(failed):
        cmds.currentTime(i)
        for v, at in zip(f, [".rx",".ry",".rz"]):
            cmds.setKeyframe(p1 + at, v=v)

    print "failed {}% times!".format(len(failed)/total_times)
    print "{} of {}".format(len(failed), total_times)
