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

    for grp in grps:
        # Move values slightly
        grp.set_values(a+precision for a in grp.get_values())
        # check what happened because of this
        children = []
        for g in grps:
            dist = g.get_distance()
            if dist != cache_dist[g]:
                children.append(g)
                cache_dist[g] = dist
        if children: # We have some children to sort through
            for i, child in enumerate(sorted_grp):
                if child in children:
                    # Swap locations
                    sorted_grp.remove(grp)
                    sorted_grp.insert(i, grp)
                    break

    for g in sorted_grp:
        print list(g)



def test():
    cmds.file(new=True, force=True)

    # Create two test chains
    chain1 = [cmds.joint(p=a) for a in [(1,2,3),(2,1,3),(3,2,1),(4,4,4),(2,1,3),(6,4,2)]]
    cmds.select(clear=True)
    chain2 = [cmds.joint(p=a) for a in [(2,3,4),(4,4,5),(4,5,2),(2,3,1),(4,3,1),(3,2,3)]]

    # Create some outliers

    axis = ["rx", "ry", "rz"]

    templates = []
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
