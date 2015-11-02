# Main Window

import warn
import scan
import maya.mel as mel
import maya.cmds as cmds

scan.Timer.verbose = True

class Attr(object):
    def __init__(s, obj, attr):
        s.obj = obj
        s.attr = attr
        s.limit = [
            cmds.attributeQuery(attr, n=obj, min=True)[0] if cmds.attributeQuery(attr, n=obj, mne=True) else -9999,
            cmds.attributeQuery(attr, n=obj, max=True)[0] if cmds.attributeQuery(attr, n=obj, mxe=True) else 9999
        ]
        if "rotate" in attr:
            s.min = 0
            s.max = 359
        else:
            s.min = -999
            s.max = 999
    def min():
        def fget(s):
            return s._min
        def fset(s, v):
            if s.limit[0] < v < s.limit[1]:
                s._min = v
            else:
                s._min = s.limit[0]
        return locals()
    min = property(**min())
    def max():
        def fget(s):
            return s._max
        def fset(s, v):
            if s.limit[0] < v < s.limit[1]:
                s._max = v
            else:
                s._max = s.limit[1]
        return locals()
    max = property(**max())

class Main(object):
    def __init__(s):
        name = "AttrGUI"
        s.objs = set() # Objects
        s.attrs = {} # Attributes

        if cmds.window(name, ex=True): cmds.deleteUI(name)
        win = cmds.window(name, rtf=True, t="Attribute Snap", s=False)
        row = cmds.rowColumnLayout(nc=2)

        cmds.columnLayout(adj=True, w=120, p=row) # Buttons
        cmds.button(l="Load Object Pair", h=46, c=lambda x: warn(s.addObj))
        cmds.button(l="Load Attributes", h=46, c=lambda x: warn(s.addAttr))
        s.steps = cmds.intFieldGrp(el="Steps", v1=10, cw2=(60,60))
        cmds.button(l="Run Snap!", h=70, c=lambda x: warn(s.runScan))

        entries = cmds.columnLayout(adj=True, w=400, p=row)
        cmds.text(l="Object Pairs", h=20, p=entries)
        cmds.separator(p=entries)
        s.objWrapper = cmds.scrollLayout(p=entries, h=70, cr=True, bgc=(0.2,0.2,0.2))
        cmds.text(l="Attributes", h=20, p=entries)
        cmds.separator(p=entries)
        s.attrWrapper = cmds.scrollLayout(p=entries, h=70, cr=True, bgc=(0.2,0.2,0.2))
        cmds.showWindow(win)

    def clear(s, element):
        try: cmds.deleteUI(cmds.layout(element, q=True, ca=True))
        except RuntimeError: pass

    def addObj(s):
        sel = cmds.ls(sl=True, type="transform")
        if len(sel) == 2:
            s.objs.add(frozenset(sel))
            s.displayObj()
        else:
            raise RuntimeError, "You must select exactly two objects"

    def displayObj(s):
        s.clear(s.objWrapper)
        if s.objs:
            def addObj(o):
                cmds.rowColumnLayout(p=s.objWrapper, nc=2, cw=[(1, 20)], bgc=(0.2,0.2,0.2)) # Objects
                cmds.button(l="X", bgc=(0.4,0.4,0.4), c=lambda x: (s.objs.remove(o), s.displayObj()))
                cmds.columnLayout(adj=True)
                for a in o: cmds.text(l=a, h=20, align="left")
            for obj in s.objs:
                addObj(obj)

    def addAttr(s):
        objs = cmds.ls(sl=True, type="transform")
        if objs:
            attr = cmds.channelBox("mainChannelBox", sma=True, q=True)
            if attr:
                new = [Attr(a, cmds.attributeQuery(b, n=a, ln=True)) for a in objs for b in attr if cmds.attributeQuery(b, n=a, ex=True)]
                s.attrs.update(dict(("%s.%s" % (a.obj, a.attr), a) for a in new))
                return s.displayAttr()
        raise RuntimeError, "Nothing selected"

    def displayAttr(s):
        s.clear(s.attrWrapper)
        if s.attrs:
            def addBtn(at):
                def setmin(val): attr.min = val
                def setmax(val): attr.max = val
                attr = s.attrs[at]
                cmds.rowLayout(
                    nc=5,
                    cw=[(1,20),(2,150),(3,70),(4,60),(5,60)],
                    cal=[(1,"center"),(2,"left"),(3,"left"),(4,"center"),(5,"center")],
                    bgc=(0.15,0.15,0.15),
                    p=s.attrWrapper)
                cmds.button(l="X", h=20, bgc=(0.4,0.4,0.4), c=lambda x: (s.attrs.pop(at), s.displayAttr()))
                cmds.text(l=attr.obj)
                cmds.text(l=cmds.attributeQuery(attr.attr, n=attr.obj, nn=True))
                cmds.floatField(v=attr.min, pre=3, cc=lambda x: setmin(x))
                cmds.floatField(v=attr.max, pre=3, cc=lambda x: setmax(x))
            for k in s.attrs:
                addBtn(k)

    def runScan(s):
        if not s.objs: raise RuntimeError, "No Objects Selected"
        if not s.attrs: raise RuntimeError, "No Attributes Selected"
        slider = mel.eval("$tmp = $gPlayBackSlider")
        if cmds.timeControl(slider, q=True, rangeVisible=True):
            framerange = cmds.timeControl(slider, q=True, rangeArray=True)
        else:
            framerange = [cmds.currentTime(q=True)]*2
        steps = cmds.intFieldGrp(s.steps, q=True, v1=True)
        attributes = dict((a, [b.min, b.max]) for a, b in s.attrs.items())
        if 3 < len(attributes):
            if "Yes" != cmds.confirmDialog(
                t="Quick Check",
                m="The more attributes you add the longer the snap will take.\nAre you sure you wish to continue?",
                button=["Yes", "No"],
                defaultButton="Yes",
                cancelButton="No",
                dismissString="No"
                ):
                return
        if 1 < len(s.objs):
            if "Yes" != cmds.confirmDialog(
                t="Quick Check",
                m="Using more than one object pair is somewhat experimental.\nAre you sure you wish to continue?",
                button=["Yes", "No"],
                defaultButton="Yes",
                cancelButton="No",
                dismissString="No"
                ):
                return
        print "-"*20
        print "Running scan:"
        print "Frames: %s" % framerange
        print "Steps: %s" % steps
        print "-"*20
        scan.Snap(attributes, s.objs, framerange, steps)
