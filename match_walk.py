# Walk to goal.

from __future__ import print_function, division
import collections
import itertools
import task
import math

Node = collections.namedtuple("Node", [
    "values", # Values of attributes at current point
    "to_goal", # Distance to goal
    "from_root", # Distance from starting location
    "prev_dist"]) # Distance from last step
    # "path"]) # Path traveled (use for prediction. TODO:)

def distance(point1, point2):
    """ Distance between two points """
    return math.sqrt(sum((b - a) ** 2 for a, b in zip(point1, point2)))

def match(group):
    """ Match by wandering over to the right place (hopefully) """
    # Set up working materials
    queue = task.Task()
    seen = set()
    combinations = itertools.product(*itertools.tee(range(-1, 2), len(group)))

    # Record starting
    root_values = group.get_values()
    root_distance = group.get_distance()
    closest = (root_distance, root_values)

    # Calibrate
    calibration = set()
    for combo in combinations:
        group.set_values(a + b for a, b in zip(combo, root_values))
        dist = group.get_distance()
        diff = dist - root_distance
        scale = (1 / diff) if diff else 0
        calibration.add([a * scale for a in combo])
    calibration = list(calibration)

    # Kick us off
    queue.add(Node(
        values = root_values,
        to_goal = root_distance,
        from_root = 0,
        last_dist = root_distance))

    # Loop our options
    for node in queue:
        # Visiting unique nodes only
        if node.values not in seen:
            seen.add(node.values)

            # Move to location, collect information
            group.set_values(node.values)
            to_goal = group.get_distance()
            from_root = distance(root_values, node.values)



        for step, combo in zip()
