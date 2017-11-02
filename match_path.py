# Prediction based on paths

from __future__ import print_function, division
import collections
import itertools
import queue

Node = collections.namedtuple("Node", [
    "values",
    "to_goal_real",
    "to_goal_predicted",
    "from_root"])


def distance(point1, point2):
    """ Distance between two points """
    return math.sqrt(sum((b - a) ** 2 for a, b in zip(point1, point2)))


def match(group):
    """ Run through and match things! """
    # Get all combinations
    combinations = list(itertools.product(*itertools.tee(range(-1, 2), len(group))))



    # Start by collecting our initial information.
    root_values = last_values = group.get_values()
    root_distance = last_distance = group.get_distance()
    if not root_distance: # On the off chance that we are already here... Stop! Yay!
        return root_values
    root_node = Node(
        values = root_values,
        to_goal = 1,
        length = 2,
        step = root_distance)
    # Normalize the distance
    distance_scale = 1 / root_distance

    # Track nodes
    Q = queue.Queue()
    Q.add(root_node, 1, 0)
    seen = set()

    # Run through our options!
    for node in Q:
        if node.values not in seen and node.length:
            seen.add(node.values)

            # Move to location and get the real distance.
            group.set_values(node.values)
            new_distance = group.get_distance()

            step = 1 # Set this somewhere!

            # Make some predictions
            for combo in combinations:
                val = [a * step + b for a, b in zip(combo, node.values)]
                to_goal = curr_distance + step
                Q.add(Node(
                    values = val,
                    to_goal = to_goal,
                    length = node.length - 1,
                    step = node.step),
                    to_goal * distance_scale,
                    distance(root_value, val) * distance_scale)
