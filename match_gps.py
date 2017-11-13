# Match using gps-like tracking.

# From file:
# https://github.com/gheja/trilateration.js/blob/master/trilateration.js
from __future__ import division

def div(a, b):
    return b and a / b

def sqrt(a):
    if a < 0:
        raise ValueError("value less than zero")
    return a and ((a ** -0.5) * a)

def sqr(a):
    return a * a

def norm(a):
    mag = dot(a,a)
    return sqrt(mag)

def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def vector_subtract(a, b):
    return a[0] - b[0], a[1] - b[1], a[2] - b[2]

def vector_add(a, b):
    return a[0] + b[0], a[1] + b[1], a[2] + b[2]

def vector_divide(a, b):
    return div(a[0], b), div(a[1], b), div(a[2], b)

def vector_multiply(a, b):
    return a[0] * b, a[1] * b, a[2] * b

def vector_cross(a, b):
    return a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]

def trilateration(P1, P2, P3, D1, D2, D3, return_middle=False):
    """ Estimate position of point. Given positions and distances.
    P1~3 = position vectors
    D1~3 = distance to point
    return_middle = Return middle of positions if more than one is found
    """

    # Calculate plane
    n = vector_subtract(P2, P1)
    d = norm(n)
    ex = vector_divide(n, d)

    m = vector_subtract(P3, P1)
    i = dot(ex, m)
    a = vector_subtract(m, vector_multiply(ex, i))
    ey = vector_divide(a, norm(a))
    ez = vector_cross(ex, ey)
    j = dot(ey, m)

    # Get location
    D1_sqr = sqr(D1)
    x = div((D1_sqr - sqr(D2) + sqr(d)), (2 * d))
    y = div((D1_sqr - sqr(D3) + sqr(i) + sqr(j)), (2 * j)) - div(i, j) * x

    b = D1_sqr - sqr(x) - sqr(y)

    # floating point math flaw in IEEE 754 standard
    if abs(b) < 0.0000000001:
        b = 0

    try:
        z = sqrt(b)
    except ValueError:
        return []

    a = vector_add(P1, vector_add(vector_multiply(ex, x), vector_multiply(ey, y)))
    ez_z = vector_multiply(ez, z)
    p4a = vector_add(a, ez_z)
    p4b = vector_subtract(a, ez_z)

    if z == 0 or return_middle:
        return [a]
    else:
        return (p4a, p4b)

def test():
    import maya.cmds as cmds
    import random
    import math
    import time

    s = time.time()
    failed = []
    for _ in range(100000):

        Position = lambda: [random.randrange(-10, 10) for _ in range(3)]

        emitter = Position()
        args = [Position() for _ in range(3)]
        args += [math.sqrt(sum((a-b)**2 for a,b in zip(arg, emitter))) for arg in args]

        prediction = trilateration(*args)
        if len(prediction) == 2:
            prediction = [min(prediction, key=lambda x: math.sqrt(sum((b-a)**2 for a,b in zip(x, emitter))))]
        pred = [round(b, 3) for a in prediction for b in a]
        # print "Actual position:", emitter
        # print "Predicted position:", pred
        try:
            assert emitter == pred
        except AssertionError:
            failed.append((emitter, pred))
    print "Took", time.time() - s
    print "Failed %s times" % len(failed)
    for em, pred in failed:
        print "Failed emitter:", em
        print "Failed prediction:", pred
