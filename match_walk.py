# Walk to goal. Simple.

from __future__ import print_function, division
import collections
import itertools

# pick a bucnh of starting locations at random...
# TODO: Issue with using curr_distance to inform step

def match(group, update_callback):
    """ Match by wandering over to the right place. """
    # Set up working materials
    combinations = list(itertools.product(*itertools.tee(range(-1, 2), len(group))))
    calibration = [1] * len(combinations)

    curr_values = group.get_values()
    root_distance = curr_distance = group.get_distance()
    update_callback(0)

    step = curr_distance * 0.3

    # while step > 0.001:
    for i in range(200):
        chunk = {}
        for j in range(len(combinations)):
            new_values = [a * calibration[j] * step + b for a, b in zip(combinations[j], curr_values)]
            group.set_values(new_values)
            new_distance = group.get_distance()
            chunk[new_distance] = new_values

            diff = abs(new_distance - curr_distance)
            scale = (step / diff) if diff else 0
            calibration[j] = calibration[j] * scale if calibration[j] else scale

        if chunk:
            # Take the closest move, and repeat!
            new_distance = min(chunk.keys())
            if new_distance < curr_distance:
                curr_distance = new_distance
                curr_values = chunk[curr_distance]
                progress = (curr_distance / root_distance) if curr_distance and root_distance else 0
                update_callback(1 - progress)
                if curr_distance < step:
                    step = curr_distance
            else:
                step *= 0.5
        else:
            break
        # Reset ready for round two
        group.set_values(curr_values)
    update_callback(1) # Done
    return curr_values
