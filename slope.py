# Slope!
from __future__ import division
import maya.cmds as cmds
import random
import math

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

def gradient(p1, p2, step=0.1):
    return [(distance([p1[j] + step if j == i else p1[j] for j, _ in enumerate(p1)], p2) - distance(p1, p2)) / step for i, _ in enumerate(p1)]

# dF(x) / dx = (F(x+h) - F(x)) / h
# dF(x) / dx = (F(x+h) - F(x-h)) / 2h


def test():
    cmds.file(new=True, force=True)

    goal = rand()
    poly, _ = cmds.polySphere()
    cmds.xform(poly, t=goal)

    start = rand()
    cmds.spaceLocator(p=start)
    step = 1


    for _ in range(80):
        aim = norm(gradient(start, goal, 0.01))
        start = vAdd(vMul(aim, -step), start)
        cmds.spaceLocator(p=start)
