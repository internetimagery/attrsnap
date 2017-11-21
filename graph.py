# Graph some matching curves
import maya.cmds as cmds







def linear():
    cmds.file(new=True, force=True)
    cmds.autoKeyframe(state=False)

    # Get variables
    marker1, _ = cmds.polySphere()
    marker2, _ = cmds.polySphere()
    attr = "{}.translateX".format(marker1)
    grp1 = cmds.group(marker1, marker2, n="Linear")

    # Scene setup
    cmds.xform(marker2, t=(0,5,0))
    cmds.setKeyframe(attr, t=0, v=-10, ott="linear")
    cmds.setKeyframe(attr, t=100, v=10, itt="linear")

    # Graph setup
    pointer1 = cmds.spaceLocator()[0]
    dist1 = cmds.shadingNode("distanceBetween", asUtility=True)
    cmds.connectAttr(attr, "{}.translateX".format(pointer1), force=True)
    cmds.connectAttr("{}.translate".format(marker1), "{}.point1".format(dist1), force=True)
    cmds.connectAttr("{}.translate".format(marker2), "{}.point2".format(dist1), force=True)
    cmds.connectAttr("{}.distance".format(dist1), "{}.translateY".format(pointer1), force=True)

    curve1 = cmds.curve(d=3, p=[cmds.getAttr("{}.translate".format(pointer1), t=fr)[0] for fr in range(101)])
    grp2 = cmds.group(pointer1, curve1, n="Linear_graph")

    return grp1, grp2



def test():
    grp1, grp2 = linear()
    # cmds.xform(grp1, t=(0,5,0))
    cmds.xform(grp2, t=(0,-5,0))
