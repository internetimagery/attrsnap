# speed testing vector stuff
from __future__ import division
import itertools
import operator
import random
import math
import time

def dot1(lhs, rhs, sum=sum, zip=zip):
    return sum(a*b for a,b in zip(lhs, rhs))
def dot2(lhs, rhs):
    return sum(lhs[i]*rhs[i] for i in range(len(lhs)))
def dot3(lhs, rhs, sum=sum, imap=itertools.imap, mul=operator.mul):
    return sum(imap(mul, lhs, rhs))
def dot4(lhs, rhs, sum=sum, zip=zip):
    return sum(a*b for a,b in zip(lhs, rhs))

Vector = lambda: tuple(random.randrange(-100, 100) for _ in range(3))

def test():
    times = 100000
    print "Running test %s times." % times
    func = {
        "Dot1": dot1,
        "Dot2": dot2,
        "Dot3": dot3,
        "Dot4": dot4
        }
    average = {a: [] for a in func}
    for n, f in func.items():
        for _ in range(times):
            start = time.time()
            v1 = Vector()
            v2 = Vector()
            dot1(v1, v2)
            average[n].append(time.time()-start)
    for n, t in average.items():
        av = sum(t) / len(t)
        print "%s took:" % n, av
