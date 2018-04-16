import maya.cmds as cmds
import element
import groups
import random
import match

def main():

    cmds.file(new=True, force=True)
    for i in range(3):
        rand = lambda: tuple(random.randrange(-10,10) for _ in range(3))


        m1, _ = cmds.polySphere()
        m2 = cmds.group(em=True)
        m3 = cmds.group(m2)

        cmds.xform(m1, t=rand())
        cmds.xform(m2, t=rand())
        cmds.setAttr(m2 + ".ty", 0)
        cmds.setAttr(m1 + ".ty", -3)
        cmds.setAttr(m3 + ".scaleX", 2)
        cmds.setAttr(m3 + ".scaleZ", 6)

        matcher = [match.optim_adam, match.optim_nelder_mead, match.optim_random][i]
        template = groups.Template(
            markers=[(m1, m2)],
            attributes=[{"obj": m1, "attr": "tx"}, {"obj": m2, "attr": "tz"}])
        grp = groups.Group(template)

        # curve1 = element.Curve(grp.markers.node1.get_position())
        n1 = grp.markers[0].node1.get_position()
        n2 = grp.markers[0].node2.get_position()
        curve = element.Curve([n2[0], (n2-n1).length() ,n2[2]])

        cmds.autoKeyframe(state=False)
        print "="*20
        print "Running", matcher.__name__
        for prog in match.match([template], matcher=matcher, start_frame=1, end_frame=120):
            n1 = grp.markers[0].node1.get_position()
            n2 = grp.markers[0].node2.get_position()
            curve.add([n2[0], (n2-n1).length() ,n2[2]])

        x1, _, z1 = cmds.xform(m1, q=True, ws=True, t=True)
        x2, _, z2 = cmds.xform(m2, q=True, ws=True, t=True)
        # print(x1, z1)
        # print(x2, z2)
        print "Accuracy", (x1 - x2) + (z1 - z2)
        assert abs(x1-x2) < 1e-3, "Expected %s. Was %s" % (x1, x2)
        assert abs(z1-z2) < 1e-3, "Expected %s. Was %s" % (z1, z2)
        cmds.group([curve.curve, m1, m2, m3], n="Grp_%s" % matcher.__name__)
    print "="*20
