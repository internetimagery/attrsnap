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

def match(group, step_chunk=0.3, path_cutoff=3):
    """ Match location using vairious levels of prediction """

    root_values = closest_values = group.get_values()
    root_distance = closest_distance = group.get_distance()
    step = root_distance * step_chunk # Break distance into chunks to travel

    queue = []
    combinations = set()
    for combo in itertools.product(*itertools.tee(range(-1, 2), len(group))):
        group.set_value(a+b for a,b in zip(combo, root_values))
        diff = group.get_distance() - root_distance
        inv = diff and 1 / diff
        combinations.add(tuple(a * inv for a in combo))
    combinations = list(combinations)

    heapq.heappush(Node(
        to_goal = root_distance,
        from_start = 0,
        values = root_values,
        confidence = 1))

    while len(queue):
        node = heapq.heappop(queue)
        if node.from_start < path_cutoff:

            # set our poistion and check it
            group.set_value(node.values)
            distance = group.get_distance()
            if distance < 0.001: # We made it!
                closest_values = node.values
                print("Match found!")
                break

            # Update our confidence
            inv_distance = 1 / node.to_goal
            confidence = inv_distance * distance

            # Decide on our step size
            next_step = confidence * step if step >= distance else distance

            # Predict some more steps
            for combo in combinations:
                values = tuple(a * next_step for a, b in zip(combo, node.values))
                heapq.heappush(Node(
                    to_goal = next_step + distance,
                    from_start = node.from_start + 1,
                    values = values,
                    confidence = confidence))

            if distance < closest_distance:
                closest_distance = distance
                closest_values = node.values
    else:
        print("Queue exhausted.")
    return closest_values

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
