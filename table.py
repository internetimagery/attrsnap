# Table layout
import maya.cmds as cmds
import functools

class Table(object):
    def __init__(s, parent, cols, row):
        """ Initiate a table.
        cols = ["name", "name"]
        row = func() """
        s.items = []
        s.cols = cols
        s.row = row
        s.parent = parent
        s.dir = False
        s.order = 0
        s.sort(0)


    def sort(s, order, *_):
        """ Change sorting order """
        if order == s.order:
            s.dir = False if s.dir else True
        s.order = order
        s.build()

    def build(s):
        """ make it """
        old = cmds.layout(s.parent, q=True, ca=True)
        if old:
            cmds.deleteUI(old)
        row = cmds.rowLayout(nc=len(s.cols))
        cols = [cmds.columnLayout(adj=True, p=row) for a in s.cols]
        for i, (name, col) in enumerate(zip(s.cols, cols)):
            dir_ = u"\u02C6" if s.dir else u"\u02c7"
            title = u"{} {}".format(name, dir_) if i == s.order else name
            cmds.button(l=title, p=col, c=functools.partial(s.sort, i))
        for row in sorted(s.items, key=(lambda x: x[s.order]), reverse=s.dir):
            for gui, col in zip(s.row(row), cols):
                cmds.control(gui, e=True, p=col)

def main():

    rows = [
        (1, "one"),
        (2, "two"),
        (3, "three")]

    cmds.window()
    p = cmds.columnLayout(adj=True)
    cmds.showWindow()
    t = Table(p, ["num1", "num2"], lambda x: (cmds.text(l=x[0]), cmds.text(l=x[1])))
    t.items = rows
    t.build()

if __name__ == '__main__':
    main()
