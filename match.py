# Match two objects as close together as possible using as few steps as possible (still brute force!)
from __future__ import print_function, division
import collections
import itertools
import element
import utility
import groups

try:
    xrange
except NameError:
    xrange = range

# Reference:
# https://cs231n.github.io/neural-networks-3/#gradcheck

class Vector(tuple):
    """ Make vector operations cleaner """
    __slots__ = ()
    def __new__(cls, *pos):
        return tuple.__new__(cls, pos[0] if len(pos) == 1 else pos)
    def dot(lhs, rhs, zip=zip):
        return sum(a*b for a,b in zip(lhs, rhs))
    def square(s):
        return s.__class__(a*a for a in s)
    def length(s):
        dot = s.dot(s)
        return dot and (dot ** -0.5) * dot
    def normalize(s):
        mag = s.length()
        return s.__class__(mag and a/mag for a in s)
    def sqrt(s):
        return s.__class__(a if a <=0 else (a ** -0.5)*a for a in s)
    def __add__(lhs, rhs, zip=zip):
        return lhs.__class__(a+b for a,b in zip(lhs, rhs))
    def __radd__(s, lhs):
        return s.__add__(lhs)
    def __sub__(s, rhs, rev=False, zip=zip):
        return s.__class__(a-b for a,b in zip(*(rhs, s) if rev else (s, rhs)))
    def __rsub__(s, lhs):
        return s.__sub__(s, lhs, True)
    def __div__(s, rhs, rev=False, zip=zip):
        return s.__class__(b and a/b for a,b in zip(*(rhs, s) if rev else (s, rhs)))
    def __rdiv__(s, lhs):
        return s.__sub__(s, lhs, True)
    def __truediv__(s, rhs):
        return s.__div__(rhs)
    def __rtruediv__(s, lhs):
        return s.__div__(lhs, True)
    def __mul__(s, rhs, rev=False):
        lhs, rhs = (rhs, s) if rev else (s, rhs)
        try: # Scalar
            return s.__class__(a*rhs for a in lhs)
        except TypeError: # Dot product
            return s.dot(rhs)
    def __rmul__(s, lhs):
        return s.__mul__(lhs, True)

def form_heirarchy(grps):
    """ Sort groups into an efficient heirarchy """
    cache_dist = {g: g.get_distance() for g in grps} # Keep track of distance values
    sorted_grp = list(grps) # Our list of groups in sorted order
    child_grp = collections.defaultdict(list) # Groups with relation to their children
    precision_move = 0.0001
    precision_check = 0.000000001

    # Check all groups
    for grp1 in grps:
        grp1.shift(precision_move) # Move values slightly
        for grp2 in grps: # Check what happened because of this
            dist = grp2.get_distance()
            diff = abs(dist - cache_dist[grp2])
            if diff > precision_check:
                if grp2 is not grp1: # Don't add self as child of self
                    child_grp[grp1].append(grp2)
            cache_dist[grp2] = dist
        if child_grp[grp1]: # We have some children to sort through
            for i, child in enumerate(sorted_grp):
                if child is grp1:
                    break
                if child in child_grp[grp1]: # Find earliest child and swap positions
                    sorted_grp.remove(grp1)
                    sorted_grp.insert(i, grp1)
                    break
    # Collect any cycles that have been dug up.
    cycles = collections.defaultdict(list)
    for parent in child_grp:
        for child in child_grp[parent]:
            if parent in child_grp[child]:
                cycles[parent].append(child)

    # If we have any cycles. Warn about them.
    if cycles:
        utility.warn("The following groups have cycle issues, and may not evaluate correctly:\n{}".format(", ".join(c.get_name() for c in cycles)))

    # Throw in duplicates for cyclic groups to ensure they get evaluated in differing orders
    new_sorted_grp = []
    for i, grp in enumerate(sorted_grp):
        new_sorted_grp.append(grp)
        if i:
            # Check if the two cyclic groups are side by side
            # TODO: Add functionality for more than two cyclic pairs (ie triplets etc)
            prev_grp = sorted_grp[i-1]
            if grp in cycles and prev_grp in cycles[grp]:
                new_sorted_grp.append(prev_grp)
    return new_sorted_grp

