# Testing quaternion distance metric
import element_maya
import maya.cmds as cmds

reload(element_maya)

def test():
    cmds.file(new=True, force=True)


    p1 = cmds.polyCube()[0]
    p2 = cmds.polyCube()[0]
    mkr = element_maya.Marker_Set(p1, p2)

    for x in range(-180, 180, 10):
        for z in range(-180, 180, 10):
            # for k in range(-180, 180, 10):
            cmds.xform(p2, ro=(x,0,z))
            dist = mkr.get_rot_distance()
            cmds.spaceLocator(p=(x*0.1, dist*10, z*0.1))
