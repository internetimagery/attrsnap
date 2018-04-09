import maya.cmds as cmds
import element
import groups
import random
import match

def main():

    rand = lambda: tuple(random.randrange(-10,10) for _ in range(3))

    cmds.file(new=True, force=True)

    m1, _ = cmds.polySphere()
    m2 = cmds.group(em=True)
    m3 = cmds.group(m2)

    cmds.xform(m1, t=rand())
    cmds.xform(m2, t=rand())
    cmds.setAttr(m2 + ".ty", 0)
    cmds.setAttr(m1 + ".ty", -3)
    cmds.setAttr(m3 + ".scaleX", 2)
    cmds.setAttr(m3 + ".scaleZ", 6)

    template = groups.Template(
        markers=[(m1, m2)],
        attributes=[{"obj": m1, "attr": "tx"}, {"obj": m2, "attr": "tz"}])
    grp = groups.Group(template)

    # curve1 = element.Curve(grp.markers.node1.get_position())
    n1 = grp.markers[0].node1.get_position()
    n2 = grp.markers[0].node2.get_position()
    curve = element.Curve([n2[0], (n2-n1).length() ,n2[2]])

    match.search2(grp)

    # for dist, values in match.search(grp, debug=True):
    #     n1 = grp.markers[0].node1.get_position()
    #     n2 = grp.markers[0].node2.get_position()
    #     curve.add([n2[0], (n2-n1).length() ,n2[2]])
    #
    # grp.set_values(values)
    #
    x1, _, z1 = cmds.xform(m1, q=True, ws=True, t=True)
    x2, _, z2 = cmds.xform(m2, q=True, ws=True, t=True)
    print(x1, z1)
    print(x2, z2)
    assert abs(x1-x2) < 0.01
    assert abs(z1-z2) < 0.01
