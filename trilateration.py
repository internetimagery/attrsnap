# From file:
# https://github.com/gheja/trilateration.js/blob/master/trilateration.js
from __future__ import division
import math
import collections

Vector = collections.namedtuple("Vector", ["x","y","z"])

def sqr(a):
    return a * a

def norm(a):
    return math.sqrt(sqr(a.x) + sqr(a.y) + sqr(a.z))

def dot(a, b):
    return a.x * b.x + a.y * b.y + a.z * b.z

def vector_subtract(a, b):
    return Vector(a.x - b.x, a.y - b.y, a.z - b.z)

def vector_add(a, b):
    return Vector(a.x + b.x, a.y + b.y, a.z + b.z)

def vector_divide(a, b):
    return Vector(a.x / b, a.y / b, a.z / b)

def vector_multiply(a, b):
    return Vector(a.x * b, a.y * b, a.z * b)

def vector_cross(a, b):
    return Vector(
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0])

def trilateration(p1, p2, p3, return_middle=False):
    """ p1 ~ p3 = (x, y, z, r) r = distance """

    ex = vector_divide(vector_subtract(p2, p1), norm(vector_subtract(p2, p1)))

    i = dot(ex, vector_subtract(p3, p1))
    a = vector_subtract(vector_subtract(p3, p1), vector_multiply(ex, i))
    ey = vector_divide(a, norm(a))
    ez = vector_cross(ex, ey)
    d = norm(vector_subtract(p2, p1))
    j = dot(ey, vector_subtract(p3, p1))

    x = (sqr(p1.r) - sqr(p2.r) + sqr(d)) / (2 * d)
    y = (sqr(p1.r) - sqr(p3.r) + sqr(i) + sqr(j)) / (2 * j) - (i / j) * x

    b = sqr(p1.r) - sqr(x) - sqr(y)

    # # floating point math flaw in IEEE 754 standard
    # if abs(b) < 0.0000000001:
    #     b = 0

    try:
        z = math.sqrt(b)
    except ValueError:
        # no solution found
        return None

    a = vector_add(p1, vector_add(vector_multiply(ex, x), vector_multiply(ey, y)))
    p4a = vector_add(a, vector_multiply(ez, z))
    p4b = vector_subtract(a, vector_multiply(ez, z))

    if z == 0 or return_middle:
        return a
    else:
        return (p4a, p4b)

def test():
    import maya.cmds as cmds
    import random

    Vec2 = collections.namedtuple("vec2", ["x","y","z","r"])

    failed = []
    for _ in range(100000):
        Position = lambda: [random.randrange(-10, 10) for _ in range(3)]

        emitter = Position()
        sensors = [Vec2(*p + [math.sqrt(sum((b-a)**2 for a,b in zip(p, emitter)))]) for p in (Position() for _ in range(3))]

        prediction = trilateration(*sensors, return_middle=False)
        if prediction and len(prediction) == 2:
            prediction = min(prediction, key=lambda x: math.sqrt(sum((b-a)**2 for a,b in zip(x, emitter))))
        try:
            assert emitter == [round(p, 3) for p in prediction]
        except (TypeError, AssertionError):
            failed.append((emitter, prediction))
    for em, pred in failed:
        print em, pred
        # print "Actual position:", emitter
        # print "Predicted position:", list(prediction)
