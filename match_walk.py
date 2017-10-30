# Walk to goal.

from __future__ import print_function
import collections
import itertools
import task
import math

Node = collections.namedtuple("Node", [
    "values", # Values of attributes at current point
    "to_goal", # Distance to goal
    "last_dist", # Distance value from last step
    "calibration"]) # How far we can travel
    # "path"]) # Path traveled (use for prediction. TODO:)

def distance(point1, point2):
    """ Distance between two points """
    return math.sqrt(sum((b - a) ** 2 for a, b in zip(point1, point2)))

def match(group):
    """ Match by wandering over to the right place (hopefully) """
    queue = task.Task()
    seen = set()
    combinations = tuple(itertools.product(*itertools.tee(range(-1, 2), len(group))))

    # Kick us off
    root_values = group.get_values()
    queue.add(Node(
        values = root_values,
        to_goal = group.get_distance(),
        last_dist = group.get_distance(),
        calibration = [1] * len(combinations)))

    for node in queue:
        if node.values not in seen:
            group.set_values(node.values)
            dist = group.get_distance()
        for step, combo in zip()
