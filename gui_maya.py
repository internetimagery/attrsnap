# Gui stuff for use within maya
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

from __future__ import print_function, division
import maya.utils as utils
import maya.cmds as cmds
import maya.mel as mel
import collections
import functools
import threading
import utility
import os.path
import groups
import match
import time
import re

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

    def enable(s, state=True):
        """ Enable / Disable widget """
        s.widget(s.gui, e=True, en=state)

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
    def __init__(s, parent, update, val=0, **kwargs):
        Widget.__init__(s, cmds.intField, "v", v=val, p=parent, cc=update, w=50, bgc=BLACK, h=WIDGET_HEIGHT, **kwargs)

class FloatBox(Widget):
    """ Float box """
    def __init__(s, parent, update, val=0, **kwargs):
        Widget.__init__(s, cmds.floatField, "v", v=val, p=parent, cc=update, w=50, pre=2, bgc=BLACK, h=WIDGET_HEIGHT, **kwargs)

class CheckBox(Widget):
    """ Int box """
    def __init__(s, parent, update, val=True, **kwargs):
        Widget.__init__(s, cmds.checkBox, "v", v=val, p=parent, cc=update, bgc=BLACK, **kwargs)

class IconCheckBox(Widget):
    """ Checkbox with image! """
    def __init__(s, parent, update, val=False, **kwargs):
        Widget.__init__(s, cmds.iconTextCheckBox, "v", cc=update, **kwargs)

class TextBox(Widget):
    """ Text box full of boxy text! """
    def __init__(s, parent, update, text="", **kwargs):
        Widget.__init__(s, cmds.textFieldGrp, "tx", tx=text, p=parent, tcc=update, bgc=BLACK, h=WIDGET_HEIGHT, **kwargs)

class Attribute(object):
    """ gui for single attribute """
    def __init__(s, cols, update, delete, attribute="", min_=-9999, max_=9999, bias=1.0):
        s.attr = TextBox(cols[0], update, attribute)
        if utility.valid_attribute(attribute):
            limit = utility.attribute_range(attribute)
            if limit[0] is not None:
                min_ = limit[0]
            if limit[1] is not None:
                max_ = limit[1]
        s.min = FloatBox(cols[1], update, min_)
        s.max = FloatBox(cols[2], update, max_)
        s.bias = FloatBox(cols[3], update, bias)
        s.trash = cmds.iconTextButton(p=cols[4], i="removeRenderable.png", st="iconOnly", c=delete, h=WIDGET_HEIGHT)

    def validate(s):
        """ Validate attribute exists and values are between limits """
        ok = True
        if s.attr.validate(utility.valid_attribute):
            min_, max_ = utility.attribute_range(s.attr.value)
            if min_ is not None and not s.min.validate(lambda x: min_ <= x and x < s.max.value):
                ok = False
            if max_ is not None and not s.max.validate(lambda x: max_ >= x and x > s.min.value):
                ok = False
            if not s.bias.validate(lambda x: x >= 0):
                ok = False
        else:
            ok = False
        return ok

    def export(s):
        """ Return representation of data """
        return s.attr.value, s.min.value, s.max.value, s.bias.value

    def remove(s):
        """ Remove element """
        cmds.deleteUI([s.trash, s.attr.gui, s.min.gui, s.max.gui])

class Attributes(object):
    """ Gui for attributes """
    def __init__(s, parent, update, attributes=None):
        s.update = update
        columns = ["Name", "Min", "Max", "Bias", ""]
        rows = cmds.rowLayout(nc=len(columns), adj=1, p=parent)
        s.cols = []
        for col in columns:
            c = cmds.columnLayout(adj=True, p=rows)
            cmds.text(l=col, p=c, bgc=GREY)
            s.cols.append(c)
        s.attributes = []
        for attr in attributes or []:
            name = ".".join((attr["obj"], attr["attr"]))
            args = [name, attr["min"], attr["max"], attr["bias"]]
            s.add_attribute(*args)

    def add_attribute(s, name, min_=-9999, max_=9999, bias=1.0):
        """ Add a new attribute """
        for attr in s.attributes:
            if name == attr.attr.value:
                return
        attr = Attribute(s.cols, s.update, functools.partial(s.del_attribute, name), name, min_, max_, bias)
        s.attributes.append(attr)
        s.update()

    def del_attribute(s, name):
        """ Remove attribute! """
        to_remove = [(i, a) for i, a in enumerate(s.attributes) if a.attr.value == name]
        for i, attr in to_remove:
            del s.attributes[i]
            attr.remove()
        s.update()

    def validate(s):
        """ Validate attributes """
        ok = True if s.attributes else False
        for at in s.attributes:
            if not at.validate():
                ok = False
        return ok

    def export(s):
        """ Send out attributes """
        for at in s.attributes:
            attr, min_, max_, bias = at.export()
            obj, at = attr.rsplit(".", 1)
            yield {"obj":obj, "attr":at, "min":min_, "max":max_, "bias":bias}

