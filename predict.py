# Idea:
# loop through all possible movements.
# calibrate.
# make prediction based on calibration.
# rinse repeat.

# Perform matching.
from __future__ import print_function, division
# import collections
import collections
import itertools
import heapq
import time


# TODO: Add this as some sort of callback. Keep maya stuff out of here.
def update():
    import maya.cmds as cmds
    cmds.refresh()

# Values = values of attributes at the time
# Distance = number representing distance from goal
# Stride = How far we will attempt to step
# Real = We have tested this value and not predicted?
Node = collections.namedtuple("Node", ["values", "distance"])

class Task(object):
    """ Ordered set of tasks """
    def __init__(s, *heap):
        s.heap = heapq.heapify(heap)
        s.id = 0
    def add(s, priority, task):
        s.id += 1
        heapq.heappush(s.heap, tuple(priority, s.id, task))
    def get(s):
        return heapq.heappop(s.heap)[2]
    def __len__(s):
        return len(s.heap)


class Group(object):
    """ A group of objects and attributes for matching """
    def __init__(s, match_type, markers, *attributes):
        s.match_type, s.markers, s.attributes = match_type, markers, attributes

    def get_positions(s):
        """ Get a list of positions / rotations from objects """
        raise NotImplementedError()

    def get_values(s):
        """ Get a list of attribute values at the current time """
        raise NotImplementedError()

    def set_values(s, vals):
        """ Set a list of values to each attribute """
        raise NotImplementedError()

    def get_distance(s, mark1, mark2):
        """ Calculate a distance value from two positionals """
        raise NotImplementedError()

    def keyframe(s, values):
        """ Set a bunch of keyframes for each attribute """
        raise NotImplementedError()

    # TODO: Investigate any issues if "step" runs us up against min/max barriers...
    # TODO: Theoretically, calibrating a step next to a barrier would result in
    # TODO: no distance being recorded, and thus a step size of 0. Even though
    # TODO: the value may have movement further in the range of motion...
    def calibrate(s):
        """ Determine how much of an impact each attribute has on our heuristic and thus our step size """
        # TODO: This number doesn't mean a lot. What is important is the relationship between the scale and value.
        # TODO: There can be a check that ensures we are not butted up against any min/max ranges. Nudge us out of the way if so.
        combinations = [(-1, 0, 1)]*len(s.attributes) # Set some standard movement.
        root_value = s.get_values() # Get our initial attribute values
        root_position = s.get_positions() # Get our initial object positions
        normalized = set()

        for combo in itertools.product(*combinations): # Jump through different step combos
            step = (a + b for a, b in zip(root_value, combo)) # Calculate a step
            s.set_values(step) # Set values to make a step

            new_position = s.get_positions() # Get new position
            distance = s.get_distance(root_position, new_position) # Heuristic
            scale = (1.0 / distance) if distance else 0
            normalized.add(tuple(a * scale for a in combo)) # Normalize motion

        # Return us back where we were.
        s.set_values(root_position)
        s.motion = list(normalized) # Convert to list for faster iteration later

def calibrate(group):
    combinations = [(-1, 0, 1)]*len(num_attributes) # Set some standard movement.
    root_value = group.get_values() # Get our initial attribute values
    root_distance = group.get_distance() # Get our initial distance
    result = {}
    for combo in itertools.product(*combinations): # Jump through different step combos
        step = (a + b for a, b in zip(root_value, combo)) # Calculate a step
        s.set_values(step) # Set values to make a step
        new_position = s.get_positions() # Get new position
        distance = s.get_distance(root_position, new_position) # Heuristic
        scale = (1.0 / distance) if distance else 0
        normalized.add(tuple(a * scale for a in combo)) # Normalize motion
    # Return us back where we were.
    s.set_values(root_position)
    s.motion = list(normalized) # Convert to list for faster iteration later

def movement(num_attributes):
    """ Return movement combinations """
    combinations = [(-1, 0, 1)]*len(num_attributes)
    return itertools.product(*combinations): # Jump through different step combos


def match(group):
    """ Match a group using predictive methods """
    new_node = Node(group.get_values(), group.get_distance())
    to_visit = Task(new_node[1], new_node)
    while len(to_visit):
        new_node = to_visit.get()
        real_distance = group.get_distance()
        # error = real_distance - new_node.distance
