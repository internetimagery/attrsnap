# Testing quaternion distance metric
import maya.cmds as cmds
import maya.api.OpenMaya as om

def get_node(name):
    """ Get Node """
    sel = om.MSelectionList()
    sel.add(name)
    node = sel.getDependNode(0)
    return om.MFnTransform(om.MDagPath.getAPathTo(node))

def test():
    cmds.file(new=True, force=True)


    p1, _ = cmds.polyCube()
    p1t = get_node(p1)
    base = p1t.rotation(om.MSpace.kWorld, True)

    points = []
    for x in range(-180, 180, 30):
        for y in range(-180, 180, 30):
            for z in range(-180, 180, 30):
                # for k in range(-180, 180, 10):
                cmds.xform(p1, ro=(x,y,z))
                quat = p1t.rotation(om.MSpace.kWorld, True)
                diff = (a-b for a, b in zip(quat, base))
                # mag2 = sum(a*a for a in quat)
                points.append((x,y,z,sum(a*a for a in diff)))

    g1 = cmds.group(n="XY", em=True)
    g2 = cmds.group(n="XZ", em=True)
    g3 = cmds.group(n="YZ", em=True)

    for p in points:
        cmds.parent(cmds.spaceLocator(p=(p[0]*0.1, p[-1]*5, p[1]*0.1)), g1)
        cmds.parent(cmds.spaceLocator(p=(p[0]*0.1, p[-1]*5, p[2]*0.1)), g2)
        cmds.parent(cmds.spaceLocator(p=(p[1]*0.1, p[-1]*5, p[2]*0.1)), g3)

    cmds.xform(g1, t=(40,0,0))
    cmds.xform(g3, t=(-40,0,0))
