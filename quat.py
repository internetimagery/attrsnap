# Testing quaternion distance metric
import element_maya
import maya.cmds as cmds

reload(element_maya)

def test():
    cmds.file(new=True, force=True)


    p1 = cmds.polyCube()[0]
    p2 = cmds.polyCube()[0]
    mkr = element_maya.Marker_Set(p1, p2)

    points = []
    for x in range(-180, 180, 10):
        for y in range(-180, 180, 10):
            for z in range(-180, 180, 10):
                # for k in range(-180, 180, 10):
                cmds.xform(p2, ro=(x,y,z))
                dist = mkr.get_rot_distance()
                points.append((x,y,z,dist))

    g1 = cmds.group(n="XY", em=True)
    g2 = cmds.group(n="XZ", em=True)
    g3 = cmds.group(n="YZ", em=True)

    for p in points:
        cmds.parent(cmds.spaceLocator(p=(p[0]*0.1, p[1]*0.1, p[-1])), g1)
        cmds.parent(cmds.spaceLocator(p=(p[0]*0.1, p[2]*0.1, p[-1])), g1)
        cmds.parent(cmds.spaceLocator(p=(p[1]*0.1, p[2]*0.1, p[-1])), g1)

    
