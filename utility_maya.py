# Some utility funtionality
import maya.cmds as cmds
import maya.mel as mel
import contextlib

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
    sel = set(cmds.ls(sl=True) or [])
    if num and len(sel) != num:
        raise RuntimeError("Please select exactly {} items.".format(num))
    return sel

def get_attribute():
    """ Get selected attribute from channelbox """
    return set("{}.{}".format(o, cmds.attributeName("{}.{}".format(o, at), l=True)) for o in cmds.ls(sl=True) for at in cmds.channelBox("mainChannelBox", sma=True, q=True) or [] if cmds.attributeQuery(at, n=o, ex=True))

def valid_attribute(attr):
    """ Check attribute is valid and exists """
    try:
        return cmds.getAttr(attr, k=True) and not cmds.getAttr(attr, l=True)
    except ValueError:
        return False

def attribute_range(attr):
    """ Return attribute range. None = infinite """
    obj, at = attr.split(".")
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
