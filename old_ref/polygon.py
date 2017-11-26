# Polgon descent methodology
# https://en.wikipedia.org/wiki/Nelder%E2%80%93Mead_method

import maya.cmds as cmds
import random
import math

def vAdd(v1, v2):
    return tuple(v1[i] + v2[i] for i in range(len(v1)))

def vSub(v1, v2):
    return tuple(v1[i] - v2[i] for i in range(len(v1)))

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
    return math.sqrt(sum((b-a)**2 for a, b in zip(p1, p2)))

def rand():
    return tuple(random.randrange(-10,10) for _ in range(3))

def centroid(*points):
    result = [0]*len(points[0])
    for i in range(len(points)):
        for j in range(len(result)):
            result[j] += points[i][j]
    inv = 1.0 / (len(points) + 1)
    return [a*inv for a in result]

def test():
    cmds.file(new=True, force=True)

    goal = rand()
    pol, _ = cmds.polySphere()
    cmds.xform(pol, t=goal)

    simplex = {}
    dimensions = len(goal)
    for _ in range(dimensions+1):
        p = rand()
        simplex[p] = distance(p, goal)

    for i in range(1000):
        # Step 1: Order
        points = sorted(simplex, key=lambda x: simplex[x])

        # Step 2: Centroid
        Xo = centroid(*points[:-1])
        if not i % 10:
            cmds.spaceLocator(p=Xo)

        # Step 3: Reflection
        A = 1 # > 0
        Xr = vAdd(vMul(vSub(Xo, points[-1]), A), Xo)
        Dr = distance(Xr, goal)
        if simplex[points[0]] <= Dr and simplex[points[-2]] > Dr:
            del simplex[points[-1]]
            simplex[Xr] = Dr
            # print "Reflection"
            continue

        # Step 4: Expansion
        if Dr < simplex[points[0]]:
            Y = 2 # > 1
            Xe = vAdd(vMul(vSub(Xr, Xo), Y), Xo)
            De = distance(Xe, goal)
            del simplex[points[-1]]
            if De < Dr:
                simplex[Xe] = De
            else:
                simplex[Xr] = Dr
            # print "Expansion"
            continue

        # Step 5: Contraction
        P = 0.5 # 0 < p < 0.5
        Xc = vAdd(vMul(vSub(points[-1], Xo), P), Xo)
        Dc = distance(Xc, goal)
        if Dc < simplex[points[-1]]:
            del simplex[points[-1]]
            simplex[Xc] = Dc
            # print "Contraction"
            continue

        # Step 6: Shrink
        O = 0.5
        for p in points[1:]:
            del simplex[p]
            p = vAdd(vMul(vSub(p, points[0]), O), points[0])
            simplex[p] = distance(p, goal)

        # print "Shrink"
