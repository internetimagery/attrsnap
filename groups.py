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

try:
    from itertools import izip
except NameError:
    izip = zip

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

class WrapAttr(element.Attribute):
    """ Attribute wrapper with caching, metrics and allowing out of bounds."""
    def __init__(s, *args, **kwargs):
        s._cache = None
        s._num_calls = 0
        super(WrapAttr, s).__init__(*args, **kwargs)
    def clear_cache(s):
        s._cache = None
    def get_value(s):
        if s._cache is None:
            s._num_calls += 1
            s._cache = super(WrapAttr, s).get_value()
        return s._cache
    def set_value(s, val):
        s._num_calls += 1
        s._cache = val
        super(WrapAttr, s).set_value(s.min if val < s.min else s.max if val > s.max else val)
    def get_calls(s):
        return s._num_calls

class WrapMarkerSet(element.Marker_Set):
    """ Marker wrapper tracking calls to host """
    def __init__(s, *args, **kwargs):
        s._num_calls = 0
        super(WrapMarkerSet, s).__init__(*args, **kwargs)
    def get_pos_distance(s, *args, **kwargs):
        s._num_calls += 1
        return super(WrapMarkerSet, s).get_pos_distance(*args, **kwargs)
    def get_rot_distance(s, *args, **kwargs):
        s._num_calls += 1
        return super(WrapMarkerSet, s).get_rot_distance(*args, **kwargs)
    def get_calls(s):
        return s._num_calls

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
        s.num_calls = 0 # Track number of calls to "get_distance"
        s.name = template.name
        s.match_type = template.match_type
        s.markers = [WrapMarkerSet(*a) for a in template.markers]
        s.attributes = [WrapAttr(**a) for a in template.attributes]

    def clear_cache(s):
        """ Clear up cached data """
        for attr in s.attributes:
            attr.clear_cache()

    def get_calls(s):
        """ Return number of calls to host system """
        calls = sum(a.get_calls() for a in s.attributes)
        calls += sum(a.get_calls() for a in s.markers)
        return calls

    def get_name(s):
        """ Useful for debugging """
        return s.name

    def get_values(s):
        """ Get a list of attribute values at the current time """
        return tuple(a.get_value() for a in s.attributes)

    def set_values(s, vals):
        """ Set a list of values to each attribute """
        for attr, new_val in izip(s.attributes, vals):
            attr.set_value(new_val)

    def get_distance(s, adjust=math.log):
        """ Calculate a distance value from our markers """
        # Increase distance cost if out of bounds.
        cost = sum(abs(b - c.min) if b < c.min else abs(b - c.max) if b > c.max else 0
            for b, c in izip((a.get_value() for a in s.attributes), s.attributes))

        if s.match_type == POSITION:
            dist = sum(a.get_pos_distance() for a in s.markers) / len(s.markers)
            cost += adjust(dist if dist > 0 else sys.float_info.min)
        elif s.match_type == ROTATION:
            dist = sum(a.get_rot_distance() for a in s.markers) / len(s.markers)
            cost += adjust(dist if dist > 0 else sys.float_info.min, 1.2)
        else:
            raise RuntimeError("Distance type not supported.")
        return cost

    def keyframe(s, values):
        """ Set a bunch of keyframes for each attribute """
        for at, val in izip(s.attributes, s.bounds(values)):
            at.key(val)

    def shift(s, step=0.001):
        """ Shift location a little. """
        for attr in s.attributes:
            val = attr.get_value() + step
            if val > attr.max:
                val -= 2 * step
            attr.set_value(val)

    def get_gradient(s, precision=0.001, adjust=math.log):
        """ Get gradient at current position. """
        result = []
        dist = s.get_distance(adjust)
        for attr in s.attributes:
            value = attr.get_value()
            new_val = value + precision
            if new_val > attr.max:
                new_val = value - precision
            attr.set_value(new_val)
            new_dist = s.get_distance(adjust)
            result.append((new_dist - dist) / precision)
            dist = new_dist
        return result

    def bounds(s, vals):
        """ Fit values into range limitation """
        return (at.min if v < at.min else at.max if v > at.max else v for v, at in izip(vals, s.attributes))

    def __len__(s):
        return len(s.attributes)

    def __iter__(s):
        for at in s.attributes:
            yield at
