# Match using predictions.

from __future__ import print_function, division
import collections
import itertools
import locate
import heapq

Node = collections.namedtuple("Node", [
    "to_goal", # Distance from goal
    "from_start", # How far we have moved from the beginning
    "values", # Values that lead us here
    "confidence" # How accurate we are with our estimates
    ])

def match(group):
    """ Match location using vairious levels of prediction """
    queue = []
    combinations = tuple(itertools.product(*itertools.tee(range(-1, 2), len(group))))

    curr_values = group.get_values()
    curr_distance = group.get_distance()
    heapq.heappush(Node(
        to_goal = curr_distance,
        from_start = 0
        values = curr_values,
        confidence = 1,
        ))

    while len(queue):
        pass
    else:
        print("Queue exhausted.")

    # TODO: Calibrate one step in all directions?

    # TODO: "dumb" approach:
    # TODO: keep track of calibration
    # TODO: make predictions in all directions but only expand from queue
    # TODO: check predicted distance against actual distance
    # TODO: given margin of error, as our confidence level
    # TODO: adjust our step size based on confidence (high accuracy = high confidence)

    # TODO: "smart" approach:
    # TODO: keep track of locations and their distances
    # TODO: take three closest distances
    # TODO: predict position of end result
    # TODO: use prediction to predict a vector direction towards it
    # TODO: add to queue a node stepping in the direction towards goal

    # TODO: Investigate a cut off mechanism to prevent endless searching
    # TODO: Possible option: base queue first on travel distance
    # TODO: and any step towards the goal is treated as not adding value
