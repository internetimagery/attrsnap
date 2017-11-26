# Match two objects as close together as possible using as few steps as possible (still brute force!)
from __future__ import print_function
import groups

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
        return s.__class__(lhs[i]-rhs[i] for i in range(len(lhs)))
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


def match(group, update):
    """ Match using gradient descent + momentum """
    pass

def test():
    v1 = Vector(1,2,3)
    v2 = Vector(3,2,1)
    print(v1 * v2)

#
#
#
# # https://cs231n.github.io/neural-networks-3/#gradcheck
# def test():
#     cmds.file(new=True, force=True)
#
#     m1, _ = cmds.polySphere()
#     m2 = cmds.group(em=True)
#     m3 = cmds.group(m2)
#
#     grp = groups.Group(
#         markers=(m1, m2),
#         attributes=[(m2, "translateX"), (m2, "translateZ")]
#     )
#
#     cmds.xform(m1, t=rand())
#     cmds.xform(m2, t=rand())
#     cmds.setAttr(m2 + ".ty", 0)
#     cmds.setAttr(m3 + ".scaleX", 3)
#     cmds.setAttr(m3 + ".scaleZ", 6)
#     curve = cmds.curve(p=cmds.xform(m2, q=True, ws=True, t=True))
#
#     step = 0.5
#     velocity = [0]*len(grp)
#     friction = 0.7
#     last_vals = grp.get_values()
#     last_dist = grp.get_distance()
#     i = 0
#     while step > 0.001:
#         i += 1
#
#         # Check if we overshot our target
#         # If so. Shrink our step size (because we are close),
#         # and dampen our momentum to help us turn.
#         dist = grp.get_distance()
#         if dist >= last_dist:
#             step *= 0.8
#             velocity = vMul(velocity, 0.8)
#         last_dist = dist
#
#         grp.set_values(last_vals)
#         cmds.curve(curve, a=True, p=cmds.xform(m2, ws=True, q=True, t=True))
#
#         prev_velocity = velocity
#         velocity = vSub(vMul(velocity, friction), vMul(grp.get_gradient(), step))
#         last_vals = vAdd(vMul(prev_velocity, -friction), vMul(velocity, 1+friction))
#
#     print "Found target in %s steps." % i
