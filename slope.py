# Slope!
from __future__ import division
import maya.cmds as cmds
import random
import math
import groups

def vAdd(v1, v2):
    return tuple(v1[i] + v2[i] for i in range(len(v1)))

def vSub(v1, v2):
    return tuple(v1[i] - v2[i] for i in range(len(v1)))

def vDiv(v1, v2):
    return tuple(v1[i] / v2[i] for i in range(len(v1)))


def vMul(v1, s1):
    return tuple(v1[i] * s1 for i in range(len(v1)))

def inv(v1):
    return tuple(a*-1 for a in v1)

def cross(v1, v2):
    return (
        v1[1] * v2[2] - v2[1] * v1[2],
        v1[2] * v2[0] - v2[2] * v1[0],
        v1[0] * v2[1] - v2[0] * v1[1])

def norm(v1):
    mag = math.sqrt(sum(a*a for a in v1))
    return tuple(mag and a/mag for a in v1)

def distance(p1, p2):
    diff = (p1[i]-p2[i] for i in range(len(p1)))
    mag2 = sum(d*d for d in diff)
    return mag2 or (mag2 ** -0.5) * mag2

def rand():
    return tuple(random.randrange(-10,10) for _ in range(3))

def gradient(grp, step=0.1):
    curr_val = grp.get_values()
    curr_dist = grp.get_distance()
    result = []
    for i in range(len(grp)):
        new_val = [v+step if i == j else v for j, v in enumerate(curr_val)]
        grp.set_values(new_val)
        new_dist = grp.get_distance()
        result.append((new_dist - curr_dist) / step)
    return result

# dF(x) / dx = (F(x+h) - F(x)) / h
# dF(x) / dx = (F(x+h) - F(x-h)) / 2h


# https://cs231n.github.io/neural-networks-3/#gradcheck
def test():
    cmds.file(new=True, force=True)

    m1, _ = cmds.polySphere()
    m2 = cmds.group(em=True)
    m3 = cmds.group(m2)

    grp = groups.Group(
        markers=(m1, m2),
        attributes=[(m2, "translateX"), (m2, "translateZ")]
    )

    cmds.xform(m1, t=rand())
    cmds.xform(m2, t=rand())
    cmds.setAttr(m2 + ".ty", 0)
    cmds.setAttr(m3 + ".scaleX", 3)
    cmds.setAttr(m3 + ".scaleZ", 6)
    curve = cmds.curve(p=cmds.xform(m2, q=True, ws=True, t=True))

    step = 0.5
    velocity = [0]*len(grp)
    friction = 0.7
    last_vals = grp.get_values()
    last_dist = grp.get_distance()
    while step > 0.001:
        dist = grp.get_distance()
        if dist >= last_dist:
            step *= 0.5
            velocity = vMul(velocity, 0.5)
        last_dist = dist

        ahead = vAdd(last_vals, vMul(velocity, friction))
        grp.set_values(ahead)
        aim = grp.get_gradient()

        # print length(aim)

        velocity = vMul(vSub(velocity, vMul(aim, step)), friction)

        new_val = vAdd(velocity, last_vals)
        last_vals = new_val

        grp.set_values(new_val)
        grp.keyframe(new_val)
        cmds.curve(curve, a=True, p=cmds.xform(m2, ws=True, q=True, t=True))
