# Testing some timing for optimal execution

import timeit
import random

import maya.cmds as cmds
import maya.api.OpenMaya as om

def random_position():
    return [random.random() * 10 - 5 for a in range(3)]

# Get attr object from freaking confusing maya api
def getPlug(obj, attr):
    sel = om.MSelectionList()
    sel.add(obj)
    obj = sel.getDependNode(0)
    func = om.MFnDependencyNode(obj)
    attr = func.attribute(attr)
    return om.MPlug(obj, attr)

# Test gathering distance between objects ::
# Setup objects in random positions
objs = ["tmp_%s" % a for a in range(2)]
for o in objs:
    if cmds.objExists(o): cmds.delete(o)
    cmds.polyCube(n=o)
    cmds.xform(o, t=random_position())

# Setup a distance node to track for us (Test2)
dist_node = "tmp_dist"
if cmds.objExists(dist_node): cmds.delete(dist_node)
dist_node = cmds.shadingNode("distanceBetween", au=True, n=dist_node)
cmds.connectAttr("%s.translate" % objs[0], "%s.point1" % dist_node, force=True)
cmds.connectAttr("%s.translate" % objs[1], "%s.point2" % dist_node, force=True)


def test1(): # Get positions using xform and MVector
    objA, objB = [om.MVector(cmds.xform(a, q=True, t=True)) for a in objs]
    return (objB - objA).length()


def test2(): # Get positions from distance node
    return cmds.getAttr("%s.distance" % dist_node)

dist_plug = getPlug(dist_node, "distance")
def test2_half(): # Get position from distance node using API
    return dist_plug.asDouble()

# Test setting and getting attributes ::

attr_name = "%s.translateX" % objs[0]
attr_plug = getPlug(objs[0], "translateX")

def test3(): # Test getting and setting attributes using cmds
    attr = cmds.getAttr(attr_name)
    cmds.setAttr(attr_name, attr)

def test4(): # Test getting and setting attributes using api
    attr = attr_plug.asDouble()
    attr_plug.setDouble(attr)


if __name__ == '__main__':
    # Now Time our tests!!

    print "Running tests. This could take a while."
    test_time = timeit.timeit(test1)
    print "Test MVector Distance complete ::", test_time
    # Test MVector Distance complete :: 55.8408849239
    test_time = timeit.timeit(test2)
    print "Test Distance Node Query complete ::", test_time
    # Test Distance Node Query complete :: 11.4106419086
    test_time = timeit.timeit(test2_half)
    print "Test Distance Node Query with API complete ::", test_time
    # Test Distance Node Query with API complete :: 0.755993127823
    test_time = timeit.timeit(test3)
    print "Test Get Set CMDS complete ::", test_time
    # Test Get Set CMDS complete :: 61.7717609406
    test_time = timeit.timeit(test4)
    print "Test Get Set API complete ::", test_time
    # Test Get Set API complete :: 8.31989216805
