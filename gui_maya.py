# Prepare and run gui!

from __future__ import print_function, division
import maya.utils as utils
import maya.cmds as cmds
import maya.mel as mel
import collections
import functools
import threading
import utility
import groups
import match
import time

SEM = threading.BoundedSemaphore(1)
WIDGET_HEIGHT = 30

BLACK = (0.1,0.1,0.1)
GREEN = (0.2, 0.5, 0.4)
RED = (0.4, 0.3, 0.3)
YELLOW = (0.7, 0.7, 0.1)
GREY = (0.2,0.2,0.2)
# L_GREEN = [a * 1.5 for a in GREEN]
# D_GREEN = [a * 0.4 for a in GREEN]
# D_RED = [a * 0.4 for a in RED]

OK = "Ok"
CANCEL = "Cancel"

options = collections.OrderedDict()
options["Position"] = groups.POSITION
options["Rotation"] = groups.ROTATION


class Widget(object):
    """ Simple widget """
    def __init__(s, widget, key, *args, **kwargs):
        s.gui = widget(*args, **kwargs)
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
        def fget(s):
            return s.widget(s.gui, q=True, **{s.key: True})
        def fset(s, value):
            s.widget(s.gui, e=True, **{s.key: value})
        return locals()
    value = property(**value())

class IntBox(Widget):
    """ Int box """
    def __init__(s, parent, update, val=0):
        Widget.__init__(s, cmds.intField, "v", v=val, p=parent, cc=update, w=50, bgc=BLACK, h=WIDGET_HEIGHT)

class CheckBox(Widget):
    """ Int box """
    def __init__(s, parent, update, val=True):
        Widget.__init__(s, cmds.checkBox, "v", v=val, p=parent, cc=update, bgc=BLACK)

class IconCheckBox(Widget):
    """ Checkbox with image! """
    def __init__(s, parent, update, val=False, **kwargs):
        Widget.__init__(s, cmds.iconTextCheckBox, "v", cc=update, **kwargs)

class TextBox(Widget):
    """ Text box full of boxy text! """
    def __init__(s, parent, update, text=""):
        Widget.__init__(s, cmds.textFieldGrp, "tx", tx=text, p=parent, tcc=update, bgc=BLACK, h=WIDGET_HEIGHT)

class Attribute(object):
    """ gui for single attribute """
    def __init__(s, cols, update, delete, attribute="", min_=-9999, max_=9999):
        s.attr = TextBox(cols[0], update, attribute)
        if utility.valid_attribute(attribute):
            limit = utility.attribute_range(attribute)
            if limit[0] is not None:
                min_ = limit[0]
            if limit[1] is not None:
                max_ = limit[1]
        s.min = IntBox(cols[1], update, min_)
        s.max = IntBox(cols[2], update, max_)
        s.trash = cmds.iconTextButton(p=cols[3], i="removeRenderable.png", st="iconOnly", c=delete, h=WIDGET_HEIGHT)

    def validate(s):
        """ Validate attribute exists and values are between limits """
        ok = True
        if s.attr.validate(utility.valid_attribute):
            min_, max_ = utility.attribute_range(s.attr.value)
            if min_ is not None and not s.min.validate(lambda x: min_ <= x and x < s.max.value):
                ok = False
            if max_ is not None and not s.max.validate(lambda x: max_ >= x and x > s.min.value):
                ok = False
        else:
            ok = False
        return ok

    def export(s):
        """ Return representation of data """
        return s.attr.value, s.min.value, s.max.value

    def remove(s):
        """ Remove element """
        cmds.deleteUI([s.trash, s.attr.gui, s.min.gui, s.max.gui])

