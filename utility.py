# Importing utility functions
try:
    from utility_maya import *
except ImportError:
    raise RuntimeError("No such utility class")
#
# from __future__ import division
# import maya.cmds as cmds
# import math
#
# # def distance(obj1, obj2):
# #     try:
# #         pos1 = cmds.xform(obj1, q=True, t=True, ws=True, rp=True)
#
# # rotate pivot?
#
# def distance(obj1, obj2):
#     return math.sqrt(sum((b-a)**2 for a, b in zip(obj1, obj2)))
#
# def test(ctrl=None, obj1=None, obj2=None, attrs=[]):
#     prec = 10
#     c = cmds.xform(obj2, q=True, ws=True, t=True)
#     if not attrs:
#         attrs = cmds.listAttr(ctrl, k=True)
#     for attr in attrs:
#         if cmds.objExists(ctrl + "." + attr):
#             sDist = distance(obj1, obj2)
#             val = cmds.getAttr(ctrl + "." + attr)
#             a = cmds.xform(obj1, q=True, ws=True, t=True)
#             try:
#                 cmds.setAttr(ctrl + "." + attr, val + 1.0 / prec)
#             except:
#                 cmds.setAttr(ctrl + "." + attr, val - 1.0 / prec)
#
#             b = cmds.xform(obj1, q=True, ws=True, t=True)
#             n = [b[i] - a[i] for i in range(3)]
#             d = math.sqrt(sum(z**2 for z in n))
#             nPow = sum(z for z in n)
#             if not d==0 and not nPow==0:
#                 l = (c[0]*n[0] + c[1]*n[1] + c[2]*n[2] - a[0]*n[0] - a[1]*n[1] - a[2]*n[2])/nPow
#                 x = [a[i]+n[i] * l for i in range(3)]
#                 t= math.sqrt(sum((x[i]-b[i])**2 for i in range(3)))
#                 m = [x[i]-x[i] for i in range(3)]
#                 p = n[0]*m[0] + n[1]*m[1] + n[2]*m[2]
#                 if not p==0
#                     p = p/abs(p)
#                 setVal = val + t / d * p / prec
#                 if cmds.listAttr(ctrl + "." + attr, ud=True):
#                     minVal = cmds.addAttr(ctrl + "." + attr, q=True, min=True)
#                     maxVal = cmds.addAttr(ctrl + "." + attr, q=True, max=True)
#                     if minVal and setVal < minVal:
#                         setVal = minVal
#                     elif maxVal and setVal > maxVal:
#                         setVal = maxVal
#                 try:
#                     cmds.setAttr(ctrl + "." + attr, setVal)
#                 except:
#                     pass
#
#                 # If not closer, reset
#                 eDist = distance(obj1, obj2)
#                 if eDist > sDist:
#                     cmds.setAttr(ctrl + "." + attr, val)
#             else:
#                 # Back to original
#                 cmds.setAttr(ctrl + "." + attr, val)
