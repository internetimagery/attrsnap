# Sort into heirarchy
import maya.cmds as cmds
import itertools
import groups
import random

def length(v1):
    mag2 = sum(a*a for a in v1)
    return mag2 and (mag2 ** -0.5) * mag2

def sort(grps, precision=0.001):
    """ Sort into heirarchy """
    cache_dist = {g: g.get_distance() for g in grps} # Track current distance to save on function calls
    sorted_grp = list(grps)
    child_grp = {g: [] for g in grps}
    cycles = []

    for grp in grps:
        # Move values slightly
        grp.set_values(a+precision for a in grp.get_values())
        # check what happened because of this
        for g in grps:
            dist = g.get_distance()
            if dist != cache_dist[g]:
                cache_dist[g] = dist
                if g is not grp: # Don't add self as child of self
                    child_grp[grp].append(g)
        if child_grp[grp]: # We have some children to sort through
            for child in child_grp[grp]:
                if grp in child_grp[child]: # Check for cycles where both groups have an affect on one another
                    print "CYCLE!", list(grp), list(child)
                    cycles.append((grp, child))

            for i, child in enumerate(sorted_grp):
                if child in child_grp[grp]:
                    # Swap locations
                    sorted_grp.remove(grp)
                    sorted_grp.insert(i, grp)
                    break

    for g in sorted_grp:
        print list(g), list(g.markers)

    print "cycles:", cycles



def test():
    cmds.file(new=True, force=True)

    # Create two test chains
    chain1 = [cmds.joint(p=a) for a in [(1,2,3),(2,1,3),(3,2,1),(4,4,4),(2,1,3),(6,4,2)]]
    cmds.select(clear=True)
    chain2 = [cmds.joint(p=a) for a in [(2,3,4),(4,4,5),(4,5,2),(2,3,1),(4,3,1),(3,2,3)]]
    mrk = cmds.spaceLocator()[0]

    # Create some outliers
    temp = groups.Template(
        match_type=groups.POSITION,
        markers=(chain1[3], mrk),
        attributes=[(chain1[3], "tx")])

    axis = ["rx", "ry", "rz"]

    templates = [temp]
    for i in range(len(chain1)):
        if i:
            templates.append(groups.Template(
                match_type=groups.POSITION,
                markers=(chain1[i], chain2[i]),
                attributes=[(chain1[i-1], a) for a in axis]
                ))
    grps = [groups.Group(a) for a in templates]
    random.shuffle(grps) # Randomize order
    sort(grps)
