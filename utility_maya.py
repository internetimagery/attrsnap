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
        obj, at = attr.split(".")
        return cmds.attributeQuery(at, n=obj, k=True)
    except (ValueError, TypeError, RuntimeError):
        return False
