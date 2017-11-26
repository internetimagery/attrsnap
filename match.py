# Match two objects as close together as possible using as few steps as possible (still brute force!)
from __future__ import print_function
import groups

try:
    xrange
except NameError:
    xrange = range

# Reference:
# https://cs231n.github.io/neural-networks-3/#gradcheck

DEBUG = True

class Curve(object):
    def __init__(s, point):
        """ Path tool for debugging """
        from maya.cmds import curve
        s.func = curve
        s.curve = curve(p=point)
    def add(s, point):
        s.func(s.curve, a=True, p=point)

class Vector(tuple):
    """ Abstract vector class """
    __slots__ = ()
    def __new__(cls, *pos):
        return tuple.__new__(cls, pos[0] if len(pos) == 1 else pos)
    def dot(lhs, rhs):
        return sum(lhs[i]*rhs[i] for i in range(len(lhs)))
    def length(s):
        dot = s.dot(s)
        return dot and (dot ** -0.5) * dot
    def normalize(s):
        mag = s.length()
        return Vector(mag and a/mag for a in s)
    def __add__(lhs, rhs):
        return lhs.__class__(lhs[i]+rhs[i] for i in range(len(lhs)))
    def __radd__(s, lhs):
        return s.__add__(lhs)
    def __sub__(s, rhs, rev=False):
        lhs, rhs = (rhs, s) if rev else (s, rhs)
        return s.__class__(lhs[i]-rhs[i] for i in range(len(s)))
    def __rsub(s, lhs):
        return s.__sub__(s, lhs, True)
    def __mul__(s, rhs, rev=False):
        lhs, rhs = (rhs, s) if rev else (s, rhs)
        try: # Scalar
            return s.__class__(a*rhs for a in lhs)
        except TypeError: # Dot product
            return s.dot(rhs)
    def __rmul__(s, lhs):
        return s.__mul__(lhs, True)

def match(group, rate=0.5, friction=0.3, tolerance=0.01, limit=500):
    """
    Match using gradient descent + momentum.
    rate = sample size of each step.
    friction = how much dampening do we get.
    tolerance = how small an incriment before we stop?
    limit = how many steps do we take before giving up?
    """
    # Validate parameters
    if rate <= 0:
        raise RuntimeError("Rate needs to be greater than zero.\nValue was {}".format(rate))
    if friction < 0 or friction > 1:
        raise RuntimeError("Friction must be between 0 and 1.\nValue was {}".format(friction))
    friction = 1 - friction
    if tolerance <= 0:
        raise RuntimeError("Tolerance needs to be greater than zero.\nValue was {}".format(rate))
    limit = abs(int(limit))

    # Initialize variables
    velocity = Vector([0]*len(group))
    prev_dist = closest_dist = group.get_distance()
    curr_values = closest_values = Vector(group.get_values())

    if DEBUG:
        curve1 = Curve(group.markers.node1.get_position())
        curve2 = Curve(group.markers.node2.get_position())

    # GO!
    for i in xrange(limit):
        group.set_values(curr_values)

        if DEBUG:
            curve1.add(group.markers.node1.get_position())
            curve2.add(group.markers.node2.get_position())

        # Check if we have overshot our target.
        # If so, reduce our sample rate because we are close.
        # Also reduce our momentum so we can turn faster.
        dist = group.get_distance()
        if dist > prev_dist:
            rate *= 0.5
            velocity *= 0.5
        prev_dist = dist

        # Check if we are closer than ever before.
        # Record it if so.
        if dist < closest_dist:
            print("closest on ", i)
            closest_dist = dist
            closest_values = curr_values

        # Check if we are stable enough to stop.
        if rate < tolerance:
            break

        # Update our momentum
        prev_velocity = velocity
        gradient = Vector(group.get_gradient())
        velocity = velocity * friction - gradient * rate
        curr_values += prev_velocity * -friction + velocity * (1+friction)

    print("Finished after {} steps".format(i))

def test():
    import maya.cmds as cmds
    import random

    rand = lambda: tuple(random.randrange(-10,10) for _ in range(3))

    cmds.file(new=True, force=True)

    m1, _ = cmds.polySphere()
    m2 = cmds.group(em=True)
    m3 = cmds.group(m2)

    grp = groups.Group(
        markers=(m1, m2),
        attributes=[(m2, "translateX"), (m2, "translateZ")]
    )

    cmds.xform(m1, t=rand())
    cmds.xform(m2, t=rand())
    cmds.setAttr(m2 + ".ty", 0)
    cmds.setAttr(m3 + ".scaleX", 3)
    cmds.setAttr(m3 + ".scaleZ", 6)
    match(grp)
