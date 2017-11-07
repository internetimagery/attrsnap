# Unrelated todo.txt parser
from __future__ import print_function
import datetime
import re

# Header stuff
DATE = r"(\d{4})-(\d{2})-(\d{2})\s+"
PRIORITY = r"\((?P<priority>[A-Z])\)\s+"
DONE = r"(?P<done>x)\s+"
HEADER = re.compile(r"^(?:%s)?(?:%s)?(?P<dates>(?:%s){0,2})" % (DONE, PRIORITY, DATE))
DATES = re.compile(DATE)

# Tag stuff
TAGS = re.compile(r"(?P<key>\+|@|[^\s:]+:)(?P<value>[^\s]+)")

class Todo(object):
    """ Todo obj """
    def __init__(s, todo="", keep_tags=False):
        """ Parse out a todo.
        todo = String to parse. Assume one line.
        keep_tags = Retain the tag text in the body of the task. ie "+project" becomes "project" """
        s.raw = todo
        s.priority = "M" # Middle of the road.
        s.done = False
        s.creation = None
        s.complete = None
        s.task = ""
        s.projects = set()
        s.contexts = set()
        s.extra = {}

        header = HEADER.search(todo)
        if header:
            s.done = True if header.group("done") else False
            priority = header.group("priority")
            if priority:
                s.priority = priority
            dates = DATES.findall(header.group("dates"))
            if dates:
                year, month, day = dates[0]
                if s.done: # Date 1 will be completion
                    s.complete = datetime.date(int(year), int(month), int(day))
                    if len(dates) > 1:
                        year, month, day = dates[1]
                        s.creation = datetime.date(int(year), int(month), int(day))
                else:
                    s.creation = datetime.date(int(year), int(month), int(day))
            head_end = header.end(0)
        else:
            head_end = 0
        s.task = todo[head_end:]

        for tag in reversed(list(TAGS.finditer(s.task))):
            key = tag.group("key")
            if key == "+":
                s.projects.add(tag.group("value"))
            elif key == "@":
                s.contexts.add(tag.group("value"))
            else:
                s.extra[key[:-1]] = tag.group("value")
                s.task = s.task[:tag.start(0)] + s.task[tag.end(0):]
                continue # Always remove key:val pairs

            if keep_tags: # Keep tags. Just remove symbol
                s.task = s.task[:tag.start(0)] + s.task[tag.start(0) + 1:]
            else: # Remove tag entirely
                s.task = s.task[:tag.start(0)] + s.task[tag.end(0):]
        s.task = s.task.strip() # Tidy up

    def __str__(s):
        task = []
        # Header stuff
        task.append("({})".format(s.priority))
        if s.done:
            task.insert(0, "x")
            if s.complete:
                task.append(str(s.complete))
                if s.creation:
                    task.append(str(s.creation))
        else:
            if s.creation:
                task.append(str(s.creation))
        task.append(s.task)
        task += ["+{}".format(a) for a in s.projects]
        task += ["@{}".format(a) for a in s.contexts]
        task += ["{}:{}".format(*a) for a in s.extra.items()]
        return " ".join(task)

if __name__ == '__main__':
    # Quick test and output
    for t in ["(A) Thank Mom for the meatballs @phone",
    "(B) Schedule Goodwill pickup +GarageSale @phone",
    "Post signs around the neighborhood +GarageSale",
    "@GroceryStore Eskimo pies",
    "x 2011-03-02 2011-03-01 Review Tim's pull request +TodoTxtTouch @github",
    "x 2011-03-02 Review Tim's pull request +TodoTxtTouch @github",
    "Get things done @home",
    "Get some other things done @work",
    "Add task text to Chromodoro @home +Chromodoro tid:293",
    "Fix retrieve password scenarios @home +Diaspora tid:292",
    "[Significant coding] for Diaspora @home +Diaspora tid:275",
    "(A) Call Mom @Phone +Family",
    "(A) Schedule annual checkup +Health",
    "(B) Outline chapter 5 +Novel @Computer",
    "(C) Add cover sheets @Office +TPSReports",
    "Plan backyard herb garden @Home",
    "Pick up milk @GroceryStore",
    "Research self-publishing services +Novel @Computer",
    "x Download Todo.txt mobile app @Phone]"]:
        t1 = Todo(t)
        t2 = Todo(str(t1))
        print("Old:", t1.raw)
        print("New:", str(t1))
        print("-"*20)
        assert str(t1) == str(t2)
