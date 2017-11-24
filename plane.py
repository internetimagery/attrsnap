# testing plane stuff

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

def position(p1, p2, p3):
    p1p2 = vSub(p2, p1)
    p1p3 = vSub(p3, p1)
    crs = cross(p1p2, p1p3)
    if crs[0] < 0:
        crs = inv(crs)
    cmds.curve(p=[p1, vAdd(p1, norm(crs))])
    return crs

def dyn_dist(pos, obj, attr):
    grp = cmds.group(em=True)
    cmds.xform(grp, t=pos)
    dist = cmds.shadingNode("distanceBetween", asUtility=True)
    cmds.connectAttr(grp + ".translate", dist + ".point1")
    cmds.connectAttr(obj + ".translate", dist + ".point2")
    cmds.connectAttr(dist + ".distance", attr)

def dyn_cross(p1, p2, p3, name):
    pma1 = cmds.shadingNode("plusMinusAverage", asUtility=True)
    pma2 = cmds.shadingNode("plusMinusAverage", asUtility=True)

    cmds.setAttr(pma1 + ".operation", 2)
    cmds.connectAttr(p2 + ".translate", pma1 + ".input3D[0]", force=True)
    cmds.connectAttr(p1 + ".translate", pma1 + ".input3D[1]", force=True)

    cmds.setAttr(pma2 + ".operation", 2)
    cmds.connectAttr(p3 + ".translate", pma2 + ".input3D[0]", force=True)
    cmds.connectAttr(p1 + ".translate", pma2 + ".input3D[1]", force=True)

    components = []
    for ax1, ax2 in ["yz", "zx", "xy"]:
        m1 = cmds.shadingNode("multiplyDivide", asUtility=True)
        pma3 = cmds.shadingNode("plusMinusAverage", asUtility=True)
        cmds.setAttr(pma3 + ".operation", 2)
        cmds.connectAttr(pma1 + ".output3D%s" % ax1, m1 + ".input1X" , force=True)
        cmds.connectAttr(pma2 + ".output3D%s" % ax2, m1 + ".input2X" , force=True)

        cmds.connectAttr(pma1 + ".output3D%s" % ax2, m1 + ".input1Y" , force=True)
        cmds.connectAttr(pma2 + ".output3D%s" % ax1, m1 + ".input2Y" , force=True)

        cmds.connectAttr(m1 + ".outputX", pma3 + ".input1D[0]")
        cmds.connectAttr(m1 + ".outputY", pma3 + ".input1D[1]")
        components.append(pma3)

    quat1 = cmds.shadingNode("quatNormalize", asUtility=True)
    for i, ax in enumerate("XYZ"):
        cmds.connectAttr(components[i] + ".output1D", quat1 + ".inputQuat.inputQuat%s" % ax, force=True)

    length = 5
    m2 = cmds.shadingNode("multiplyDivide", asUtility=True)
    for ax in "XYZ":
        cmds.setAttr(m2 + ".input1%s" % ax, length)
        cmds.connectAttr(quat1 + ".outputQuat%s" % ax, m2 + ".input2%s" % ax, force=True)

    pma4 = cmds.shadingNode("plusMinusAverage", asUtility=True)
    cmds.connectAttr(m2 + ".output", pma4 + ".input3D[0]", force=True)
    cmds.connectAttr(p1 + ".translate", pma4 + ".input3D[1]", force=True)

    curve1 = cmds.curve(p=[(0,0,0), (0,0,0)])
    result = cmds.spaceLocator()[0]

    cmds.connectAttr(p1 + ".translate", curve1 + ".controlPoints[0]", force=True)
    cmds.connectAttr(pma4 + ".output3D", curve1 + ".controlPoints[1]", force=True)
    cmds.connectAttr(pma4 + ".output3D", result + ".translate", force=True)
    return result
# Take three nearest points (heap should keep them sorted if axis is X)
# Check not in straight line... grab different point if so
# get cross product of the points
# check if cross product goes below or above the plane
# remove axis, and normalize resulting vector
# multiply unit vector by step size
# take result, and add that to point list.
# if axis (x?) of cross is almost 0, we are at our destination!

import maya.cmds as cmds
import random
import math
import heapq

def map():
    cmds.file(new=True, force=True)

    rand = lambda: random.randrange(-10, 11)

    goal = [random.randrange(-5, 5) for _ in range(3)]
    poly, _ = cmds.polySphere()
    cmds.xform(poly, t=goal)

    points = []
    curvesX = []
    for i, x in enumerate(range(-10, 11)):
        for j, z in enumerate(range(-10, 11)):
            y = distance((x, 0, z), goal)
            point = (x,y,z)
            points.append(point)
            if i:
                cmds.curve(curvesX[j], a=True, p=point)
            else:
                curvesX.append(cmds.curve(p=point))

            dyn_dist((x,0,z), poly, curvesX[j] + ".controlPoints[%s].yValue" % i)
    cmds.loft(curvesX)
    cmds.hide(curvesX)

    # Pick random point to start search
    def position(x, y, name):
        p1 = cmds.spaceLocator(n=name)[0]
        cmds.xform(p1, t=(x, 0, y))
        dyn_dist((x,0,y), poly, p1 + ".ty")
        return p1

    p1 = position(rand(), rand(), "pos1")
    p2 = position(rand(), rand(), "pos2")
    p3 = position(rand(), rand(), "pos3")
    crs = dyn_cross(p1, p2, p3, "cross1")


def test():

    cmds.file(new=True, force=True)

    def get(x):
        return [distance([0, x[1], x[2]], goal), x[1], x[2]]

    # Create a goal
    goal = [random.randrange(-10, 10) for _ in range(3)]

    # Create our starting points
    root = get([random.randrange(-10, 10) for _ in range(3)])
    points = [root]

    for x in [(0,1,0), (0,0,1)]:
        points.append(get(vAdd(x, root)))

    poly, _ = cmds.polySphere()
    cmds.xform(poly, t=goal)
    curve = cmds.curve(p=(0, root[1], root[2]))
    curve2 = cmds.curve(p=root)

    step = root[0] * 0.8
    step = 1

    for _ in range(50):
        # Grab the three recent points
        p3, p1, p2 = points[-3:]
        crs = position(p1, p2, p3)
        n_move = norm(crs[1:])
        move = vMul(get([0, n_move[0], n_move[1]]), step)
        # step = (step - move[0]) * 0.8
        # if step < 0:
        #     step *= -1
        #     move = inv(move)


        cmds.curve(curve, a=True, p=(0, move[1], move[2]))
        cmds.curve(curve2, a=True, p=move)
        points.append(move)

    #
    # cmds.xform(p1, t=goal)
    #
    # points = [[random.randrange(-10, 10) for _ in range(2)] for _ in range(3)]
    # for n, p in enumerate(points):
    #     tmp = p + [0]
    #     loc = cmds.spaceLocator(p=tmp, n="Point%s" % n)
    #     d = math.sqrt(sum((tmp[i]-goal[i]) ** 2 for i in range(3)))
    #     p.append(d)
    #
    # CA = vSub(points[0], points[2])
    # CB = vSub(points[1], points[2])
    # crs = cross(CA, CB)
    # if crs[-1] < 0:
    #     crs = [-a for a in crs]
    # mag = math.sqrt(sum(a*a for a in crs))
    # norm = [a/mag for a in crs]
    # vec = [norm[i]*d+tmp[i] for i in range(3)]
    # cmds.curve(p=[(vec[0], vec[1], 0), tmp])
