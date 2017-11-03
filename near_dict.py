# Dict that takes vectors as keys and gets values based on nearest key.
from __future__ import print_function, division
import math

def distance(vec1, vec2):
    return math.sqrt(sum((b - a)**2 for a, b in zip(vec1, vec2)))

class Dict(dict):
    def near(s, *vec):
        """ Return nearest keys value. """
        nearest = [(distance(vec, a), b) for a, b in s.items()]
        scale = 1 / sum(a for a, b in nearest)
        return sum(a * scale * b for a, b in nearest)
