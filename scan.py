# Walk from one position to another using arbitrary attirubtes
# Created By Jason Dixon. http://internetimagery.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
from __future__ import division, print_function

import time
import heapq
import operator
import functools
import itertools
import contextlib
import collections
import maya.cmds as cmds
import maya.api.OpenMaya as om
from pprint import pprint as print

def getNode(name):
    """ Get Node """
    sel = om.MSelectionList()
    sel.add(name)
    return sel.getDependNode(0)

def getPlug(obj, attr):
    """ Get attribute from mayas API ugh """
    obj = getNode(obj)
    func = om.MFnDependencyNode(obj)
    attr = func.attribute(attr)
    return om.MPlug(obj, attr)

@contextlib.contextmanager
def safe_state():
    """ Disable Autokey and keep the scene in a usable state """
    err = None; state = cmds.autoKeyframe(q=True, st=True)
    cmds.autoKeyframe(st=False)
    cmds.undoInfo(openChunk=True)
    try: yield
    except Exception as err: raise
    finally:
        cmds.undoInfo(closeChunk=True)
        if err: cmds.undo()
        cmds.autoKeyframe(st=state)

class Attribute(object):
    """ An Attribute """
    threshold = 0.001 # Negate tiny adjustments
    def __init__(s, obj, attr):
        s.obj, s.attr = obj, attr
        s.min = -9999999; s.max = 9999999
        query = functools.partial(cmds.attributeQuery, attr, n=obj)
        if not query(ex=True): raise RuntimeError, "%s does not exist." % attr
        if query(mne=True): s.min = query(min=True)
        if query(mxe=True): s.max = query(max=True)
        s.plug = plug = getPlug(obj, attr)
        s.current = plug.asDouble()
    def __str__(s): return s.plug.name()
    def __call__(s, val=None):
        """ Use to query or set the attribute """
        current = s.current
        if val is None: return current
        threshold = s.threshold
        val = max(s.min, min(val, s.max))
        if val < current - threshold or current + threshold < val:
            s.plug.setDouble(val); s.current = val

class Model(object):
    """ A model """
    def __init__(s, name):
        obj = getNode(name)
        s.transform = om.MFnTransform(om.MDagPath.getAPathTo(obj))
    def __str__(s): return s.transform.name()
    def __call__(s):
        """ Get position of object """
        return s.transform.translation(om.MSpace.kWorld)

class Node(collections.Sequence):
    """ Path Node """
    __slots__ = ("pos", "priority")
    attrs = None # attributes
    objs1 = None # Main objs
    objs2 = None # Secondary objs
    start2 = None # Start of Secondary
    stride = 0 # Step length
    def __init__(s, position, parent=None):
        o1, o2, at = s.objs1, s.objs2, s.attrs
        s.pos, s.parent = position, parent
        # Move into location
        for a, p in zip(at, position): a(p)
        s.to_goal = (o1[1]() - o1[0]()).length() # Dist from man objs
        s.to_cost = (o2[1]() - o2[0]()).length() # Dist from secondary

        if parent: s.stride = parent.stride # Take our stride

        s.pos = position # Position
        s.priority = s.to_goal # priority
    def __hash__(s): return hash(s.pos)
    def __lt__(s, n): return s.priority < s.priority
    def __getitem__(s, k): return s.pos[k]
    def __len__(s): return len(s.pos)