class Markers(object):
    """ Gui for markers """
    def __init__(s, parent, update, delete, index, markers):
        s.root = cmds.rowLayout(nc=3, adj=2, p=parent)
        cmds.text(l=index, p=s.root, h=WIDGET_HEIGHT*2)
        col = cmds.columnLayout(adj=True, p=s.root)
        s.m1 = TextBox(col, update)
        s.m2 = TextBox(col, update)
        for m, gui in zip(markers, [s.m1, s.m2]):
            gui.value = m
        cmds.iconTextButton(p=s.root, i="removeRenderable.png", st="iconOnly", c=lambda: delete(s), h=WIDGET_HEIGHT*2, bgc=GREY)
        s.validate()

    def validate(s, *_):
        """ validate all markers actually exist """
        ok = True
        m1 = s.m1.validate(cmds.objExists)
        m2 = s.m2.validate(cmds.objExists)
        if not m1 or not m2 or s.m1.value == s.m2.value:
            ok = False
        return ok

    def remove(s):
        """ DESTROY MYSELF! """
        cmds.deleteUI(s.root)

    def export(s):
        """ Return information """
        return s.m1.value, s.m2.value

class Marker_List(object):
    """ Listing all marker groups """
    def __init__(s, parent, update, markers=None):
        s.root = cmds.columnLayout(adj=True, p=parent)
        s.update = update
        s.markers = [Markers(s.root, update, s.remove, i+1, a) for i, a in enumerate(markers or [])]
        s.index = len(s.markers)

    def add(s, mark1, mark2):
        """ Add markers! """
        s.index += 1
        s.markers.append(Markers(s.root, s.update, s.remove, s.index, [mark1, mark2]))
        s.update()

    def validate(s):
        """ Check all groups are ok """
        ok = True if s.markers else False
        for marker in s.markers:
            if not marker.validate():
                ok = False
        return ok

    def remove(s, element):
        """ Remove element! """
        element.remove()
        s.markers.remove(element)
        s.update()

    def export(s):
        """ Return information """
        return (a.export() for a in s.markers)

