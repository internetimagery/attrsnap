# Match positions / rotations.
from __future__ import print_function, division
import element
import json

POSITION = 0
ROTATION = 1

def save(templates, file_path):
    """ Export a list of groups into a file """
    data = []
    for template in templates:
        data.append({
            "enabled": template.enabled,
            "name": template.name,
            "match_type": template.match_type,
            "markers": template.markers,
            "attributes": template.attributes})
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def load(file_path):
    """ Load a list of groups from a file """
    with open(file_path, "r") as f:
        return [Template(**d) for d in json.load(f)]

class Template(object):
    """ Hold information, for transfer """
    def __init__(s, name="Group", enabled=True, match_type=POSITION, markers=None, attributes=None):
        s.name = name
        s.enabled = enabled
        s.match_type=match_type
        s.markers = markers or []
        s.attributes = attributes or []

class Group(object):
    """ A group of objects and attributes for matching """
    def __init__(s, template):
        s.name = template.name
        s.match_type = template.match_type
        s.markers = [element.Marker_Set(*a) for a in template.markers]
        s.attributes = [element.Attribute(*a) for a in template.attributes]

    def get_name(s):
        """ Useful for debugging """
        return s.name

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
            return sum(a.get_pos_distance() for a in s.markers)
        elif s.match_type == ROTATION:
            return sum(a.get_rot_distance() for a in s.markers)
        else:
            raise RuntimeError("Distance type not supported.")

    def keyframe(s, values):
        """ Set a bunch of keyframes for each attribute """
        for at, val in zip(s.attributes, values):
            at.key(val)

    def shift(s, step=0.001):
        """ Shift location a little. """
        for attr in s.attributes:
            val = attr.get_value() + step
            if val > attr.max:
                val -= 2 * step
            attr.set_value(val)

    def get_gradient(s, precision=0.001):
        """ Get gradient at current position. """
        result = []
        dist = s.get_distance()
        for attr in s.attributes:
            value = attr.get_value()
            new_val = value + precision
            if new_val > attr.max:
                new_val = value - precision
            attr.set_value(new_val)
            new_dist = s.get_distance()
            result.append((new_dist - dist) / precision)
            dist = new_dist
        return result

    def bounds(s, vals):
        """ Fit values into range limitation """
        return (at.min if v < at.min else at.max if v > at.max else v for v, at in zip(vals, s.attributes))

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
