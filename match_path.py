# Prediction based on paths

from __future__ import print_function, division
import itertools
import groups

import maya.cmds as cmds


def distance(point1, point2):
    """ Distance between two points """
    return math.sqrt(sum((b - a) ** 2 for a, b in zip(point1, point2)))


def movement(num):
    combo = [(0,1) * num]
    return itertools.product(*combo)


def match(group):
    """ Run through and match things! """
    root_values = last_values = group.get_values()
    root_distance = last_distance = group.get_distance()
    calibration = [1] * len(group)
    trail = [root_values]gczv
    for i in range(1):
        for i, move in enumerate(movement(len(group))):
            group.set_values(move)
            dist = group.last_distance()
            magnitude = dist - last_distance
            normalized = [a / magnitude if a else 0 for a in move]
            prediction = [a * dist for a in normalized]
            cmds.locator(p=prediction)
