# Prepare and run gui!

from __future__ import print_function
import maya.cmds as cmds
import maya.mel as mel
import contextlib

BLACK = (0.1,0.1,0.1)
GREEN = (0.2, 0.5, 0.4)
RED = (0.4, 0.3, 0.3)
YELLOW = (0.7, 0.7, 0.1)
# L_GREEN = [a * 1.5 for a in GREEN]
# D_GREEN = [a * 0.4 for a in GREEN]
# D_RED = [a * 0.4 for a in RED]

OK = "Ok"
CANCEL = "Cancel"


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
    gMainProgressBar = maya.mel.eval('$tmp = $gMainProgressBar')
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

class Tab(object):
    """ Tab holding information! """
    def __init__(s, tab_parent, title="Group"):
        s.parent = tab_parent
        s.layout = cmds.columnLayout(adj=True, p=s.parent)

        # Group stuff
        cmds.rowLayout(nc=2, adj=1, p=s.layout)
        cmds.checkBox(l="Enable", v=True, bgc=YELLOW)
        cmds.optionMenu()
        cmds.menuItem(l="opt1")
        cmds.menuItem(l="other opt")
        pane = cmds.paneLayout(configuration="vertical2", p=s.layout)
        cmds.columnLayout(adj=True, p=pane)
        cmds.button(l="New markers from selection")
        cmds.columnLayout(adj=True, bgc=BLACK)
        cmds.text(l="Marker1")
        cmds.text(l="Marker2")
        cmds.columnLayout(adj=True, p=pane)
        cmds.button(l="New Attribute from Channelbox")
        cmds.scrollLayout(h=300, bgc=BLACK)
        cmds.text(l="Attribute!")
        cmds.text(l="Attribute!")
        cmds.text(l="Attribute!")

        s.set_title(title)

    def rename(s):
        """ Prompt rename """
        if cmds.promptDialog(t="Rename group", m="Name:", b=[OK, CANCEL], db=OK, cb=CANCEL, ds=CANCEL) == OK:
            text = cmds.promptDialog(q=True, tx=True).strip()
            if text:
                s.set_title(text)

    def set_title(s, title):
        """ Set title of tab """
        s.title = title
        cmds.tabLayout(s.parent, e=True, tl=(s.layout, title))

    def __str__(s):
        """ Make class usable """
        return s.layout

class Window(object):
    """ Main window! """
    def __init__(s):
        s.tabs = []
        name = "attrsnap"
        if cmds.window(name, q=True, ex=True):
            cmds.deleteUI(name)

        win = cmds.window(t="Attribute Snapping!")
        cmds.columnLayout(adj=True)
        cmds.button(l="Add new group.", bgc=GREEN, c=s.new_group)
        cmds.separator()
        s.tab_grp = cmds.tabLayout(doubleClickCommand=s.rename_tab)
        for name in ["one", "two", "three"]:
            t = Tab(s.tab_grp)
            t.set_title(name)
            s.tabs.append(t)
        cmds.showWindow(win)

    def rename_tab(s):
        """ Rename tabs on doubleclick """
        selected = cmds.tabLayout(s.tab_grp, q=True, st=True, fpn=True)
        for tab in (t for t in s.tabs if selected in t.layout):
            tab.rename()

    def new_group(s, *_):
        """ Create a new group """
        pass
