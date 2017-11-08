# Table layout
import maya.cmds as cmds
import functools

class Table(object):
    def __init__(s, parent, cols):
        """ Initiate a table. cols = {"column", func} """
        s.items = []
        s.cols = cols
        s.parent = parent
        s.dir = True
        s.order = ""
        s.sort(cols.keys()[0])


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
        for name, col in zip(s.cols, cols):
            dir_ = u"\u02C6" if s.dir else u"\u02c7"
            title = u"{} {}".format(name, dir_) if name == s.order else name
            cmds.button(l=title, p=col, c=functools.partial(s.sort, name))
        for row in sorted(s.items, key=s.cols[s.order], reverse=s.dir):
            for name, col in zip(row, cols):
                cmds.text(l=name, p=col)

def main():
    cmds.window()
    p = cmds.columnLayout(adj=True)
    cmds.showWindow()

    rows = [
        (1, "one"),
        (2, "two"),
        (3, "three")]

    t = Table(p, {
        "num1": lambda x: x[0],
        "num2": lambda x: x[1]})
    t.items = rows
    t.build()

if __name__ == '__main__':
    main()
