# Dict that gets values based on nearest key.
from __future__ import print_function, division
import math

def distance(vec1, vec2):
    return math.sqrt(sum((b - a)**2 for a, b in zip(vec1, vec2)))

class Dict(dict):
    def near(s, *key):
        """ Return nearest keys value """
        # grab all nearby keys
        nearest = [(distance(key, k), v) for k, v in s.items()]
        total = sum(a[0] for a in nearest)
        scale = 1 / total
        return sum(k * scale * v for k, v in nearest)
