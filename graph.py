# Graph some matching curves
import maya.cmds as cmds


START, END = 0, 100

def graph(start, end, obj):
    attr = position(obj)
    return cmds.curve(d=3, p=[cmds.getAttr(attr, t=fr)[0] for fr in range(start, end+1)])

def position(obj):
    dec = cmds.shadingNode("decomposeMatrix", asUtility=True)
    cmds.connectAttr("{}.worldMatrix[0]".format(obj), "{}.inputMatrix".format(dec), force=True)
    return "{}.outputTranslate".format(dec)

def distance(obj1, obj2):
    dist = cmds.shadingNode("distanceBetween", asUtility=True)
    cmds.connectAttr(position(obj1), "{}.point1".format(dist), force=True)
    cmds.connectAttr(position(obj2), "{}.point2".format(dist), force=True)
    return "{}.distance".format(dist)

def linear():
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
    dist = distance(marker1, marker2)
    cmds.connectAttr(dist, "{}.translateY".format(pointer1), force=True)
    cmds.connectAttr(attr, "{}.translateX".format(pointer1), force=True)

    curve1 = graph(START, END, pointer1)
    grp2 = cmds.group(pointer1, curve1, n="Linear_graph")

    return grp1, grp2

def linear2():
    # Get variables
    marker1, _ = cmds.polySphere()
    marker2, _ = cmds.polySphere()
    attr = "{}.translateX".format(marker1)
    grp1 = cmds.group(marker1, marker2, n="Linear2")

    # Scene setup
    cmds.xform(marker2, t=(0,5,0))
    cmds.setKeyframe(attr, t=0, v=-10, ott="linear")
    cmds.setKeyframe(attr, t=100, v=10, itt="linear")

    # Graph setup
    pointer1 = cmds.spaceLocator()[0]
    dist = distance(marker1, marker2)
    cmds.connectAttr(dist, "{}.translateY".format(pointer1), force=True)
    cmds.connectAttr(attr, "{}.translateX".format(pointer1), force=True)

    curves = []
    for i in range(5):
        cmds.xform(marker2, t=(0,i*2,0))
        curves.append(graph(START, END, pointer1))

    grp2 = cmds.group(pointer1, *curves, n="Linear_graph")

    return grp1, grp2

def rotation():
    # Get variables
    marker1, _ = cmds.polySphere()
    marker2, _ = cmds.polySphere()
    offset1 = cmds.group(marker1, n="{}_offset".format(marker1))
    attr = "{}.rotateZ".format(offset1)
    grp1 = cmds.group(offset1, marker2, n="Rotation")

    # Scene setup
    cmds.xform(marker2, t=(0,5,0))
    cmds.xform(marker1, t=(0,5,0))
    cmds.setKeyframe(attr, t=0, v=-180, ott="linear")
    cmds.setKeyframe(attr, t=100, v=180, itt="linear")

    # Graph setup
    pointer1 = cmds.spaceLocator()[0]
    dist = distance(marker1, marker2)
    scale = cmds.shadingNode("multiplyDivide", asUtility=True)
    cmds.setAttr("{}.input2Z".format(scale), 0.06)
    cmds.connectAttr(attr, "{}.input1Z".format(scale), force=True)
    cmds.connectAttr("{}.outputZ".format(scale), "{}.translateX".format(pointer1), force=True)
    cmds.connectAttr(dist, "{}.translateY".format(pointer1), force=True)

    curve1 = graph(START, END, pointer1)
    grp2 = cmds.group(pointer1, curve1, n="Rotation_graph")

    return grp1, grp2


def test():
    cmds.file(new=True, force=True)
    cmds.autoKeyframe(state=False)

    # grp1, grp2 = linear()
    # cmds.xform(grp1, t=(0,10,0))
    # cmds.xform(grp2, t=(0,5,0))

    # grp3, grp4 = rotation()
    # cmds.xform(grp3, t=(0,5,0))
    # cmds.xform(grp4, t=(0,-5,0))

    grp5, grp6 = linear2()