class Scanner(object):
    """ Scan through attributes """
    def __init__(s, attrs, objs1, objs2=None): # Primary / Secondary objs
        s.objs1 = objs1 = [Model(o) for o in objs1]
        s.objs2 = objs2 = [Model(o) for o in objs2] if objs2 else objs1
        s.attrs = attrs = [Attribute(o, at) for o, at in attrs]
        s.movement = s.calibrate(attrs, set(objs1 + objs2))

    def calibrate(s, attrs, objs):
        """ Work out how much each combination moves and normalize """
        with safe_state():
            combinations = [(-1, 0, 1)]*len(attrs)
            start_position = [a() for a in attrs]
            start_loc = [o() for o in objs]
            normalized = set()
            for c in itertools.product(*combinations):
                for at, offset, pos in zip(attrs, c, start_position): # Move attributes into place
                    at(pos + offset)
                curr_loc = [o() for o in objs] # New Position
                total = sum((a-b).length() for a, b in zip(curr_loc, start_loc))
                scale = (1 / total) if total else 0
                normalized.add(tuple(a * scale for a in c)) # Normalized movement
            for at, pos in zip(attrs, start_position): # Move us back to start
                at(pos)
            return list(normalized) # list for quicker iteration

    def heuristic(s, position, center=None):
        """ Suck all objects to the last selected """
        objs, attrs = s.objs, s.attrs
        # Move into location
        for at, pos in zip(attrs, position): at(pos)

        # Little computationally intensive...
        if center is None: # Calculate on the fly
            num = len(objs)
            pos = [a() for a in objs]
            vec = [pos[a-1] - pos[a] for a in range(num)]
            step = 1/num
            center = pos[-1] + reduce(operator.add, (step * a * b for a, b in enumerate(vec)))
            distance = (center - pos[-1]).length()

        # Quicker!
        else:
            center = om.MVector(cmds.xform(center, q=True, ws=True, rp=True))
            distance = (center - objs[-1]()).length()
        return distance

    def walk(s, timeout=6):
        """ Move to location """
        objs1, objs2, attrs = s.objs1, s.objs2, s.attrs
        movement = s.movement

        with safe_state():
            start_time = time.time() # Start the clock!
            count = 0 # Combination count
            success = 1 # Success count

            def dist(objs): # Get distance between obj pair
                return (objs[1]() - objs[0]()).length()

            # Get our step cost
            to_goal = dist(objs1) # Get distance of main objs
            to_cost = dist(objs2) # Get distance of secondary objs
            cost_scale = (to_goal / to_cost) if to_goal and to_cost else 0

            # Record our start location.
            start_position = tuple(a() for a in attrs) # Where we start from
            start_stride = to_goal * 0.25 # Step length
            start_node = (
                to_goal,
                start_position,
                start_stride,
                to_goal,
                0,
                0)

            # Track our path
            visited = set() # Don't retrace our steps
            to_visit = [start_node] # Where to next?
            closest = start_node # Closest position so far

            print("Walking...")
            try:
                while len(to_visit):
                    curr_priority, curr_pos, curr_stride, curr_dist, curr_cost, curr_offset = heapq.heappop(to_visit)
                    path_end = True
                    for step in movement: # Check immediate surroundings
                        new_pos = tuple(curr_stride * a + b for a, b in zip(step, curr_pos))
                        if new_pos not in visited: # Don't backtrack
                            visited.add(new_pos)
                            count += 1
                            # Move into location
                            for at, pos in zip(attrs, new_pos): at(pos)

                            # Work out cost to move
                            new_dist = dist(objs1)
                            new_offset = abs(dist(objs2) - to_cost)
                            moved = abs(curr_offset - new_offset) * cost_scale
                            new_cost = curr_cost + moved

                            new_priority = new_cost + new_dist

                            new_node = ( # Build a new node
                                new_priority, # Raise to top of the stack
                                new_pos, # Positional information
                                curr_stride, # Step Length
                                new_dist, # Distance from goal
                                new_cost, # How far have we traveled?
                                new_offset # Offset from our last move
                                )

                            heapq.heappush(to_visit, new_node) # Mark on map
                            if new_dist < 0.001: raise StopIteration # We made it!
                            if new_priority <= curr_priority: # Are we closer?
                                path_end = False # We have somewhere to go!
                            if new_dist < closest[3]: # Are we the closest we have ever been?
                                closest = new_node
                                success += 1
                                cmds.refresh() # Update view
                    if path_end: # Are we at a deadend?
                        new_stride = curr_stride * 0.5 # Narrow Search
                        if 0.001 < new_stride:
                            new_node = (
                                curr_priority,
                                curr_pos,
                                new_stride,
                                curr_dist,
                                curr_cost,
                                curr_offset
                            )
                            heapq.heappush(to_visit, new_node)

                    elapsed_time = time.time() - start_time
                    if timeout < elapsed_time: # Important!
                        print("Timed out...")
                        break
            except StopIteration:
                print("Made it!")
            for at, pos in zip(attrs, closest[1]):
                at(pos); cmds.setKeyframe(at)
            total_time = (time.time() - start_time) * 1000
            print("Travel complete with a time of %s ms." % total_time)
            print("Finished with a distance of %s." % closest[3])
            print("Made %s attempts to get there with a time of %s ms per attempt." % (count, (total_time / count)))

# TODO:
# Add secondary object check (pole vector)
# Normalize distances to match main distance1. ie: dist1 / dist2
# Add together to produce heuristic
# Track distance1 and only allow nodes that get us closer (TEST THIS)
# Perhaps add distance2 each step so the only decreasing distance is 1

if __name__ == '__main__':
    # Test functionality
    import random
    for i in range(1,4): # Run 3 Tests
        print("Running test %s." % i)
        objs = ["obj%s" % a for a in range(3)]
        for o in objs: # Set up some objects in random placements
            if cmds.objExists(o):
                cmds.delete(o)
            cmds.polyCube(n=o)
            random_pos = [random.random() * 10 - 5 for a in range(3)]
            cmds.xform(o, t=random_pos)
        cmds.parent(objs[1], objs[0]) # Create lever action
        cmds.refresh()
        print("Starting a new test in...")
        for t in range(3,0,-1):
            time.sleep(1)
            print(t)
        time.sleep(1)

        objA, objB, objC = objs
        objs = [objB, objC]
        attrs = (
            (objA, "translateX"),
            (objA, "translateY"),
            (objA, "rotateX"),
            (objA, "rotateY"),
            (objA, "rotateZ"),
        )
        scan = Scanner(attrs, objs)
        scan.walk()
        time.sleep(3)
    print("Tests complete!")