class Attributes(object):
    """ Gui for attributes """
    def __init__(s, parent, update, attributes=None):
        s.update = update
        columns = ["Name", "Min", "Max", ""]
        rows = cmds.rowLayout(nc=len(columns), adj=1, p=parent)
        s.cols = []
        for col in columns:
            c = cmds.columnLayout(adj=True, p=rows)
            cmds.text(l=col, p=c, bgc=GREY)
            s.cols.append(c)
        s.attributes = []
        for attr in attributes or []:
            name = ".".join(attr[:2])
            args = [name] + attr[2:]
            s.add_attribute(*args)

    def add_attribute(s, name, min_=-9999, max_=9999):
        """ Add a new attribute """
        for attr in s.attributes:
            if name == attr.attr.value:
                return
        attr = Attribute(s.cols, s.update, functools.partial(s.del_attribute, name), name, min_, max_)
        s.attributes.append(attr)

    def del_attribute(s, name):
        """ Remove attribute! """
        to_remove = [(i, a) for i, a in enumerate(s.attributes) if a.attr.value == name]
        for i, attr in to_remove:
            del s.attributes[i]
            attr.remove()

    def validate(s):
        """ Validate attributes """
        ok = True
        for at in s.attributes:
            if not at.validate():
                ok = False
        return ok

    def export(s):
        """ Send out attributes """
        for at in s.attributes:
            attr, min_, max_ = at.export()
            yield attr.split(".") + [min_, max_]

class Markers(object):
    """ Gui for markers """
    def __init__(s, parent, update, markers):
        s.parent = cmds.columnLayout(adj=True, p=parent)
        s.m1 = TextBox(s.parent, update)
        s.m2 = TextBox(s.parent, update)
        for m, gui in zip(markers, [s.m1, s.m2]):
            gui.value = m
        s.validate()

    def validate(s, *_):
        """ validate all markers actually exist """
        ok = True
        m1 = s.m1.validate(cmds.objExists)
        m2 = s.m2.validate(cmds.objExists)
        if not m1 or not m2 or s.m1.value == s.m2.value:
            ok = False
        return ok

    def set(s, mark1, mark2):
        """ Set markers in bulk """
        s.m1.value = mark1
        s.m2.value = mark2

class Tab(object):
    """ Tab holding information! """
    def __init__(s, tab_parent, template):
        s.parent = tab_parent
        s.layout = cmds.columnLayout(adj=True, p=s.parent)
        s.ready = False

        # Group stuff
        cmds.rowLayout(nc=2, adj=1, p=s.layout)
        s.GUI_enable = cmds.checkBox(l="Enable", v=template.enabled, cc=s.enable,
        ann="Disabled groups will not be evaluated. Useful if you don't want to use a group, while not wanting to delete it.")
        s.GUI_type = cmds.optionMenu(
        ann="Matching type. Position: Moves objects closer together. Rotation: Orients objects closer together.")
        for i, opt in enumerate(options):
            cmds.menuItem(l=opt)
            if template.match_type == options[opt]:
                cmds.optionMenu(s.GUI_type, e=True, sl=i+1)
        pane = cmds.paneLayout(configuration="vertical2", p=s.layout)
        markers = cmds.columnLayout(adj=True, p=pane)
        cmds.button(l="Get Snapping Objects from Selection", c=lambda _: s.markers.set(*utility.get_selection(2)),
        ann="Select two objects in the scene that you wish to be moved/rotated closer together.")
        s.markers = Markers(markers, s.validate, template.markers)
        # -----
        cmds.columnLayout(adj=True, p=pane)
        cmds.button(l="Add Attribute from Channelbox", c=lambda _: [s.attributes.add_attribute(a) for a in utility.get_attribute()],
        ann="Highlight attributes in the channelbox, and click the button to add them.")
        attributes = cmds.columnLayout(adj=True, bgc=BLACK)
        # attributes = cmds.scrollLayout(cr=True, h=300, bgc=BLACK)
        s.attributes = Attributes(attributes, s.validate, template.attributes)
        # -----

        # Pre fill information
        s.set_title(template.name)
        s.ready = True
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
        s.name = title
        cmds.tabLayout(s.parent, e=True, tl=(s.layout, title))

    def get_type(s):
        """ Get type """
        typ = cmds.optionMenu(s.GUI_type, q=True, v=True)
        return options[typ]

    def enable(s, state):
        """ Enable / disable """
        cmds.checkBox(s.GUI_enable, e=True, v=state)
        cmds.tabLayout(s.parent, e=True, tl=(s.layout, s.name + ("" if state else "*")))
        s.validate()

    def is_active(s):
        """ Return if active or not """
        return cmds.checkBox(s.GUI_enable, q=True, v=True)

    def validate(s, *_):
        """ Validate all info is there """
        ok = True
        if s.ready:
            if cmds.checkBox(s.GUI_enable, q=True, v=True): # Check we are enabled
                m_ok = s.markers.validate()
                a_ok = s.attributes.validate()
                if m_ok and a_ok:
                    cmds.checkBox(s.GUI_enable, e=True, bgc=GREEN)
                else:
                    cmds.checkBox(s.GUI_enable, e=True, bgc=RED)
                    ok = False
            else:
                cmds.checkBox(s.GUI_enable, e=True, bgc=YELLOW)
        return ok

    def export(s):
        """ Export information into a clean group from gui """
        name = s.name
        match_type = s.get_type()
        markers = [s.markers.m1.value, s.markers.m2.value]
        attributes = list(s.attributes.export())
        return groups.Template(
            enabled=s.is_active(),
            name=name,
            match_type=match_type,
            markers=markers,
            attributes=attributes)

    def __str__(s):
        """ Make class usable """
        return s.layout

