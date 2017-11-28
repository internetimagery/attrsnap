# Match a curve to the position
import maya.cmds as cmds

def curve(a, b, c, x):
    """ sample curve """
    y = a*x**2 + b*x + c
    return y

def distance(obj1, obj2):
    p1 = cmds.xform(obj1, q=True, ws=True, t=True)
    p2 = cmds.xform(obj2, q=True, ws=True, t=True)
    p1p2 = (b-a for a,b in zip(p1, p2))
    mag2 = sum(a*a for a in p1p2)
    return mag2 and (mag2 ** -0.5) * mag2




def test():
    cmds.file(new=True, force=True)

    ply1, _ = cmds.polySphere()
    cmds.xform(ply1, t=(3,4,5))

    loc1 = cmds.spaceLocator()[0]

    points = []
    for x in range(-10, 10):
        for z in range(-10, 10):
            cmds.xform(loc1, t=(x, 0, z))
            y = distance(loc1, ply1)
            pnt = (x, y, z)
            cmds.spaceLocator(p=pnt)
            points.append(pnt)




    # # crv = cmds.curve(p=(0,0,0))
    # for i in range(-10, 11):
    #     a,b,c = 3,5,0.8
    #     pos = (i, curve(a,b,c,i), 0)
    #     try:
    #         cmds.curve(crv, a=True, p=pos)
    #     except NameError:
    #         crv = cmds.curve(p=pos)
