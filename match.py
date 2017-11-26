# Match two objects as close together as possible using as few steps as possible (still brute force!)
from __future__ import print_function
import groups
import element

try:
    xrange
except NameError:
    xrange = range

# Reference:
# https://cs231n.github.io/neural-networks-3/#gradcheck

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

def match(group, update, rate=0.5, friction=0.3, tolerance=0.0001, limit=500, debug=False):
    """
    Match using gradient descent + momentum.
    rate = sample size of each step.
    friction = how much dampening do we get.
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
    velocity = prev_gradient = Vector([0]*len(group))
    root_dist = prev_dist = closest_dist = group.get_distance()
    curr_values = closest_values = Vector(group.get_values())

    if debug:
        curve1 = element.Curve(group.markers.node1.get_position())
        curve2 = element.Curve(group.markers.node2.get_position())

    # GO!
    for i in xrange(limit):
        group.set_values(curr_values)

        if debug:
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
            closest_dist = dist
            closest_values = curr_values
            update(dist and dist/root_dist)

        # Check if we are stable enough to stop.
        if rate < tolerance:
            print("Rate below tolerance. Done.")
            break

        # Check if we are sitting on a flat plateau.
        gradient = Vector(group.get_gradient())
        if (gradient - prev_gradient).length() < tolerance:
            print("Gradient flat. Done.")
            break
        prev_gradient = gradient

        # Update our momentum
        prev_velocity = velocity
        velocity = velocity * friction - gradient * rate
        curr_values += prev_velocity * -friction + velocity * (1+friction)

    print("Finished after {} steps".format(i))
    return closest_values

def test():
    import maya.cmds as cmds
    import random

    def say(m):
        print("closest:", m)

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
    grp.set_values(match(grp, say, debug=True))

    x1, _, z1 = cmds.xform(m1, q=True, ws=True, t=True)
    x2, _, z2 = cmds.xform(m2, q=True, ws=True, t=True)
    print(x1, z1)
    print(x2, z2)
    assert abs(x1-x2) < 0.01
    assert abs(z1-z2) < 0.01
