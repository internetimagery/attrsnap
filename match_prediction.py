# Match using predictions.

from __future__ import print_function, division
import collections
import itertools
import locate
import heapq
import time

def normalize(vector):
    mag2 = sum(a*a for a in vector)
    mag = mag2 and (mag2 ** -0.5) * mag2
    return tuple(mag and a / mag for a in vector)

Node = collections.namedtuple("Node", [
    "distance", # Distance from goal
    "traveled", # How far we have moved from the beginning
    "values", # Values that lead us here
    "calibration", # Calibrate
    "confidence", # How accurate we are with our estimates
    "step"]) # Reference to last node

def match(group, update_callback, step_chunk=0.3, path_cutoff=3, timeout=0.5):
    """ Match location using vairious levels of prediction """

    root_values = closest_values = group.get_values()
    root_distance = closest_distance = group.get_distance()
    step = root_distance * step_chunk # Break distance into chunks to travel

    queue = []
    combinations = {}
    for combo in itertools.product(*itertools.tee(range(-1, 2), len(group))):
        combo = normalize(combo)
        if sum(combo): # skip (0,0,0) values
            group.set_values(a+b for a,b in zip(combo, root_values))
            diff = group.get_distance() - root_distance
            inv = diff and 1 / diff
            combinations[combo] = inv

    heapq.heappush(queue, Node(
        distance = root_distance,
        traveled = 0,
        values = root_values,
        calibration = 1,
        confidence = 1,
        step=1))

    update_callback(0) # Get going!

    end = time.time() + timeout
    while len(queue):
        if time.time() > end:
            print("Match Timed Out")
            break
        node = heapq.heappop(queue)
        if node.traveled < path_cutoff:

            # set our poistion and check it
            group.set_values(node.values)
            distance = group.get_distance()
            if distance < 0.001: # We made it!
                closest_values = node.values
                break

            # Update our confidence and calibration
            inv_distance = node.distance and 1 / node.distance
            confidence = abs(inv_distance * distance)
            calibration = node.calibration * confidence
            print(calibration)

            # Decide on our step size
            next_step = confidence * step if step >= distance else distance

            # Predict some more steps
            for combo, inv in combinations.items():
                dist_prediction = next_step * inv + distance
                heapq.heappush(queue, Node(
                    distance = dist_prediction,
                    traveled = node.traveled + 0 if dist_prediction < closest_distance else 1,
                    values = tuple(a * inv * calibration * next_step + b  for a, b in zip(combo, node.values)),
                    calibration = calibration,
                    confidence = confidence,
                    step=next_step * inv))

            if distance < closest_distance:
                print("closer!", node.traveled)
                closest_distance = distance
                closest_values = node.values
                update_callback(1 - (closest_distance / root_distance))
    else:
        print("Queue exhausted.")
    update_callback(1)
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
