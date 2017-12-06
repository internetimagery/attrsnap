import maya.cmds as cmds

import element
import math

def custom(q1 ,q2):
    diff = (a-b for a,b in zip(q1, q2))
    # diff = (q1[i]-q2[i] for i in range(3))
    mag2 = sum(a*a for a in diff)
    return 5 * mag2

def aprox_angle(q1, q2):
    dot = sum(a*b for a,b in zip(q1,q2))
    res = 1 - dot * dot
    return 10 * res and math.log(res, 1.1)

def angle(q1, q2):
    dot = sum(a*b for a,b in zip(q1,q2))
    angle = 2 * dot**2 - 1
    return 2 * math.acos(angle)

def linear(q1, q2):
    diff = (a-b for a,b in zip(q1, q2))
    mag2 = sum(a*a for a in diff)
    res = (mag2 and (mag2 ** -0.5) * mag2)
    return 10 * (res and math.log(res))

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
                dist = linear(root, quat)
                points[x,y,z] = dist

    locs = {(x,z): cmds.spaceLocator()[0] for x in range(-360, 360, 30) for z in range(-360, 360, 30)}
    for (x, y, z), dist in points.items():
        cmds.setKeyframe(locs[x,z] + ".tx", t=y, v=x*0.1)
        cmds.setKeyframe(locs[x,z] + ".ty", t=y, v=dist)
        cmds.setKeyframe(locs[x,z] + ".tz", t=y, v=z*0.1)
    cmds.group([locs[a] for a in locs])
    cmds.playbackOptions(min=-360, max=360)
