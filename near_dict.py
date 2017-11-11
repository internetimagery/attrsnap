# Dict that takes vectors as keys and gets values based on nearest key.
from __future__ import print_function, division
import math
import itertools

def distance(vec1, vec2):
    return math.sqrt(sum((b - a)**2 for a, b in zip(vec1, vec2)))

class Dict(dict):
    def __init__(s, func):
        s.func = func
    def near(s, vec):
        """ Return nearest keys value. """
        func = s.func
        dist = []
        nearest = [(func(vec, a), b) for a, b in s.items()]
        # for a in itertools.permutations(nearest, 2):
            # print(a)

        scale = 1 / sum(a for a, b in nearest)
        # return sum(a * scale * b for a, b in nearest)
        return sum((1 - a * scale) * b for a, b in nearest) / sum(a for a, b in nearest)

def test():
    import random
    vector = lambda:tuple(random.randrange(-10, 10) for _ in range(3))
    d = Dict(distance)

    real_location = vector()
    test_location = vector()

    for _ in range(5):
        vec = vector()
        d[vec] = distance(vec, real_location)

    print("Expected distance:", distance(real_location, test_location))
    print("Predicted distance:", d.near(test_location))


if __name__ == '__main__':
    test()