class Range(object):
    """ Frame range widget """
    def __init__(s, parent):
        s.row = cmds.rowLayout(nc=2, p=parent)
        col = cmds.columnLayout(p=s.row)
        s.dynamic = IconCheckBox(col, lambda x: "", v=True,
        l="Automatic\nFrame Range:",
        i="autoload.png",
        st="iconAndTextHorizontal",
        ann="RIGHT CLICK: Additional options.\nON: Auto frame range.\nOFF: Manual.")
        cmds.popupMenu(p=col)
        cmds.menuItem(l="Set to playback range.", c=lambda x: s.set_range(*utility.get_playback_range()))
        col = cmds.columnLayout(p=s.row)
        frame = utility.get_frame()
        s.min = IntBox(col, s.validate, frame)
        s.max = IntBox(col, s.validate, frame)

        # Detect things!
        s.loop = True
        threading.Thread(target=s.inner_loop).start()

    def validate(s, *_):
        """ Validate our timeline range """
        ok = True
        if not s.min.validate(lambda x: x <= s.max.value):
            ok = False
        if not s.max.validate(lambda x: x >= s.min.value):
            ok = False
        return ok

    def set_range(s, start, end, auto=False):
        """ Set range to values """
        if auto and not s.dynamic.value:
            return
        s.dynamic.value = auto
        s.min.value = start
        s.max.value = end

    def inner_loop(s):
        """ Detect things on loop, with low priority """
        while s.loop:
            SEM.acquire()
            utils.executeDeferred(cmds.scriptJob, ro=True, e=("idle", s.update_timeline_highlight))
            time.sleep(0.3)

    def update_timeline_highlight(s):
        """ If the timeline is highlighted, update range values """
        try:
            if cmds.layout(s.row, q=True, ex=True):
                fr = utility.get_frame_range()
                if fr:
                    s.set_range(*fr, auto=True)
                else:
                    frame = utility.get_frame()
                    s.set_range(frame, frame, auto=True)
            else:
                s.loop = False
        except Exception as err:
            print("ERROR:", err)
            s.loop = False
        finally:
            SEM.release()

    def export(s):
        """ Pump out values """
        return s.min.value, s.max.value

