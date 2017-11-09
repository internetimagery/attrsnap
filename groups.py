# Match positions / rotations.
from __future__ import print_function
import element
import uuid

POSITION = 0
ROTATION = 1


class Group(object):
    """ A group of objects and attributes for matching """
    def __init__(s, name="", match_type=POSITION, markers=None, attributes=None):
        s.name = name
        s.match_type = match_type
        s.markers = []
        if markers:
            s.set_markers(*markers)
        s.attributes = []
        if attributes:
            s.add_attributes(*attributes)

    def get_name(s):
        """ Get name value """
        return s.name
    def set_name(s, name):
        """ Set name value """
        s.name = name.strip()
        return s

    def get_type(s):
        """ Get type value """
        return s.match_type
    def set_type(s, val):
        """ Set type value """
        s.match_type = val
        return s

    def get_markers(s):
        """ Get current markers """
        return s.markers
    def set_markers(s, m1, m2):
        """ Set markers """
        s.markers = element.Marker_Set(m1, m2)
        return s

    def get_attributes(s):
        """ List out attributes ascociated """
        return s.attributes
    def add_attributes(s, *attrs):
        """ Add some attributes """
        s.attributes += [element.Attribute(a, b) for a, b in attrs]

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
