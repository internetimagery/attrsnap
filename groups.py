# Match positions / rotations.
from __future__ import print_function, division
import element
import json

POSITION = 0
ROTATION = 1

def save(groups, file_path):
    """ Export a list of groups into a file """
    data = []
    for group in groups:
        data.append({
            "name": group.get_name(),
            "type": group.get_type(),
            "markers": [str(a) for a in group.get_markers()],
            "attributes": [str(a) for a in group.get_attributes()]
            })
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def load(file_path):
    """ Load a list of groups from a file """
    pass

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
        s.attributes += [element.Attribute(*at) for at in attrs]

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
        for at, val in zip(s.attributes, values):
            at.key(val)

    def get_gradient(s, precision=0.001):
        """ Get gradient at current position. """
        result = []
        for attr in s.attributes:
            dist = s.get_distance()
            attr.set_value(attr.get_value() + precision)
            result.append((s.get_distance() - dist) / precision)
        return result

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
