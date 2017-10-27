# Perform matching.
from __future__ import print_function, division
# import collections
import itertools
import time
import heapq


# TODO: Add this as some sort of callback. Keep maya stuff out of here.
def update():
    import maya.cmds as cmds
    cmds.refresh()

Node = collections.namedtuple("Node", ["values", "distance", "stride"])

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
    def __init__(s, match_type, objs, *attributes):
        s.match_type, s.objs, s.attributes = match_type, objs, attributes

    def get_positions(s):
        """ Get a list of positions / rotations from objects """
        raise NotImplementedError()

    def get_values(s):
        """ Get a list of attribute values at the current time """
        raise NotImplementedError()

    def set_values(s, vals):
        """ Set a list of values to each attribute """
        raise NotImplementedError()

    def get_distance(s, root_pos, curr_pos):
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



def match(groups, timeout=2.5, step_length=0.25, stop_threshold=0.001, update_interval=0.5):
    """ Match a bunch of groups """
    start_time = last_refresh = time.time()
    # Firstly calibrate our motions to efficiently use each attribute.
    print("Matching...")
    # Loop each combo. Brute force, but we don't want different combinations from making us miss our mark.
    for combo in itertools.permutations(groups):
        for group in combo:
            # Mark how long sice last forward motion.
            last_success = time.time()

            # Initialize our position.
            current_distance = group.get_distance()
            current_values = group.get_values()
            current_stride = current_distance * step_length # Set up our initial stride size

            # Create our first node!
            current_node = Node(current_values, current_distance, current_stride)

            # Record where we have been
            visited = set() # Don't retrace our steps...
            to_visit = Task(current_node)
            closest = current_node

            # Here we go!
            try:
                while len(to_visit):
                    deadend = True
                    curr_node = to_visit.get()
                    for move_values in group.motion: # Make one step each way!
                        new_values = [a * b for a, b in zip(move_values, curr_node.values)]
                        if new_values not in visited: # Do not backtrack!
                            visited.add(new_values)

                            # Move to position, and get distance
                            group.set_values(new_values)
                            new_distance = group.get_distance()

                            # Build a new node.
                            new_node = Node(new_values, new_distance, curr_stride)
                            to_visit.add(new_distance, new_node)

                            # Have we reached a dead end? Where we cannot get any closer?
                            if new_distance < curr_node.distance: # Are we closer?
                                deadend = False # We have somewhere to go!

                            # Are we on the right track?
                            if new_distance < closest.distance: # Are we the closest we have ever been?
                                closest = new_node
                                curr_time = time.time()
                                if curr_time - last_refresh > update_interval:
                                    last_refresh = curr_time
                                    update()

                            # If we are close enough to call it quits.
                            if new_distance < stop_threshold: raise StopIteration # We made it!

                    if deadend: # Deadend? Take smaller steps.
                        new_stride = curr_node.stride * 0.5 # Take smaller steps.
                        if 0.001 < new_stride:
                            new_node = Node(new_values, curr_node.distance, new_stride)
                            to_visit.add(curr_node.distance, new_node)

                    elapsed_time = time.time() - last_success
                    if timeout < elapsed_time: # Important!
                        print("Timed out...")
                        break
                else: # This should never really run.
                    print("Exhausted all options.")
            except StopIteration:
                print("Made it!")

            # Set our final keyframe
            group.keyframe(closest.values)

    total_time = (time.time() - start_time) * 1000
    print("Travel complete with a time of %s ms." % total_time)
    print("Finished with a distance of %s." % closest[0])
    print("Made %s attempts to get there with a time of %s ms per attempt." % (count, (total_time / count)))