class Window(object):
    """ Main window! """
    def __init__(s, templates=None):
        templates = templates or []
        s.idle = True
        s.tabs = []
        s.group_index = 0
        name = "attrsnap"
        if cmds.window(name, q=True, ex=True):
            cmds.deleteUI(name)

        s.win = cmds.window(t="Attribute Snapping!")
        root = cmds.columnLayout(adj=True)
        cmds.menuBarLayout()
        cmds.menu(l="Groups")
        cmds.menuItem(l="New Group", c=s.new_group,
        ann="Create a new group.")
        cmds.menuItem(l="Remove Group", c=s.delete_tab,
        ann="Remove currently visible group.")
        cmds.menuItem(d=True)
        cmds.menuItem(l="Enable All", c=lambda x: s.enable_all(True),
        ann="Enable all groups.")
        cmds.menuItem(l="Disable All", c=lambda x: s.enable_all(False),
        ann="Disable all groups.")
        cmds.menuItem(d=True)
        cmds.menuItem(l="Load Template", c=s.load_template,
        ann="Get groups from a template file.")
        cmds.menuItem(l="Save Template", c=s.save_template,
        ann="Save current groups into a template file. For later retrieval.")

        s.tab_grp = cmds.tabLayout(
            snt=True,
            newTabCommand=s.new_group,
            doubleClickCommand=s.rename_tab,
            p=root)

        cmds.separator(p=root)
        row = cmds.rowLayout(nc=2, adj=2, p=root)
        s.range = Range(row)
        cmds.button(l="-- Do it! --", h=WIDGET_HEIGHT*2, bgc=GREEN, c=s.run_match, p=row,
        ann="Click to start matching. Using all enabled groups.")
        cmds.helpLine(p=root)
        cmds.showWindow(s.win)

        # Initial group
        if templates:
            for t in templates:
                s.new_group(t)
        else:
            s.new_group()

    def enable_all(s, status=True):
        """ Enable every group """
        for tab in s.tabs:
            tab.enable(status)

    def delete_tab(s, *_):
        """ Delete active tab """
        selected = cmds.tabLayout(s.tab_grp, q=True, fpn=True, st=True)
        for i, tab in enumerate(s.tabs):
            if selected in tab.layout:
                cmds.deleteUI(tab.layout)
                del s.tabs[i]
                if not len(s.tabs):
                    s.new_group()
                return

    def rename_tab(s):
        """ Rename tabs on doubleclick """
        selected = cmds.tabLayout(s.tab_grp, q=True, st=True, fpn=True)
        for tab in (t for t in s.tabs if selected in t.layout):
            tab.rename()

    def new_group(s, template=None):
        """ Create a new group """
        if not template:
            tab_names = cmds.tabLayout(s.tab_grp, q=True, tl=True) or []
            while True:
                s.group_index += 1
                name = "Group{}".format(s.group_index)
                if name not in tab_names:
                    break
            template = groups.Template(name="Group{}".format(s.group_index))
        s.tabs.append(Tab(s.tab_grp, template))
        cmds.tabLayout(s.tab_grp, e=True, sti=cmds.tabLayout(s.tab_grp, q=True, nch=True))

    def load_template(s, *_):
        """ Load template file """
        path = cmds.fileDialog2(fm=1, ff="Snap file (*.snap)")
        if path:
            Window(groups.load(path[0]))

    def save_template(s, *_):
        """ Save template file """
        templates = [tab.export() for tab in s.tabs]
        path = cmds.fileDialog2(fm=0, ff="Snap file (*.snap)")
        if path:
            groups.save(templates, path[0])

    def run_match(s, *_):
        """ Run match! Woot """
        if s.idle:
            s.idle = False
            valid = [tab.export() for tab in s.tabs if tab.validate() and tab.is_active()]
            num_valid = len(valid)
            if not valid:
                return
            if not s.range.validate():
                return
            frame_range = s.range.export()
            frame_diff = (frame_range[1] - frame_range[0]) + 1
            frame_scale = 1 / frame_diff
            grp_scale = 1 / num_valid

            # TODO: Put in proper matching!
            with utility.progress() as prog:
                for progress in match.match(valid, frame_range[0], frame_range[1]):
                    prog(progress)
        s.idle = True