def search(group, rate=0.8, resistance=0.8, friction=0.9, tolerance=0.00001, limit=500, debug=False):
    """
    Match using gradient descent + momentum.
    rate = sample size of each step.
    friction = how much dampening do we get.
    limit = how many steps do we take before giving up?
    """
    # Validate some parameters
    limit = abs(int(limit))
    if resistance >= 1 or friction >= 1 or rate <= 0:
        raise RuntimeError("Variables are out of range.")


    # Initialize variables
    velocity = momentum = Vector([0]*len(group))
    prev_dist = closest_dist = group.get_distance()
    curr_values = closest_values = Vector(group.get_values())

    yield closest_dist, closest_values

    # GO!
    for i in xrange(limit):
        group.set_values(curr_values)

        # Check if we have overshot our target.
        # If so, reduce our sample rate and our momentum, so we can turn faster.
        dist = group.get_distance()
        if dist > prev_dist:
            rate *= 0.5
            resistance *= 0.5
            friction *= 0.5
            velocity *= 0.5
            momentum *= 0.5
        prev_dist = dist

        # Check if we are closer than ever before.
        # Record it if so.
        if dist < closest_dist:
            closest_dist = dist
            closest_values = curr_values
            yield closest_dist, closest_values

        # Check if we are stable enough to stop.
        # If rate is low enough we're not going to move anywhere anyway...
        if rate < tolerance:
            if debug:
                print("Rate below tolerance. Done.")
            break

        # Check if we are sitting on a flat plateau.
        gradient = Vector(group.get_gradient())
        if i and (gradient - prev_gradient).length() < 0.0000001:
            if debug:
                print("Gradient flat. Done.")
            break
        prev_gradient = gradient

        # Calculate our path
        momentum = momentum*resistance + gradient*(1-resistance)
        velocity = velocity*friction + gradient.square()*(1-friction)
        curr_values += momentum*-rate / velocity.sqrt()
        momentum = Vector(group.bounds(momentum))
        velocity = Vector(group.bounds(velocity))
        curr_values = Vector(group.bounds(curr_values))

    if debug:
        print("Finished after {} steps".format(i))
    yield closest_dist, closest_values

def match(templates, start_frame=None, end_frame=None, **kwargs):
    """
    Match groups across frames.
    update. function run updating matching progress.
    start_frame (optional). Current frame if not given.
    end_frame (optional). Single frame if not provided else the full range.
    """
    start_frame = int(utility.get_frame()) if start_frame is None else int(start_frame)
    end_frame = start_frame if end_frame is None else int(end_frame)
    end_frame += 1
    grps = form_heirarchy([groups.Group(t) for t in templates if t.enabled])
    print("Matching Groups Now!")
    print("Match order: {}".format(", ".join(a.get_name() for a in grps)))
    group_step = 1 / len(grps)

    yield 0 # Kick us off
    for i, frame in enumerate(range(start_frame, end_frame)):
        utility.set_frame(frame)
        for j, grp in enumerate(grps):
            total_dist = None
            for dist, values in search(grp, **kwargs):
                if total_dist is None:
                    total_dist = dist
                if not dist: # Break early if we're there
                    break
                progress = 1-dist/total_dist
                yield progress * group_step + j * group_step
            grp.keyframe(values)
    yield 1

def testfile(file_path):
    templates = groups.load(file_path)
    if templates:
        for _ in match(templates, debug=True):
            pass

def test2():
    import maya.cmds as cmds
    import random
    cmds.file(new=True, force=True)

    # Create two test chains
    chain1 = [cmds.joint(p=a) for a in [(1,2,3),(2,1,3),(3,2,1),(4,4,4),(2,1,3),(6,4,2)]]
    cmds.select(clear=True)
    chain2 = [cmds.joint(p=a) for a in [(2,3,4),(4,4,5),(4,5,2),(2,3,1),(4,3,1),(3,2,3)]]
    mrk = cmds.spaceLocator()[0]

    # Create some outliers
    temp = groups.Template(
        match_type=groups.POSITION,
        markers=(chain1[3], mrk),
        attributes=[(chain1[3], "tx")])

    axis = ["rx", "ry", "rz"]

    templates = [temp]
    for i in range(len(chain1)):
        if i:
            templates.append(groups.Template(
                match_type=groups.POSITION,
                markers=(chain1[i], chain2[i]),
                attributes=[(chain1[i-1], a) for a in axis]
                ))
    grps = [groups.Group(a) for a in templates]
    random.shuffle(grps) # Randomize order
    sorted_grps = form_heirarchy(grps)
    for s in sorted_grps:
        print(list(s), list(s.markers))

def test():
    import maya.cmds as cmds
    import random

    rand = lambda: tuple(random.randrange(-10,10) for _ in range(3))

    cmds.file(new=True, force=True)

    m1, _ = cmds.polySphere()
    m2 = cmds.group(em=True)
    m3 = cmds.group(m2)

    cmds.xform(m1, t=rand())
    cmds.xform(m2, t=rand())
    cmds.setAttr(m2 + ".ty", 0)
    cmds.setAttr(m1 + ".ty", -3)
    cmds.setAttr(m3 + ".scaleX", 2)
    cmds.setAttr(m3 + ".scaleZ", 6)

    template = groups.Template(
        markers=[m1, m2],
        attributes=[(m2, "tx", 0), (m2, "tz", 0)]
    )
    grp = groups.Group(template)

    curve1 = element.Curve(grp.markers.node1.get_position())
    curve2 = element.Curve(grp.markers.node2.get_position())

    for dist, values in search(grp, debug=True):
        curve1.add(grp.markers.node1.get_position())
        curve2.add(grp.markers.node2.get_position())

    grp.set_values(values)

    x1, _, z1 = cmds.xform(m1, q=True, ws=True, t=True)
    x2, _, z2 = cmds.xform(m2, q=True, ws=True, t=True)
    # print(x1, z1)
    # print(x2, z2)
    assert abs(x1-x2) < 0.01
    assert abs(z1-z2) < 0.01
