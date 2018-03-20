# Utilize some functionalities within maya
# Created By Jason Dixon. http://internetimagery.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is a labor of love, and therefore is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

import maya.cmds as cmds
import maya.mel as mel
import contextlib
import difflib
import groups

def load_prompt():
    """ Prompt for load path """
    path = cmds.fileDialog2(fm=1, ff="Snap file (*.snap)")
    return groups.load(path[0]) if path else []

def save_prompt(templates):
    """ Prompt for load path """
    path = cmds.fileDialog2(fm=0, ff="Snap file (*.snap)")
    if path:
        groups.save(templates, path[0])

def get_suggestion(word):
    """ Get suggested object names """
    return difflib.get_close_matches(word, cmds.ls())

def warn(message, popup=False):
    """ Provide a warning """
    cmds.warning(message)
    if popup:
        cmds.confirmDialog(t="Careful...", m=message)

def get_frame():
    """ Get current frame """
    return cmds.currentTime(q=True)

def set_frame(f):
    """ Move to frame """
    cmds.currentTime(f)

def get_selection(num=0):
    """ Get current selection. num = expected selection number """
    sel = cmds.ls(sl=True) or []
    if num and len(sel) != num:
        raise RuntimeError("Please select exactly {} items.".format(num))
    return sel

def get_attribute():
    """ Get selected attribute from channelbox """
    return set(c+"."+cmds.attributeName(c+"."+b, l=True)
        for a in "msho"
        for b in cmds.channelBox("mainChannelBox", q=True, **{"s%sa"%a:True}) or []
        for c in cmds.channelBox("mainChannelBox", q=True, **{"%sol"%a:True})
        if cmds.attributeQuery(b, n=c, ex=True))

def valid_object(obj):
    """ Check object is valid and exists """
    return cmds.objExists(obj)

def valid_attribute(attr):
    """ Check attribute is valid and exists """
    try:
        return cmds.getAttr(attr, k=True) and not cmds.getAttr(attr, l=True)
    except ValueError:
        return False

def attribute_range(attr):
    """ Return attribute range. None = infinite """
    obj, at = attr.rsplit(".", 1)
    result = [None, None]
    if cmds.attributeQuery(at, n=obj, mne=True):
        result[0] = cmds.attributeQuery(at, n=obj, min=True)[0]
    if cmds.attributeQuery(at, n=obj, mxe=True):
        result[1] = cmds.attributeQuery(at, n=obj, max=True)[0]
    return result

def get_frame_range():
    """ Get selected region """
    slider = mel.eval("$tmp = $gPlayBackSlider") # Get timeslider
    if cmds.timeControl(slider, q=True, rangeVisible=True): # Get framerange
        return cmds.timeControl(slider, q=True, rangeArray=True)
    return []
    # return [cmds.currentTime(q=True)]*2

def get_playback_range():
    """ Get frame range from playback """
    return cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)

def frame_walk(start, end):
    """ Move along frames """
    origin = cmds.currentTime(q=True)
    for frame in range(int(start), int(end + 1)):
        cmds.currentTime(frame)
        yield frame
    cmds.currentTime(origin)

@contextlib.contextmanager
def progress():
    """ Safely run operations in the scene. Clean up afterwards if errors occurr """

    def update(val):
        """ Update progress. Expect value 0 ~ 1 """
        if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True):
            raise KeyboardInterrupt
        cmds.progressBar(gMainProgressBar, edit=True, progress=val * 100)

    err = cmds.undoInfo(openChunk=True)
    state = cmds.autoKeyframe(q=True, state=True)
    cmds.refresh(suspend=True) # Careful with this. Some depend nodes may not update as expected.
    cmds.autoKeyframe(state=False)
    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
    cmds.progressBar( gMainProgressBar,
    				edit=True,
    				beginProgress=True,
    				isInterruptable=True,
    				status='Matching ...',
    				maxValue=100 )
    try:
        yield update
    except KeyboardInterrupt:
        pass
    except Exception as err:
        raise
    finally:
        cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
        cmds.autoKeyframe(state=state)
        cmds.refresh(suspend=False)
        cmds.undoInfo(closeChunk=True)
        if err:
            cmds.undo()
