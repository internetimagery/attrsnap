# Grouping match candidates with attributes
# Created By Jason Dixon. http://internetimagery.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is a labor of love, and therefore is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

from __future__ import print_function, division
import element
import json
import math
import sys

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

    def get_distance(s, log=math.log):
        """ Calculate a distance value from our markers """
        import math
        if s.match_type == POSITION:
            dist = sum(a.get_pos_distance() for a in s.markers) / len(s.markers)
            return log(dist if dist > 0 else sys.float_info.min)
        elif s.match_type == ROTATION:
            dist = sum(a.get_rot_distance() for a in s.markers) / len(s.markers)
            return log(dist if dist > 0 else sys.float_info.min, 1.1)
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
