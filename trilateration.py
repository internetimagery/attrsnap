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
    return Vector(a.x - b.x, y: a.y - b.y, z: a.z - b.z)

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

def trilateration(p1, p2, p3, return_middle):
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

    # floating point math flaw in IEEE 754 standard
    if abs(b) < 0.0000000001:
		b = 0

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
