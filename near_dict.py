# Dict that takes vectors as keys and gets values based on nearest key.
from __future__ import print_function, division
import math
import itertools


# TODO: Take X number of closest points
# TODO: Triangulate (multilateration) the predicted vector position
# TODO: Work out a vector that points to that from our prediction
# TODO: Return vector. So we can use it to make a step in that direction.

def distance(vec1, vec2):
    return math.sqrt(sum((b - a)**2 for a, b in zip(vec1, vec2)))

class Dict(dict):
    def __init__(s, func):
        s.func = func
    def near(s, vec):
        """ Return nearest keys value. """
        func = s.func
        nearest = [(func(vec, a), b) for a, b in s.items()]
        dist = []
        for a, b in nearest:
            scale = (1 / b) if b else 0
            dist.append(a * scale * b)

        return sum(dist) / len(dist)

        scale = 1 / sum(a for a, b in nearest)
        # for a, b in nearest:
        #     print(a * scale, 1 - a * scale)
        #     print(b, a * scale * b, (1 - a * scale) * b)
        #     print("-"*20)
        total = sum(b for a,b in nearest) / len(nearest)
        print(total)
        return sum(a * scale * b for a, b in nearest)
        # return sum((1 - a * scale) * b for a, b in nearest)
        dist = []
        for (dist1, val1), (dist2, val2) in itertools.permutations(nearest, 2):
            inv = 1 / (dist1 + dist2)
            dist.append((1 - (dist1 * inv)) * val1 + (1 - (dist2 * inv)) * val2)
        return sum(dist) / len(dist)


def test():
    import random
    vector = lambda:tuple(random.randrange(-100, 100) for _ in range(3))
    result = []
    for _ in range(20):
        d = Dict(distance)

        real_location = vector()
        test_location = vector()
        real_distance = distance(real_location, test_location)
        print("Real distance:", real_distance)

        for _ in range(5):
            vec = vector()
            d[vec] = distance(vec, real_location)

        pred_distance = d.near(test_location)
        # print("Expected:", real_distance, "Got:", pred_distance)
        result.append((real_distance, pred_distance))
    real_total = sum(a for a,b in result)
    pred_total = sum(b for a,b in result)
    scale = 1 / real_total
    # print(scale * pred_total)
    print("Accuracy:", (real_total - abs(real_total - pred_total)) / real_total)



if __name__ == '__main__':
    test()