class Tab(object):
    """ Tab holding information! """
    def __init__(s, tab_parent, template):
        s.parent = tab_parent
        s.layout = cmds.formLayout(p=tab_parent)
        # s.layout = cmds.columnLayout(adj=True, p=s.parent, bgc=(1,0,0))
        s.ready = False

        # Group stuff
        row = cmds.rowLayout(nc=2, adj=1, p=s.layout)
        s.GUI_enable = cmds.checkBox(l="Enable", v=True, cc=s.enable,
        ann="Disabled groups will not be evaluated. Useful if you don't want to use a group, while not wanting to delete it.")
        s.GUI_type = cmds.optionMenu(
        ann="Matching type. Position: Moves objects closer together. Rotation: Orients objects closer together.")
        for i, opt in enumerate(options):
            cmds.menuItem(l=opt)
            if template.match_type == options[opt]:
                cmds.optionMenu(s.GUI_type, e=True, sl=i+1)
        scroll = cmds.scrollLayout(cr=True, p=s.layout)
        pane = cmds.paneLayout(configuration="vertical2", p=scroll)
        # pane = cmds.paneLayout(configuration="vertical2", p=s.layout)
        markers = cmds.columnLayout(adj=True, p=pane)
        cmds.button(l="Get Snapping Objects from Selection", c=lambda _: s.markers.add(*utility.get_selection(2)),
        ann="Select two objects in the scene that you wish to be moved/rotated closer together.\nIt is recommended to only use one group.")
        # scr = cmds.scrollLayout(cr=True)
        # s.markers = Marker_List(scr, s.validate, template.markers)
        s.markers = Marker_List(markers, s.validate, template.markers)
        # -----
        cmds.columnLayout(adj=True, p=pane)
        cmds.button(l="Add Attribute from Channelbox", c=lambda _: [s.attributes.add_attribute(a) for a in utility.get_attribute()],
        ann="Highlight attributes in the channelbox, and click the button to add them.")
        attributes = cmds.columnLayout(adj=True, bgc=BLACK)
        s.attributes = Attributes(attributes, s.validate, template.attributes)
        # -----
        cmds.formLayout(s.layout, e=True, af=[
            (row, "top", 0),
            (row, "left", 0),
            (row, "right", 0),
            (scroll, "left", 0),
            (scroll, "right", 0),
            (scroll, "bottom", 0)
            ], ac=[
                (scroll, "top", 0, row)
            ])

        # Pre fill information
        s.set_title(template.name)
        s.ready = True
        s.validate()
        s.enable(template.enabled)

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
        markers = list(s.markers.export())
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
        col = cmds.columnLayout(adj=True, p=parent)
        s.auto_state = True
        s.dynamic = IconCheckBox(col, s.set_auto, v=s.auto_state, h=WIDGET_HEIGHT,
            l="Automatic\nFrame Range:",
            i="autoload.png",
            st="iconAndTextHorizontal",
            ann="RIGHT CLICK: Additional options.\nON: Auto frame range.\nOFF: Manual.")
        cmds.popupMenu(p=col)
        cmds.menuItem(l="Set to playback range.", c=lambda x: s.set_range(*utility.get_playback_range()))
        s.row = cmds.rowLayout(nc=4, p=col)
        frame = utility.get_frame()
        s.min = IntBox(s.row, s.validate, frame, ann="Start Frame")
        s.max = IntBox(s.row, s.validate, frame, ann="End Frame")
        cmds.text(l="x", p=s.row)
        s.sub = FloatBox(s.row, s.validate, 1.0, ann="Subframes")

        # Detect things!
        s.loop = True
        threading.Thread(target=s.inner_loop).start()
        s.set_auto(s.auto_state)

    def validate(s, *_):
        """ Validate our timeline range """
        ok = True
        if not s.min.validate(lambda x: x <= s.max.value):
            ok = False
        if not s.max.validate(lambda x: x >= s.min.value):
            ok = False
        if not s.sub.validate(lambda x: x > 0):
            ok = False
        return ok

    def set_auto(s, state):
        """ Adjust auto frame range state """
        s.auto_state = state
        flip = False if state else True
        s.min.enable(flip)
        s.max.enable(flip)
        s.sub.enable(flip)

    def set_range(s, start, end, auto=False):
        """ Set range to values """
        if auto and not s.auto_state:# s.dynamic.value:
            return
        s.dynamic.value = auto
        s.set_auto(auto)
        s.min.value = start
        s.max.value = end
        s.sub.value = 1.0

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
                if s.auto_state:
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
        return s.min.value, s.max.value, s.sub.value

