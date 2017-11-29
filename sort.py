# Sort into heirarchy
import maya.cmds as cmds
import itertools
import groups


def test():
    cmds.file(new=True, force=True)

    # Create two test chains
    chain1 = [cmds.joint(p=a) for a in [(1,2,3),(2,1,3),(3,2,1),(4,4,4)]]
    cmds.select(clear=True)
    chain2 = [cmds.joint(p=a) for a in [(2,3,4),(4,4,5),(4,5,2),(2,3,1)]]

    axis = [".rx", ".ry", ".rz"]

    templates = []
    for i in range(len(chain1)):
        if i:
            templates.append(groups.Template(
                markers=(chain1[i], chain2[i]),
                attributes=[(chain1[i-1], a) for a in axis]
                ))
    print templates
