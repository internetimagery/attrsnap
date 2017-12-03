# Maya elements

# Match positions / rotations.
from __future__ import print_function, division
import maya.api.OpenMaya as om
import maya.cmds as cmds
import math

def get_node(name):
    """ Get Node """
    sel = om.MSelectionList()
    sel.add(name)
    return sel.getDependNode(0)

def get_plug(obj, attr):
    """ Get attribute from mayas API ugh """
    node = get_node(obj)
    func = om.MFnDependencyNode(node)
    attr = func.attribute(attr)
    return om.MPlug(node, attr)

class Attribute(object):
    """ An Attribute """
    # threshold = 0.001 # Negate tiny adjustments
    def __init__(s, obj, attr, min_=-999999, max_=999999):
        query = lambda **kwargs: cmds.attributeQuery(attr, n=obj, **kwargs) # REUSE!
        if not query(ex=True):
            raise RuntimeError("\"{}\" does not exist.".format(attr))
        s._attr = get_plug(obj, attr)
        # We are working in radians
        s._is_angle = "doubleAngle" == query(at=True)

        s.min, s.max = min_, max_ # Initialize max / min range
        if query(mne=True):
            s.min = max(query(min=True), s.min)
        if query(mxe=True):
            s.max = min(query(max=True), s.max)

    def __repr__(s):
        """ Represent object in a usable state for cmds """
        return s._attr.name()

    def set_value(s, val):
        """ Set attribute value """
        if val < s.min:
            val = s.min
        elif val > s.max:
            val = s.max
        if s._is_angle:
            return s._attr.setMAngle(om.MAngle(val, om.MAngle.kDegrees))
        s._attr.setDouble(val)
        return val

    def get_value(s):
        """ Get current value """
        if s._is_angle:
            return s._attr.asMAngle().asDegrees()
        return s._attr.asDouble()

    def key(s, value):
        """ Keyframe value at current time """
        s.set_value(value) # Can't use values directly, as some attributes work in radians
        cmds.setKeyframe(str(s))

class Marker(object):
    """ A maya object """
    def __init__(s, name):
        s.name = name
        node = get_node(name)
        s.node = om.MFnTransform(om.MDagPath.getAPathTo(node))
    def __repr__(s):
        return s.node.name()
    def get_position(s):
        """ Get position of object """
        try:
            return s.node.translation(om.MSpace.kWorld)
        except RuntimeError:
            return om.MVector(cmds.xform(s.name, q=True, t=True, ws=True))
    def get_rotation(s):
        """ Get rotation of object """
        try:
            return s.node.rotation(om.MSpace.kWorld, True)
        except RuntimeError:
            m = cmds.xform(s.name, q=True, ws=True, m=True)
            w = (1 + m[0] + m[5] + m[10])
            qw = (w and (w ** -0.5)*w) / 2
            qx = m[6] - m[9]
            qy = m[8] - m[2]
            qz = m[1] - m[4]
            total = 4 * qw
            if not total:
                dot = sum(a*a for a in (qx,qy,qz))
                total = dot and (dot ** -0.5)*dot
            qx /= total
            qy /= total
            qz /= total
            return qx, qy, qz, qw

class Marker_Set(object):
    """ Collection of two markers """
    def __init__(s, node1, node2):
        s.node1 = Marker(node1)
        s.node2 = Marker(node2)

    def get_pos_distance(s, log=math.log):
        """ Get positional distance """
        dist = (s.node2.get_position() - s.node1.get_position()).length()
        return dist and log(dist)

    def get_rot_distance(s, log=math.log, sum=sum, zip=zip):
        """ Get rotational distance """
        r1 = s.node1.get_rotation()
        r2 = s.node2.get_rotation()
        diff = (a-b for a,b in zip(r1, r2))
        dist = sum(a*a for a in diff)
        return dist and log(dist,1.2)

    def __iter__(s):
        """ Loop over entries """
        yield s.node1
        yield s.node2

class Curve(object):
    def __init__(s, point):
        """ Path tool for debugging """
        from maya.cmds import curve
        s.func = curve
        s.curve = curve(p=point)
    def add(s, point):
        s.func(s.curve, a=True, p=point)

if __name__ == '__main__':
    cmds.file(new=True, force=True)
    obj, _ = cmds.polySphere()
    o = Transform(obj)
    at = Attribute(obj, "tx")
    print(o, at)