class Window(object):
    """ Main window! """
    def __init__(s, templates=None, title=""):
        templates = templates or []
        s.idle = True
        s.tabs = []
        s.group_index = 0
        name = "attrsnap"
        if cmds.window(name, q=True, ex=True):
            cmds.deleteUI(name)

        s.win = cmds.window(t=title or "Attribute Snapping!", w=800, h=400)
        form = cmds.formLayout()
        root = cmds.columnLayout(adj=True, p=form)
        cmds.menuBarLayout()
        cmds.menu(l="Groups")
        cmds.menuItem(l="New Group", c=s.new_group,
        ann="Create a new group.")
        cmds.menuItem(l="Remove Group", c=s.delete_tab,
        ann="Remove currently visible group.")
        cmds.menuItem(l="Duplicate Group", c=s.duplicate_tab,
        ann="Duplicate current group.")
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
        cmds.menu(l="Utility")
        cmds.menuItem(l="Fix Missing", c=s.fix,
        ann="Run retaget tool filtering only missing objects.")
        cmds.menuItem(l="Retarget", c=s.retarget,
        ann="Run retaget tool.")

        try:
            s.tab_grp = cmds.tabLayout(
                snt=True,
                newTabCommand=s.new_group,
                doubleClickCommand=s.rename_tab,
                p=form)
        except TypeError:
            s.tab_grp = cmds.tabLayout(
                doubleClickCommand=s.rename_tab,
                p=form)

        root2 = cmds.columnLayout(adj=True, p=form)
        cmds.separator(p=root2)
        row = cmds.rowLayout(nc=2, adj=2, p=root2)
        s.range = Range(row)
        cmds.button(l="-- Do it! --", h=WIDGET_HEIGHT*2, bgc=GREEN, p=row, c=s.run_match,
        ann="CLICK: Start matching, using all enabled groups.")
        cmds.helpLine(p=root2)

        cmds.formLayout(form, e=True, af=[
            (root, "top", 0),
            (root, "left", 0),
            (root, "right", 0),
            (s.tab_grp, "left", 0),
            (s.tab_grp, "right", 0),
            (root2, "left", 0),
            (root2, "right", 0),
            (root2, "bottom", 0)],
            ac=[
                # (root, "bottom", 0, root2)
                (s.tab_grp, "top", 0, root),
                (s.tab_grp, "bottom", 0, root2)
            ])
        cmds.showWindow(s.win)

        # Initial group
        if templates:
            for t in templates:
                s.new_group(t)
        else:
            s.new_group()

    def fix(s, *_):
        """ Retarget with only missing objects """
        templates = [tab.export() for tab in s.tabs]
        if templates:
            return Fixer(templates, type(s))
        utility.warn("Nothing to retarget.")

    def retarget(s, *_):
        """ Run retarget tool """
        templates = [tab.export() for tab in s.tabs]
        if templates:
            return Fixer(templates, type(s), include_present=True)

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

    def duplicate_tab(s, *_):
        """ Make a new group the same """
        selected = cmds.tabLayout(s.tab_grp, q=True, fpn=True, st=True)
        for i, tab in enumerate(s.tabs):
            if selected in tab.layout:
                template = tab.export()
                template.enabled = False
                s.new_group(template)
                return

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
        templates = utility.load_prompt()
        if templates:
            fix = Fixer(templates, type(s))
            if not fix.missing:
                Window(templates)

    def save_template(s, *_):
        """ Save template file """
        templates = [tab.export() for tab in s.tabs]
        utility.save_prompt(templates)

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

            # Match this!
            with utility.progress() as prog:
                for progress in match.match(valid, *s.range.export()):
                    prog(progress)
        s.idle = True

class Retarget(object):
    """ Retarget object """
    def __init__(s, col1, col2, col3, obj):
        s.old_obj = s.new_obj = obj
        cmds.text(l=obj, p=col1 , h=WIDGET_HEIGHT, bgc=GREY,
            ann="Original object name.")
        cmds.iconTextButton(i="arrowRight.png", p=col2, h=WIDGET_HEIGHT, w=WIDGET_HEIGHT, c=s.reset,
            ann="Click to reset back to old name.")
        s.gui = TextBox(col3, s.validate, obj,
            ann="Right click for suggestions.")
        cmds.popupMenu(pmc=s.get_suggestions)
        s.validate()

    def set_value(s, text, *_):
        """ Set value """
        s.gui.value = text

    def reset(s, *_):
        """ Reset to old name """
        s.gui.value = s.old_obj

    def validate(s, *_):
        """ Check object exists """
        return s.gui.validate(utility.valid_object)

    def get_value(s):
        """ Return value """
        return s.gui.value

    def get_suggestions(s, popup, *_):
        """ Find similarly named items """
        children = cmds.popupMenu(popup, q=True, ia=True)
        if children:
            cmds.deleteUI(children)
        for suggestion in utility.get_suggestion(s.gui.value):
            cmds.menuItem(l=suggestion, p=popup, c=functools.partial(s.set_value, suggestion))


