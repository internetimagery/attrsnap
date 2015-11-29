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

@contextlib.contextmanager
def temp_obj(num=1):
    """ Create some temporary objects """
    objs = [cmds.group(em=True) for a in range(num)]
    try:
        yield objs
    finally:
        for o in objs:
            if cmds.objExists(o): cmds.delete(o)

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
        s.name = name = "%s.%s" % (obj, attr)
        s.current = cmds.getAttr(name)
    def __str__(s): return str(s.name)
    def __call__(s, val=None):
        """ Use to query or set the attribute """
        current, threshold = s.current, s.threshold
        if val is None: return current
        val = max(s.min, min(val, s.max))
        if val < current - threshold or current + threshold < val:
            cmds.setAttr(s, val); s.current = val

class Model(object):
    """ A model """
    def __init__(s, name):
        s.name = name
    def __str__(s): return str(s.name)
    def __call__(s):
        """ Get position of object """
        return om.MVector(cmds.xform(s.name, q=True, ws=True, rp=True))

class Scanner(object):
    """ Scan through attributes """
    def __init__(s, objs, attrs):
        s.objs = objs = [Model(o) for o in objs]
        s.attrs = attrs = [Attribute(o, at) for o, at in attrs]
        s.movement = s.calibrate(attrs, objs)

    def calibrate(s, attrs, objs):
        """ Work out how much each combination moves and normalize """
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
            distance = (center - objs[-1]).length()
        return distance

    def walk(s):
        """ Move to location """
        objs, attrs = s.objs, s.attrs
        movement = s.movement
        heuristic = s.heuristic

        with safe_state():
            with temp_obj(1) as tmp:
                start_time = time.time() # Start the clock!
                timeout = 6 # Seconds
                count = 0 # Combination count
                success = 1 # Success count
                threshold = 0.001 # How close is made it?

                # Find center
                center = tmp[0]
                for o in objs: cmds.pointConstraint(o, center) # Position obj

                # Record our start location.
                base_position = tuple(a() for a in attrs) # Where we start from
                base_distance = heuristic(base_position) # priority
                base_stride = base_distance * 0.25 # Step length
                start_node = (base_distance, base_position, base_stride)

                visited = set() # Don't retrace our steps
                to_visit = [start_node] # Where to next?
                closest = start_node # Closest position so far

                print("Walking...")
                try:
                    while len(to_visit):
                        curr_dist, curr_pos, curr_stride = heapq.heappop(to_visit)
                        path_end = True
                        for step in movement: # Check immediate surroundings
                            new_pos = tuple(curr_stride * a + b for a, b in zip(step, curr_pos))
                            if new_pos not in visited: # Don't backtrack
                                visited.add(new_pos)
                                count += 1
                                new_dist = heuristic(new_pos)
                                new_node = (new_dist, new_pos, curr_stride)
                                heapq.heappush(to_visit, new_node) # Mark on map
                                if new_dist < threshold: raise StopIteration # We made it!
                                if new_dist < curr_dist: # Are we closer?
                                    path_end = False # We have somewhere to go!
                                if new_dist < closest[0]: # Are we the closest we have ever been?
                                    closest = new_node
                                    success += 1
                                    cmds.refresh() # Update view
                        if path_end: # Are we at a deadend?
                            new_stride = curr_stride * 0.5 # Narrow Search
                            if 0.001 < new_stride:
                                new_node = (curr_dist, curr_pos, new_stride)
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
                print("Finished with a distance of %s." % closest[0])
                print("Made %s attempts to get there with a time of %s ms per attempt." % (count, (total_time / count)))


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
        scan = Scanner(objs, attrs)
        scan.walk()
        time.sleep(3)
    print("Tests complete!")
