# Match positions / rotations.
from __future__ import print_function
import maya_elem as elem
import collections
import uuid

POSITION = 0
ROTATION = 1

class ID_Map(collections.Mapping):
    """ Entries have ID's. """
    def __init__(s):
        s.data = {}
    def __contains__(s, ID):
        return ID in s.data
    def __iter__(s):
        for ID in s.data:
            yield ID, s.data[ID]
    def __len__(s):
        return len(s.data)
    def add(s, value):
        ID = uuid.uuid4()
        s.data[ID] = value
        return ID
    def remove(s, ID):
        del s.data[ID]

group_data = collections.namedtuple("Group Data", [
    "name",
    "markers",
    "attributes"])

class Group_Set(ID_Map):
    """ Manage a collection of groups """
    def new(s, name="Group"):
        """ Create a new group. Return its id """
        return s.add(group_data(name, [], {}))

    def set_markers(s, ID, maker1, marker2):
        """ Set markers """
        s.data[ID].markers = [marker1, marker2]
        return s
    def get_markers(s, ID):
        """ Get marker info """
        return s.data[ID].markers

    def add_attribute(s, ID, name, min=0, max=0):
        """ Add an attribute """
        s.data[ID].attributes[name] = [min,max]
        return s
    def remove_attribute(s, ID, name):
        """ Take an attribute out """
        del s.data[ID]
        return s

class Group(object):
    """ A group of objects and attributes for matching """
    def __init__(s, match_type=POSITION, markers, *attributes):
        s.match_type = match_type
        s.markers = elem.Marker_Set(*markers)
        s.attributes = [elem.Attribute(a, b) for a, b in attributes]

    def get_values(s):
        """ Get a list of attribute values at the current time """
        return tuple(a.get_value() for a in s.attributes)

    def set_values(s, vals):
        """ Set a list of values to each attribute """
        for attr, val in zip(s.attributes, vals):
            attr.set_value(val)

    def get_distance(s):
        """ Calculate a distance value from our markers """
        if s.match_type == POSITION:
            return s.markers.get_pos_distance()
        elif s.match_type == ROTATION:
            return s.markers.get_rot_distance()
        else:
            raise RuntimeError("Distance type not supported.")

    def keyframe(s, values):
        """ Set a bunch of keyframes for each attribute """
        raise NotImplementedError
        for at in s.attributes:
            # Set keyframe!
            pass

    def __len__(s):
        return len(s.attributes)

    def __iter__(s):
        for at in s.attributes:
            yield at

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