class Fixer(object):
    """ Popup to assist in renaming missing objects """
    def __init__(s, templates, windowtype, include_present=False):
        # Pull out all objects
        all_objs = set()
        s.templates = templates
        s.windowtype = windowtype
        for template in templates:
            for marker_set in template.markers:
                for marker in marker_set:
                    all_objs.add(marker)
            for attribute in template.attributes:
                all_objs.add(attribute["obj"])

        # Filter for missing objects
        s.missing = []
        if include_present: # Just renaming? Add all object as "missing"
            s.missing = [a for a in all_objs]
        else:
            for obj in all_objs:
                if obj and not utility.valid_object(obj):
                    s.missing.append(obj)

        if not s.missing:
            return utility.warn("There are no missing objects!")

        s.win = cmds.window(rtf=True, t="Retarget")
        # root = cmds.formLayout()
        cmds.popupMenu()
        cmds.menuItem(l="Reset all.", c=s.reset_all,
            ann="Return all names back to default.")
        base = cmds.formLayout()
        root = cmds.scrollLayout(cr=True, p=base)
        cmds.text(l="Some objects cannot be found.\nPlease use the following tools to rename them.")
        fr1 = cmds.frameLayout(l="Batch Rename", p=root)
        row1 = cmds.rowLayout(nc=2, adj=1)
        row2 = cmds.rowLayout(nc=2, adj=2)
        cmds.columnLayout(adj=True, p=row2)
        cmds.text(l="Search:", h=WIDGET_HEIGHT)
        cmds.text(l="Replace:", h=WIDGET_HEIGHT)
        col = cmds.columnLayout(adj=True, p=row2)
        s.search = TextBox(col, (lambda x: ""), os.path.commonprefix(s.missing))
        s.replace = TextBox(col, lambda x:"")
        cmds.button(l="Rename", bgc=GREEN, p=row1, h=WIDGET_HEIGHT*2, c=s.rename_all,
            ann="Click to run the rename on all entries. Uses 'Regular Expression' syntax.")
        fr2 = cmds.frameLayout(l="Individual Rename", p=root)
        rows = cmds.rowLayout(nc=3, adj=3)
        c1 = cmds.columnLayout(adj=True, p=rows)
        c2 = cmds.columnLayout(adj=True, p=rows)
        c3 = cmds.columnLayout(adj=True, p=rows)
        s.retargets = {a: Retarget(c1, c2, c3, a) for a in s.missing}
        root2 = cmds.columnLayout(adj=True, p=base)
        fr3 = cmds.button(l="Apply Rename", p=root2, bgc=GREEN, h=WIDGET_HEIGHT*2, c=s.apply_all,
            ann="Applies changes to objects.")
        fr4 = cmds.helpLine(p=root2)

        cmds.formLayout(base, e=True, af=[
            (root, "top", 0),
            (root, "left", 0),
            (root, "right", 0),
            (root2, "bottom", 0),
            (root2, "left", 0),
            (root2, "right", 0)
        ], ac=[
            (root, "bottom", 0, root2),
         ])
        cmds.showWindow()

    def reset_all(s, *_):
        """ Reset all names """
        for obj in s.retargets:
            s.retargets[obj].reset()

    def rename_all(s, *_):
        """ Rename everything """
        search = s.search.value
        replace = s.replace.value

        searcher = re.compile(search)
        for obj in s.retargets:
            s.retargets[obj].set_value(searcher.sub(replace, s.retargets[obj].get_value()))

    def apply_all(s, *_):
        """ apply everything """
        changes = {a: s.retargets[a].get_value() for a in s.missing}

        # copy templates
        for template in s.templates:
            markers = [[changes[b] if b in changes else b for b in a] for a in template.markers]
            attributes = [{b: changes[b] if b == "obj" and b in changes else c for b, c in a.items()} for a in template.attributes]
            template.markers = markers
            template.attributes = attributes
        cmds.deleteUI(s.win)
        s.windowtype(s.templates)

class MiniWindow(object):
    def __init__(s, templates, title=""):
        """ Mini version of window """
        s.templates = templates
        s.idle = True
        cmds.window(t=title or "Attribute Snap!", rtf=True)
        row = cmds.rowLayout(nc=2, adj=2)
        s.range = Range(row)
        cmds.button(l="-- Do it! --", h=WIDGET_HEIGHT*2, bgc=GREEN, p=row, c=s.run_match,
        ann="CLICK: Start matching, using all enabled groups.")
        cmds.showWindow()

    def run_match(s, *_):
        """ Match things! """
        if s.idle:
            s.idle = False
            with utility.progress() as prog:
                for progress in match.match(s.templates, *s.range.export()):
                    prog(progress)
            s.idle = True
