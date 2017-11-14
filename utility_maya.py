# Some utility funtionality
import maya.cmds as cmds

def get_selection(num=0):
    """ Get current selection. num = expected selection number """
    sel = set(cmds.ls(sl=True) or [])
    if num and len(sel) != num:
        raise RuntimeError("Please select only {} items.".format(num))
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
