# Walk to goal. Simple.

from __future__ import print_function, division
import collections
import itertools


def match(group):
    """ Match by wandering over to the right place (hopefully) """
    # Set up working materials
    queue = task.Task()
    seen = set()
    combinations = list(itertools.product(*itertools.tee(range(-1, 2), len(group))))
    calibration = [1] * len(combinations)

    curr_values = group.get_values()
    curr_distance = group.get_distance()

    step = 1


    for i in range(1, 3):
        step = (1 / i) * curr_distance
        chunk = {}
        for j in range(len(combinations)):
            new_values = [a * calibration[j] * step for a in combinations[j]]
            group.set_values(new_values)
            new_distance = group.get_distance()
            chunk[new_distance] = new_values

            diff = [b - a for a, b in zip(curr_values, new_values)]
            calibration[j] = (1 / diff) if diff else 0

        if chunk:
            # Take the closest move, and repeat!
            new_distance = min(chunk.keys())
            if new_distance < curr_distance:
                curr_distance = min(chunk.keys())
                curr_values = chunk[curr_distance]

    group.set_values(curr_values)
