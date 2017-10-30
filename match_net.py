# Perform a match by broadly casting a net. Then within that net, getting finer and finer detailself.
from __future__ import print_function
import itertools
import task





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


get ranges and divide into steps.







def set_attributes():
    """ Set attributes through all combinations. """
    pass

def match(group):
    """ Cast a wide net. Slowly narrow down after the fact """
    resolution = 11 # Number if times to divide our attributes
    att_start = [a.min for a in group.attributes] # Get our starting location
    att_step = [(a.max - a.min) / resolution for a in group.attributes]
    queue = task.Task()
    queue.add(att_start, group.get_distance()) # Kick us off
    seen = set()
    for i in range(5): # Lopo over and over!
        movement = itertools.product(*itertools.tee(range(resolution + 1),len(att_step))) # Bunch of combinations
        attr_start = queue.get()
        for move in zip(att_start, att_step, movement):
            pos = [step * mov + start for start, step, mov in move]
            if pos not in seen:
                group.set_values(pos)
                dist = group.get_distance()
                queue.add(pos, dist)

        # TODO: DO STUFF

        pass



    chunks = 11 # Number of chunks to split range into
    chunk_scale = 1 / chunks
    attr_chunks = [(a.max - a.min) * chunk_scale for a in group.attributes]
    for i in range(chunks + 1) * chunks:



                        for i in range(moves): # Expected iteration ammount.
                                with Timer("Running Scan"):
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


def chunks(range_, steps):
    """ Split range into usable chunks """
    if steps < 3: raise RuntimeError, "Step Size is too low"
    scale = (range_[1] - range_[0]) * (1.0 / (steps - 1.0))
return [a * scale + range_[0] for a in range(steps)]
