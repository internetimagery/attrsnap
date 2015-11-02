# Check with brute force the distance of objects
import math
import maya.cmds as cmds

def distance(locs):
    """ Calculate Distances """
    pos = [[cmds.xform(b, q=True, t=True) for b in a] for a in locs]
    return sum([ math.sqrt(sum([(a[0][b] - a[1][b]) ** 2 for b in range(3)])) for a in pos])

def chunks(range_, steps):
    """ Split range into usable chunks """
    if steps < 3: raise RuntimeError, "Step Size is too low"
    scale = (range_[1] - range_[0]) * (1.0 / (steps - 1.0))
    return [a * scale + range_[0] for a in range(steps)]

def position(movement, callback, keys=None, index=0, pos=None):
    """ Position attributes in all combinations """
    if not keys: keys = movement.keys() # Iterate in a specific order
    if not pos: pos = {} # Save a snapshot of where we are
    if index < len(keys):
        attr = keys[index]
        positions = movement[attr]
        numPositions = len(positions)
        for i in range(numPositions):
            v2 = positions[i]
            if not i: # Start
                v1 = v2
            else:
                v1 = positions[i - 1]
            try:
                v3 = positions[i + 1]
            except IndexError:
                v3 = v2
            if 0.002 < v3 - v1: # Cut off if the distance is so small it's neglidgable
                cmds.setAttr(attr, v2)
            pos[attr] = [v1, v3]
            position(movement, callback,
                keys=keys,
                index=index + 1,
                pos=pos
                )
    else:
        callback(pos)

class AutoKey(object):
    """ Turn off Autokey """
    def __enter__(s):
        s.state = cmds.autoKeyframe(q=True, st=True)
        cmds.autoKeyframe(st=False)
    def __exit__(s, *err):
        cmds.autoKeyframe(st=s.state)

class Progress(object):
    """ Display Progress """
    def __init__(s, title):
        s.title = title
        s.canceled = False
        s._progress = 1
    def __enter__(s):
        s.win = cmds.window(t=s.title)
        cmds.columnLayout(w=200, bgc=(0.2,0.2,0.2))
        s.bar = cmds.columnLayout(w=1, h=40, bgc=(0.8,0.4,0.5))
        cmds.showWindow(s.win)
        cmds.refresh()
        return s
    def __exit__(s, *err):
        if cmds.window(s.win, ex=True): cmds.deleteUI(s.win)
    def progress():
        def fget(s):
            return s._progress
        def fset(s, v):
            if v < 0:
                v = 1
            elif 100 < v:
                v = 100
            if cmds.layout(s.bar, ex=True):
                if int(v) is not int(s._progress) and not int(v) % 10 and 1 < v < 100: # Update on incriments of 15
                    cmds.columnLayout(s.bar, e=True, w=s._progress * 2)
                    cmds.refresh()
            else:
                s.canceled = True
            s._progress = v
        return locals()
    progress = property(**progress())

class Marker(object):
    """ Mark Objects """
    def __init__(s, objs):
        s.objs = objs
    def __enter__(s):
        s.locators = dict((c, cmds.spaceLocator()[0]) for c in set(b for a in s.objs for b in a))
        for a, b in s.locators.items(): cmds.pointConstraint(a, b)
        return [[s.locators[b] for b in a] for a in s.objs]
    def __exit__(s, *err):
        for a, b in s.locators.items():
            if cmds.objExists(b): cmds.delete(b)

class Undo(object):
    """ Turn off Undo """
    def __enter__(s): cmds.undoInfo(openChunk=True)
    def __exit__(s, *err):
        cmds.undoInfo(closeChunk=True)
        if err[0]: cmds.undo()

def Snap(attrs, objs, frames, steps=10):
    steps = int(steps)
    # Estimate number of combinations
    longest = max([b[1] - b[0] for a, b in attrs.items()]) # Get widest range
    for moves in range(100):
        longest = (longest / (steps + 1)) * 2
        if longest < 0.001:
            break
    moves += 1 # Number of moves it takes to shrink longest range to zero
    moves *= 2 # Lets beef it up a bit for accuracy.
    cmb = steps ** len(attrs) # Number of combinations per move
    frameRange = int(frames[1] - frames[0]) + 1
    progStep = 100.0 / (moves * cmb * frameRange) # Ammount to step each time in progress
    # Run Through
    with Undo(): # Turn off Undo
        with AutoKey(): # Turn off Autokey
            with Marker(objs) as m: # Mark Objects
                with Progress("Snapping Objects") as prog:
                    def updateDistance(locs, pos, container):
                        if prog.canceled: raise SystemExit, "Canceled."
                        dist = distance(locs)
                        container[dist] = pos.copy()
                        prog.progress += progStep
                    for f in range(frameRange):
                        cmds.currentTime(frames[0] + f)
                        move = attrs.copy()
                        for i in range(moves): # Expected iteration ammount.
                            dist = {} # Container to hold distances
                            move = dict((a, chunks(b, steps)) for a, b in move.items())
                            position(move, lambda x: updateDistance(m, x, dist)) # Map positions
                            minDistance = min([a for a in dist])
                            move = dist[minDistance] # Pick the shortest distance
                        # Set attribute
                        for at in move:
                            cmds.setAttr(at, (move[at][1] - move[at][0]) * 0.5 + move[at][0])
                        cmds.setKeyframe(move.keys())
                        print "Narrowed to %s." % minDistance
