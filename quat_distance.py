import maya.cmds as cmds

import element
import math

def aprox_angle(q1, q2):
    dot = sum(a*b for a,b in zip(q1,q2))
    return 1 - dot**2

def angle(q1, q2):
    dot = sum(a*b for a,b in zip(q1,q2))
    angle = 2 * dot**2 - 1
    return math.acos(angle)

def linear(q1, q2):
    diff = (a-b for a,b in zip(q1, q2))
    mag2 = sum(a*a for a in diff)
    return mag2 and (mag2 ** -0.5) * mag2

def main():
    cmds.file(new=True, force=True)

    p1, _ = cmds.polyCube()
    p2, _ = cmds.polyCube()
    m1 = element.Marker(p1)
    m2 = element.Marker(p2)

    points = {}
    root = m1.get_rotation()
    for x in range(-180, 180, 20):
        for y in range(-180, 180, 20):
            for z in range(-180, 180, 20):
                cmds.xform(p2, ro=(x,y,z))
                quat = m2.get_rotation()
                dist = aprox_angle(root, quat) + linear(root, quat)
                points[x,y,z] = dist

    locs = []
    for (x, y, z), dist in points.items():
        locs.append(cmds.spaceLocator(p=(x*0.1,dist*5,z*0.1))[0])
    cmds.group(locs)
