# Testing some stuff
from __future__ import division

# ANOTHER CANDIDATE
# https://en.wikipedia.org/wiki/Gauss%E2%80%93Newton_algorithm#Description

# https://github.com/zwigglers/multilateration/tree/master/doc

import maya.api.OpenMaya as om
import random

Vector = lambda: om.MVector(*(random.randrange(-10, 10) for _ in range(3)))

# https://github.com/gheja/trilateration.js/blob/master/trilateration.js

# https://github.com/noomrevlis/trilateration
# https://github.com/paulhayes/MultilaterationExample
# https://github.com/kim74/multilateration/blob/master/Multilateration.py
# https://stackoverflow.com/questions/16176656/trilateration-and-locating-the-point-x-y-z
# https://en.wikipedia.org/wiki/Trilateration
def test():
    position = Vector()

    P1, P2, P3 = (Vector() for _ in range(3))

    Ex = (P2 - P1) * (1 / (P2 - P1).length()) # Unit vector in direction P1 to P2
    i = Ex * (P3 - P1) # Signed magnitude of x component.
    Ey = (P3 - P1 - Ex*i) * (1 / (P3 - P1 - Ex*i).length()) # Unit vector in y direction.
    Ez = Ex ^ Ey
    d = (P2 - P1).length()
    j = Ey * (P3 - P1)

    print P1.length()
    print
    print d, j
