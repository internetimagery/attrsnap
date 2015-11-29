# Move two objects as close as possible using arbirary attributes.
# Created By Jason Dixon. http://internetimagery.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import scan
import maya.mel as mel
import maya.cmds as cmds
import maya.api.OpenMaya as om

DARK = (0.2,0.2,0.2)

def ask(question, title="Quick Check..."):
    """ Simple question popup """
    if "Yes" == cmds.confirmDialog(
        t=title,
        m=question,
        button=["Yes", "No"],
        defaultButton="Yes",
        cancelButton="No",
        dismissString="No"
        ):
        return True

class Warn(object):
    def _err(s, title, message):
        cmds.confirmDialog(
            t="Uh oh... %s" % title,
            m=message
        )
    def __call__(s, *args, **kwargs):
        with s:
            if len(args) and callable(args[0]):
                return args[0](*args[1:], **kwargs)
            else:
                raise RuntimeError, "Function not provided as first argument."
    def __enter__(s):
        pass
    def __exit__(s, eType, eName, eTrace):
        if eType:
            s._err(eType.__name__, str(eName))
warn = Warn()

class Main(object):
    """ Main Window """
    def __init__(s):
        with warn:
            s.objs = objs = cmds.ls(sl=True, type="transform") or [] # Grab selection
            if len(objs) < 2: raise RuntimeError, "You must select at least two objects."

            s.attrs = set() # Empty attribute list
            # Create window
            name = "AttrSnap2Win"
            if cmds.window(name, ex=True): cmds.deleteUI(name)
            win = cmds.window(name, rtf=True, t="Attribute Snap")
            wrapper = cmds.columnLayout(adj=True)
            cmds.text("""
    <h4>Move two objects close together using arbitrary attributes.</h4>
""")
            cmds.text("""
<ul>
    <li>Select attributes in the channel box and click the button below to add them.</li>
    <li>Only pick as few attributes as nessisary.</li>
    <li>Select a time range in the timeline to scan across the entire range.</li>
</ul>
""",
                align="left",
                hl=True)
            cmds.separator()
            # Objects
            def add_obj(row, o):
                cmds.iconTextStaticLabel(
                    st="iconAndTextHorizontal",
                    i="cube.png",
                    l=o,
                    ann="""
These two objects will be moved as close as possible together.
""",
                    h=30,
                    bgc=DARK)
                cmds.iconTextButton(
                    st="iconAndTextHorizontal",
                    i="redSelect.png",
                    l="",
                    ann="""
Select this object.
""",
                    h=30,
                    bgc=DARK,
                    c=lambda: warn(cmds.select, o, r=True),
                    p=row)
            obj_wrapper = cmds.columnLayout(adj=True, bgc=DARK)
            for o in objs:
                row = cmds.rowLayout(adj=1, nc=2, p=obj_wrapper)
                add_obj(row, o)
            # Attributes
            cmds.button(l="Load Attributes", h=46, p=wrapper, c=lambda x: warn(s.add_attr))
            s.attr_wrapper = cmds.columnLayout(adj=True, p=wrapper)
            s.display_attr()
            # Run Scan
            cmds.button(l="Run Snap!", h=70, p=wrapper, c=lambda x: warn(s.run_scan))
            cmds.showWindow(win)

    def add_attr(s):
        """ Add selected attributes to list """
        objs = cmds.ls(sl=True, type="transform")
        if objs:
            attr = cmds.channelBox("mainChannelBox", sma=True, q=True)
            if attr:
                s.attrs |= set((a, cmds.attributeQuery(b, n=a, ln=True)) for a in objs for b in attr if cmds.attributeQuery(b, n=a, ex=True))
                return s.display_attr()
        raise RuntimeError, "Nothing selected"


    def display_attr(s):
        """ Update attribute display """
        try:
            cmds.deleteUI(cmds.layout(s.attr_wrapper, q=True, ca=True))
        except RuntimeError:
            pass
        def delete_attr(at):
            s.attrs.remove(at)
            s.display_attr()
        def show_attr(row, at):
            cmds.iconTextStaticLabel(
                st="iconAndTextHorizontal",
                i="attributes.png",
                l="%s.%s" % at,
                ann="""
These attributes will be used to bring the two objects close together.
""",
                h=30,
                bgc=DARK,
                p=row)
            cmds.iconTextButton(
                st="iconAndTextHorizontal",
                i="removeRenderable.png",
                l="",
                ann="""
Remove this attribute.
""",
                h=30,
                bgc=DARK,
                c=lambda: warn(delete_attr, at),
                p=row)
        win = cmds.scrollLayout(cr=True, bgc=DARK, p=s.attr_wrapper)
        for at in s.attrs:
            row = cmds.rowLayout(nc=2, adj=1, p=win)
            show_attr(row, at)

    def run_scan(s):
        """ Do the thing! """
        attrs, objs = s.attrs, s.objs
        # Valdate everything
        for o in objs:
            if not cmds.objExists(o): raise RuntimeError, "%s could not be found." % o
        if not attrs: raise RuntimeError, "No attributes provided!"
        for o, at in attrs:
            if not cmds.objExists(o): raise RuntimeError, "%s could not be found." % o
            if not cmds.attributeQuery(at, n=o, ex=True): raise RuntimeError, "%s could not be found." % at
        # Are ok to go!
        slider = mel.eval("$tmp = $gPlayBackSlider") # Get timeslider
        if cmds.timeControl(slider, q=True, rangeVisible=True): # Get framerange
            frame_start, frame_end = cmds.timeControl(slider, q=True, rangeArray=True)
        else:
            frame_start, frame_end = [cmds.currentTime(q=True)]*2

        # Alert if we have a lot of attributes
        if 3 < len(attrs) and not ask("The more attributes you add the longer the snap will take.\nAre you sure you wish to continue?"):
            return
        # Alert if the objects are starting far apart
        o1, o2 = [om.MVector(cmds.xform(o, q=True, ws=True, t=True)) for o in objs]
        if 100 < (o2 - o1).length() and not ask("The objects are starting quite far away.\nMoving them closer to start will speed up the scan.\nDo you wish to contine as is?"):
            return
        # Run scan!
        print "Starting scan..."
        path = scan.Scanner(objs, attrs)
        while frame_start <= frame_end:
            cmds.currentTime(frame_start)
            path.walk()
            frame_start += 1
        print "Scan complete."


if __name__ == '__main__':
    Main()
