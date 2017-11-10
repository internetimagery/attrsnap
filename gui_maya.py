# Prepare and run gui!

from __future__ import print_function
import maya.cmds as cmds
import maya.mel as mel
import functools
import contextlib
import utility
import groups

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

class Widget(object):
    """ Simple widget """
    def __init__(s, widget, key):
        s.key = key
        s.widget = widget

    def validate(s, check):
        """ Check value is ok """
        if check(s.value):
            colour = BLACK
        else:
            colour = RED
        s.widget(s.gui, e=True, bgc=colour)
        return colour == BLACK

    def value():
        doc = "The value property."
        def fget(self):
            return s.widget(s.qui, q=True, **{s.key: True})
        def fset(self, value):
            s.widget(s.gui, e=True, **{s.key: value})
        return locals()
    value = property(**value())


class IntBox(Widget):
    """ Int box """
    def __init__(s, parent, update, val=0):
        s.gui = cmds.intField(v=val, p=parent, cc=update, bgc=BLACK)
        Widget.__init__(s, cmds.intField, "v")

class TextBox(Widget):
    """ Text box full of boxy text! """
    def __init__(s, parent, update, text=""):
        s.gui = cmds.textFieldGrp(tx=text, p=parent, tcc=update, bgc=BLACK)
        Widget.__init__(s, cmds.textFieldGrp, "tx")

class Attribute(object):
    """ gui for single attribute """
    def __init__(s, parent, update, attribute="", min_=None, max_=None):
        s.row = cmds.rowLayout(nc=1)
        s.attr = TextBox(s.row, update, attribute)

    def validate(s):
        """ Validate attribute exists and values are between limits """
        ok = True
        if not s.attr.validate(utility.attr_exists):
            ok = False
        return ok

class Attributes(object):
    """ Gui for attributes """
    def __init__(s, parent, update, attributes=None):
        s.parent = parent
        s.update = update
        s.attributes = [Attribute(parent, update, a) for a in attributes or []]

    def add_attribute(s, name=""):
        """ Add a new attribute """
        s.attributes.append(Attribute(s.parent, s.update, name))

    def validate(s):
        """ Validate attributes """
        ok = True
        for at in s.attributes:
            if not at.validate():
                ok = False
        return ok

class Markers(object):
    """ Gui for markers """
    def __init__(s, parent, update, m1="", m2=""):
        s.parent = cmds.columnLayout(adj=True, p=parent)
        s.m1 = TextBox(s.parent, update)
        s.m2 = TextBox(s.parent, update)
        s.validate()

    def validate(s, *_):
        """ validate all markers actually exist """
        ok = True
        for m in (s.m1, s.m2):
            if not m.validate(cmds.objExists):
                ok = False
        return ok

    def set(s, mark1, mark2):
        """ Set markers in bulk """
        s.m1.text = mark1
        s.m2.text = mark2

class Tab(object):
    """ Tab holding information! """
    def __init__(s, tab_parent, group, enabled=True):
        s.parent = tab_parent
        s.group = group
        s.layout = cmds.columnLayout(adj=True, p=s.parent)

        # Group stuff
        cmds.rowLayout(nc=2, adj=1, p=s.layout)
        s.GUI_enable = cmds.checkBox(l="Enable", v=enabled, cc=s.enable)
        cmds.optionMenu()
        cmds.menuItem(l="opt1")
        cmds.menuItem(l="other opt")
        pane = cmds.paneLayout(configuration="vertical2", p=s.layout)
        markers = cmds.columnLayout(adj=True, p=pane)
        cmds.button(l="New markers from selection", c=lambda _: s.markers.set(*utility.get_selection(2)))
        s.markers = Markers(markers, s.validate, *s.group.get_markers())
        # -----
        cmds.columnLayout(adj=True, p=pane)
        cmds.button(l="New Attribute from Channelbox")
        s.GUI_attr = cmds.scrollLayout(h=300, bgc=BLACK)
        # -----

        s.set_title(group.get_name())
        s.validate()

    def rename(s):
        """ Prompt rename """
        if cmds.promptDialog(t="Rename group", m="Name:", b=[OK, CANCEL], db=OK, cb=CANCEL, ds=CANCEL) == OK:
            text = cmds.promptDialog(q=True, tx=True).strip()
            if text:
                s.set_title(text)
                s.enable(True)

    def set_title(s, title):
        """ Set title of tab """
        s.group.set_name(title)
        cmds.tabLayout(s.parent, e=True, tl=(s.layout, title))

    def enable(s, state):
        """ Enable / disable """
        cmds.checkBox(s.GUI_enable, e=True, v=state)
        title = s.group.get_name()
        if state:
            s.set_title(title.replace("*", ""))
        else:
            s.set_title(title + "*")
        s.validate()

    def validate(s, *_):
        """ Validate all info is there """
        if cmds.checkBox(s.GUI_enable, q=True, v=True): # Check we are enabled
            if s.markers.validate():# and s.group.get_attributes():
                cmds.checkBox(s.GUI_enable, e=True, bgc=GREEN)
            else:
                cmds.checkBox(s.GUI_enable, e=True, bgc=YELLOW)
        else:
            cmds.checkBox(s.GUI_enable, e=True, bgc=RED)

    def __str__(s):
        """ Make class usable """
        return s.layout

class Window(object):
    """ Main window! """
    def __init__(s):
        # s.groups = groups.Group_Set()
        s.tabs = []
        s.group_index = 0
        name = "attrsnap"
        if cmds.window(name, q=True, ex=True):
            cmds.deleteUI(name)

        win = cmds.window(t="Attribute Snapping!")
        root = cmds.columnLayout(adj=True)
        cmds.menuBarLayout()
        cmds.menu(l="Groups")
        cmds.menuItem(l="New Group", c=s.new_group)
        cmds.menuItem(l="Load Template", c=s.load_template)
        cmds.menuItem(l="Save Template", c=s.save_template)
        s.tab_grp = cmds.tabLayout(doubleClickCommand=s.rename_tab, p=root)
        cmds.showWindow(win)

        # Initial group
        s.new_group()

    def rename_tab(s):
        """ Rename tabs on doubleclick """
        selected = cmds.tabLayout(s.tab_grp, q=True, st=True, fpn=True)
        for tab in (t for t in s.tabs if selected in t.layout):
            tab.rename()

    def new_group(s, *_):
        """ Create a new group """
        tab_names = cmds.tabLayout(s.tab_grp, q=True, tl=True) or []
        while True:
            s.group_index += 1
            name = "Group{}".format(s.group_index)
            if name not in tab_names:
                break
        group = groups.Group(name="GroupP{}".format(s.group_index))
        s.tabs.append(Tab(s.tab_grp, group))
        cmds.tabLayout(s.tab_grp, e=True, sti=cmds.tabLayout(s.tab_grp, q=True, nch=True))

    def load_template(s, *_):
        """ Load template file """
        raise NotImplementedError("Sorry... Not yet.")

    def save_template(s, *_):
        """ Save template file """
        raise NotImplementedError("Sorry... Load doesn't work! Why would this?")
