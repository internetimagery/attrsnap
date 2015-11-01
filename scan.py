# Check with brute force the distance of objects
import math
import time
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

class Progress(object):
    def __init__(s, title):
        s.title = title
        s.canceled = False
    def __enter__(s):
        s.win = cmds.window(t=s.title)
        cmds.columnLayout(w=200, bgc=(0.2,0.2,0.2))
        s.bar = cmds.columnLayout(w=1, h=40, bgc=(0.8,0.4,0.5))
        cmds.showWindow(s.win)
        return s
    def update(s, progress):
        if not progress: progress = 1
        if cmds.layout(s.bar, ex=True):
            cmds.columnLayout(s.bar, e=True, w=progress * 2)
        else:
            s.canceled = True
        cmds.refresh()
    def __exit__(s, *err):
        if cmds.window(s.win, ex=True): cmds.deleteUI(s.win)

with Progress("prog") as p:
    for i in range(100):
        time.sleep(0.1)
        print i
        p.update(i)
        if p.canceled: break
