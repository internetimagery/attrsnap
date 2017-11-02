# Maya elements

# Match positions / rotations.
from __future__ import print_function
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
    def __init__(s, obj, attr):
        query = lambda **kwargs: cmds.attributeQuery(attr, n=obj, **kwargs) # REUSE!
        if not query(ex=True):
            raise RuntimeError("\"{}\" does not exist.".format(attr))
        s.attr = get_plug(obj, attr)

        s.min, s.max = -9999999, 9999999 # Initialize max / min range
        if query(mne=True):
            s.min = query(min=True)
        if query(mxe=True):
            s.max = query(max=True)

    def __str__(s):
        """ Represent object in a usable state for cmds """
        return "{}.{}".format(s.attr.node().name(), s.attr.name())

    def set_value(s, val):
        """ Set attribute value """
        if val <= s.max and s.min <= val:
            s.attr.setDouble(val)

    def get_value(s):
        """ Get current value """
        return s.attr.asDouble()

class Marker(object):
    """ A maya object """
    def __init__(s, name):
        node = get_node(name)
        s.node = om.MFnTransform(om.MDagPath.getAPathTo(node))
    def __str__(s):
        return s.node.name()
    def get_position(s):
        """ Get position of object """
        return s.node.translation(om.MSpace.kWorld)
    def get_rotation(s):
        """ Get rotation of object """
        return s.node.rotation(om.MSpace.kWorld, True)

class Marker_Set(object):
    """ Collection of two markers """
    def __init__(s, node1, node2):
        s.node1 = Marker(node1)
        s.node2 = Marker(node2)

    def get_pos_distance(s):
        """ Get positional distance """
        return (s.node2.get_position() - s.node1.get_position()).length()

    def get_rot_distance(s):
        """ Get rotational distance """
        return math.sqrt(abs(sum(b-a for a, b in zip(s.node1.get_rotation(), s.node2.get_rotation()))))

if __name__ == '__main__':
    cmds.file(new=True, force=True)
    obj, _ = cmds.polySphere()
    o = Transform(obj)
    at = Attribute(obj, "tx")
    print(o, at)
