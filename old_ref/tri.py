import maya.cmds as cmds
import random
import heapq

def distance(p1, p2):
    p1p2 = (p2[i]-p1[i] for i in range(len(p1)))
    return length(p1p2)

def length(v1):
    mag2 = sum(a*a for a in v1)
    return mag2 and (mag2 ** -0.5) * mag2

def vadd(v1, v2):
    return [v1[i]+v2[i] for i in range(len(v1))]

def vsub(v1, v2):
    return [v1[i]-v2[i] for i in range(len(v1))]

def vmul(v1, s1):
    return [v1[i]*s1 for i in range(len(v1))]

def vector():
    return [random.randrange(-10, 10) for _ in range(3)]

def eq(v1, v2):
    for i in range(len(v1)):
        if abs(v1[i]-v2[i]) > 0.001:
            return False
    return True


def test():
    cmds.file(new=True, force=True)

    def step(vec):
        x, y, z = vec
        x = distance(goal, (0, y, z))
        return x, y, z

    goal = vector()
    p1, _ = cmds.polySphere()
    cmds.xform(p1, t=goal)

    queue = sorted([step(vector()) for _ in range(3)], key=lambda x: x[0])

    last = queue[1]
    for _ in range(20):
        trio = queue[:3]
        if eq(trio[0], last):
            trio = queue[1:4]
        last = trio[0]

        diff = vadd(vmul(vsub(trio[0], trio[1]), 0.5), trio[1])
        aim = vsub(diff, trio[2])
        move = vadd(vmul(aim, 1.5), trio[2])
        queue.append(step(move))
        queue.sort(key=lambda x: x[0])

        print "Distance:", step(move)[0]

        cmds.spaceLocator(p=move)

        # for p in trio:
        #     cmds.spaceLocator(p=p)
        # p1, _ = cmds.polyCube()
        # cmds.xform(p1, t=diff)
        # cmds.curve(p=[trio[2], move])
