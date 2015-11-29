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
import functools
import itertools
import contextlib
import collections
import maya.cmds as cmds
import maya.api.OpenMaya as om
from pprint import pprint as print

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

class Node(collections.Sequence):
    """ Pathfinding node """
    __slots__ = ("_pos", "_parent", "_distance")
    objs = None # Object to track
    attrs = None # Attributes
    stride = None # Step length
    stage = 0 # Stage of the scan
    def __init__(s, position, parent=None):
        s._parent = parent # Previous Node
        s._distance = None # Distance from goal
        s._pos = position # Location
    def __getitem__(s, k): return s._pos[k]
    def __repr__(s): return "Node :: %s" % repr(s._pos)
    def __hash__(s): return hash(s._pos)
    def __len__(s): return len(s._pos)
    def __lt__(s, n):
        try:
            return s.distance < n.distance
        except AttributeError:
            return s.distance < n
    @property
    def distance(s): # Heuristic
        dist = s._distance
        if dist is None:
            objA, objB = s.objs
            for at, p in zip(s.attrs, s._pos): at(p) # Move into place
            s._distance = dist = (objB() - objA()).length() # Get distance (heuristic)
        return dist

class Scanner(object):
    """ Scan through attributes """
    def __init__(s, objs, attrs):
        s.objs = objs = [Model(o) for o in objs]
        s.attrs = attrs = [Attribute(o, at) for o, at in attrs]
        s.movement = s.calibrate(attrs, objs)

    def calibrate(s, attrs, objs):
        """ Work out how much each combination moves and normalize """
        objA, objB = objs
        startA, startB = objA(), objB()
        combinations = [(-1, 0, 1)]*len(attrs)
        start_position = [a() for a in attrs]
        normalized = set()
        for c in itertools.product(*combinations):
            for at, offset, pos in zip(attrs, c, start_position): # Move attributes into place
                at(pos + offset)
            moveA = (objA() - startA).length() # Get distance moved
            moveB = (objB() - startB).length()
            total = moveA + moveB # Total distance moved
            scale = (1 / total) if total else 0
            normalized.add(tuple(a * scale for a in c)) # Normalized movement
        for at, pos in zip(attrs, start_position): # Move us back to start
            at(pos)
        return list(normalized) # list for quicker iteration

    def walk(s):
        """ Move to location """
        objs, attrs = s.objs, s.attrs
        movement = s.movement

        with safe_state():
            start_time = time.time() # Start the clock!
            timeout = 6 # Seconds
            count = 0 # Combination count
            success = 1 # Success count
            threshold = 0.001 # How close is made it?

            # Record our start location.
            base_position = tuple(a() for a in attrs) # Where we start from
            Node.objs, Node.attrs = objs, attrs # Initialize our nodes
            start_node = Node(base_position) # Root node
            Node.stride = start_node.distance * 0.3 # Step length

            visited = set() # Don't retrace our steps
            to_visit = [start_node] # Where to next?
            closest = start_node # Closest position so far

            print("Walking...")
            try:
                while len(to_visit):
                    curr_step = heapq.heappop(to_visit)
                    path_end = True
                    stride = curr_step.stride
                    for step in movement: # Check immediate surroundings
                        new_move = tuple(stride * a + b for a, b in zip(step, curr_step))
                        if new_move not in visited: # Don't backtrack
                            visited.add(new_move)
                            count += 1
                            new_step = Node(new_move, curr_step)
                            heapq.heappush(to_visit, new_step) # Mark as viable path
                            if new_step < threshold: raise StopIteration
                            if new_step < curr_step: # Are we closer?
                                path_end = False # We have somewhere to go!
                            if new_step < closest: # Are we closest we have ever been?
                                closest = new_step
                                success += 1
                                cmds.refresh() # Update view
                    if path_end: # Are we at a deadend?
                        curr_step.stride *= 0.3 # Narrow Search
                        if 0.001 < curr_step.stride:
                            heapq.heappush(to_visit, curr_step)

                    elapsed_time = time.time() - start_time
                    if timeout < elapsed_time: # Important!
                        print("Timed out...")
                        break
            except StopIteration:
                print("Made it!")
            for at, pos in zip(attrs, closest):
                at(pos); cmds.setKeyframe(at)
            total_time = (time.time() - start_time) * 1000
            print("Travel complete with a time of %s ms." % total_time)
            print("Finished with a distance of %s." % closest.distance)
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
