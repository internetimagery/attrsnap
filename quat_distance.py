import maya.cmds as cmds

import element
import math

def aprox_angle(q1, q2):
    dot = sum(a*b for a,b in zip(q1,q2))
    return 10 * (1 - dot**2)

def angle(q1, q2):
    dot = sum(a*b for a,b in zip(q1,q2))
    angle = 2 * dot**2 - 1
    return 2 * math.acos(angle)

def linear(q1, q2):
    diff = (a-b for a,b in zip(q1, q2))
    mag2 = sum(a*a for a in diff)
    return 10 * (mag2 and (mag2 ** -0.5) * mag2)

def main():
    cmds.file(new=True, force=True)

    p1, _ = cmds.polyCube()
    p2, _ = cmds.polyCube()
    m1 = element.Marker(p1)
    m2 = element.Marker(p2)

    points = {}
    root = m1.get_rotation()
    for x in range(-360, 360, 30):
        for y in range(-360, 360, 30):
            for z in range(-360, 360, 30):
                cmds.xform(p2, ro=(x,y,z))
                quat = m2.get_rotation()
                dist = angle(root, quat)
                points[x,y,z] = dist

    locs = {(x,y): cmds.spaceLocator()[0] for x in range(-360, 360, 30) for y in range(-360, 360, 30)}
    for (x, y, z), dist in points.items():
        cmds.setKeyframe(locs[x,y] + ".tx", t=z, v=x*0.1)
        cmds.setKeyframe(locs[x,y] + ".ty", t=z, v=dist)
        cmds.setKeyframe(locs[x,y] + ".tz", t=z, v=y*0.1)
    cmds.group([locs[a] for a in locs])
    cmds.playbackOptions(min=-360, max=360)
