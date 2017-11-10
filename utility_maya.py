# Some utility funtionality
import maya.cmds as cmds

def get_selection(num=0):
    """ Get current selection. num = expected selection number """
    sel = set(cmds.ls(sl=True) or [])
    if num and len(sel) != num:
        raise RuntimeError("Please select only {} items.".format(num))
    return sel
