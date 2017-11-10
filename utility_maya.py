# Some utility funtionality
import maya.cmds as cmds

def get_selection(num=0):
    """ Get current selection. num = expected selection number """
    sel = set(cmds.ls(sl=True) or [])
    if num and len(sel) != num:
        raise RuntimeError("Please select only {} items.".format(num))
    return sel

def attr_exists(attribute):
    """ Check attribute exists (object.attribute) """
    try:
        obj, attr = attribute.split(".")
        if cmds.attributeQuery(attr, n=obj, ex=True):
            return True
    except ValueError:
        pass
    return False
