# Check with brute force the distance of objects
import math
import maya.cmds as cmds
from pprint import pprint

def distance(objs):
    pos = [[cmds.xform(b, q=True, ws=True, t=True) for b in a] for a in objs]
    return math.sqrt(sum([(a[0][b] - a[1][b])**2 for a in pos for b in range(3)]))

class AutoKey(object):
    def __enter__(s):
        s.state = cmds.autoKeyframe(q=True, st=True)
        cmds.autoKeyframe(st=False)
    def __exit__(s, *err):
        cmds.autoKeyframe(st=s.state)
