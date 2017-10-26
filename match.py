# Perform matching.
from __future__ import print_function, division
import itertools
import time
import heapq


# TODO: Add this as some sort of callback. Keep maya stuff out of here.
def refresh():
    import maya.cmds as cmds
    cmds.refresh()

# TODO: Investigate any issues if "step" runs us up against min/max barriers...
# TODO: Theoretically, calibrating a step next to a barrier would result in
# TODO: no distance being recorded, and thus a step size of 0. Even though
# TODO: the value may have movement further in the range of motion...
def calibrate(s, group):
    """ Determine how much of an impact each attribute has on our heuristic and thus our step size """
    combinations = [(-1, 0, 1)]*len(attrs) # Set some standard movement.
    root_value = group.get_values() # Get our initial attribute values
    root_position = group.get_positions() # Get our initial object positions
    normalized = set()

    for combo in itertools.product(*combinations): # Jump through different step combos
        step = (a + b for a, b in zip(root_value, combo)) # Calculate a step
        group.set_values(step) # Set values to make a step

        new_position = group.get_positions() # Get new position
        distance = group.get_distance(root_position, new_position) # Heuristic
        scale = (1.0 / distance) if distance else 0
        normalized.add(tuple(a * scale for a in combo)) # Normalize motion

    # Return us back where we were.
    group.set_values(root_position)
    return list(normalized) # Convert to list for faster iteration later

def match(groups, frame_start, frame_end, timeout=2.5, step_length=0.25, stop_threshold=0.001, refresh_interval=0.5):
    """ Match a bunch of groups """
    start_time = last_refresh = time.time()
    # Firstly calibrate our motions to efficiently use each attribute.
    steps = [calibrate(a) for a in groups] # Calibrate our step sizing
    print("Matching...")
    for combo in itertools.permutations(range(len(groups))):
        for c in combo:
            group = groups[c]
            step = steps[c]

            # Prepare some setup variables
            combo_start = time.time()
            node_id = 0 # Serves as a heapq tiebreaker
            success_count = 1

            # Initial distance cost

            root_distance = group.get_distance()
            root_values = group.get_values()
            root_stride = root_distance * step_length
            # Node = (distance left, node_id, current values, step to take)
            root_node = (root_distance, node_id, root_values, root_stride)

            # Record where we have been
            visited = set()
            to_visit = heapq.heapify([root_node])
            closest = root_node

            # Here we go!
            try:
                while len(to_visit):
                    deadend = True
                    curr_distance, _, curr_values, curr_stride = heapq.heappop(to_visit)
                    for step_values in step: # Make one step each way!
                        new_values = [a * b for a, b in zip(step_values, curr_values)]
                        if new_values not in visited: # Do not backtrack!
                            visited.add(new_values)
                            node_id += 1

                            # Move to position, and get distance
                            group.set_values(new_values)
                            new_distance = group.get_distance()

                            # Build a new node.
                            new_node = (new_distance, node_id, new_values, curr_stride)
                            heapq.heappush(to_visit, new_node)

                            if new_distance < stop_threshold: raise StopIteration # We made it!
                            if new_distance < curr_distance: # Are we closer?
                                deadend = False # We have somewhere to go!
                            if new_distance < closest[0]: # Are we the closest we have ever been?
                                closest = new_node
                                success += 1
                                curr_time = time.time()
                                if curr_time - last_refresh > refresh_interval:
                                    last_refresh = curr_time
                                    refresh()
                    if deadend: # Deadend? Take smaller steps.
                        new_stride = curr_stride * 0.5 # Take smaller steps.
                        if 0.001 < new_stride:
                            node_id += 1
                            new_node = (curr_distance, node_id, new_values, new_stride)
                            heapq.heappush(to_visit, new_node)

                    elapsed_time = time.time() - combo_start
                    if timeout < elapsed_time: # Important!
                        print("Timed out...")
                        break
                else: # This should never really run.
                    print("Exhausted all options.")
            except StopIteration:
                print("Made it!")

            # Set our final keyframe
            group.keyframe(closest[2])

    total_time = (time.time() - start_time) * 1000
    print("Travel complete with a time of %s ms." % total_time)
    print("Finished with a distance of %s." % closest[0])
    print("Made %s attempts to get there with a time of %s ms per attempt." % (count, (total_time / count)))
