# Match positions / rotations.
from __future__ import print_function
import maya.api.OpenMaya as om
import maya.cmds as cmds
import match
# import contextlib

def get_node(name):
    """ Get Node """
    sel = om.MSelectionList()
    sel.add(name)
    return sel.getDependNode(0)

def get_plug(obj, attr):
    """ Get attribute from mayas API ugh """
    obj = get_node(obj)
    func = om.MFnDependencyNode(obj)
    attr = func.attribute(attr)
    return om.MPlug(obj, attr)

# @contextlib.contextmanager
# def safe_state():
#     """ Disable Autokey and keep the scene in a usable state """
#     state = cmds.autoKeyframe(q=True, st=True)
#     err = cmds.undoInfo(openChunk=True)
#     try:
#         cmds.autoKeyframe(st=False)
#         yield
#     except Exception as err:
#         raise
#     finally:
#         cmds.autoKeyframe(st=state)
#         cmds.undoInfo(closeChunk=True)
#         if err:
#             cmds.undo()

class Attribute(object):
    """ An Attribute """
    threshold = 0.001 # Negate tiny adjustments
    def __init__(s, obj, attr):
        s.obj, s.attr = obj, attr # Store variables
        s.min, s.max = -9999999, 9999999 # Initialize max / min range
        query = lambda **kwargs: cmds.attributeQuery(attr, n=obj, **kwargs) # REUSE!
        if not query(ex=True):
            raise RuntimeError("\"{}\" does not exist.".format(attr))
        if query(mne=True):
            s.min = query(min=True)
        if query(mxe=True):
            s.max = query(max=True)
        s.plug = plug = getPlug(obj, attr)
        s.current = plug.asDouble()
    def __str__(s):
        return s.plug.name()
    def set_value(val):
        """ Set attribute value """
        s.threshold
        val = max(s.min, min(val, s.max)) # Ensure we are capped to the range limit
        if val < s.current - threshold or s.current + threshold < val: # Check we are outside the threshold
            s.plug.setDouble(val)
            s.current = val
    def get_value():
        """ Get current value """
        return s.current

class Transform(object):
    """ A maya object """
    def __init__(s, name):
        obj = get_node(name)
        s.transform = om.MFnTransform(om.MDagPath.getAPathTo(obj))
    def __str__(s):
        return s.transform.name()
    def get_position(s):
        """ Get position of object """
        return s.transform.translation(om.MSpace.kWorld)

class Group(match.Group):
    """ A group of objects and attributes for matching """
    def __init__(s, match_type, markers, *attributes):
        s.match_type = match_type
        s.markers = [Transform(a) for a in markers]
        s.attributes = [Attribute(a, b) for a, b in attributes]

    def get_positions(s):
        """ Get a list of positions / rotations from objects """
        return tuple(a.get_position() for a in s.markers)

    def get_values(s):
        """ Get a list of attribute values at the current time """
        return tuple(a.get_value() for a in s.attributes)

    def set_values(s, vals):
        """ Set a list of values to each attribute """
        for attr, val in zip(s.attributes, vals):
            attr.set_value(val)

    def get_distance(s, root_pos, curr_pos):
        """ Calculate a distance value from two positionals """
        # Calculate distance or rotational distance. OR whatever we are using.
        # Returns single number
        # Distance positionally:
        return sum((a-b).length() for a, b in zip(curr_pos, root_pos))

    def keyframe(s, values):
        """ Set a bunch of keyframes for each attribute """
        for at in s.attributes:
            # Set keyframe!
            pass

if __name__ == '__main__':
    import random
    cmds.autoKeyframe(state=False)
    for i in range(1,4): # Run 3 Tests
        print("Running test %s." % i)
        objs = ["obj%s" % a for a in range(3)]
        for o in objs: # Set up some objects in random placements
            if cmds.objExists(o):
                cmds.delete(o)
            cmds.polyCube(n=o)
            random_pos = [random.random() * 20 - 10 for a in range(3)]
            cmds.xform(o, t=random_pos)
        cmds.parent(objs[1], objs[0]) # Create lever action
        cmds.refresh()
        print("Starting a new test in...")
        for t in range(3,0,-1):
            time.sleep(1)
            print(t)
        time.sleep(1)

        objA, objB, objC = objs
        objs = [objB, objC]
        attrs = (
            (objA, "translateX"),
            (objA, "translateY"),
            (objA, "rotateX"),
            (objA, "rotateY"),
            (objA, "rotateZ"),
        )
        group = Group("pos", objs, attrs)
        match.match([group])
        time.sleep(3)
    print("Tests complete!")
