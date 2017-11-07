# Unrelated todo.txt parser
import datetime
import re

# Header stuff
DATE = r"(\d{4})-(\d{2})-(\d{2})\s+"
PRIORITY = r"\((?P<priority>[A-Z])\)\s+"
COMPLETE = r"(?P<complete>x)\s+"
HEADER = re.compile(r"^(?:%s|%s)?(?P<dates>(?:%s){0,2})" % (COMPLETE, PRIORITY, DATE))

# Tag stuff
PROJECT = r"\+[^\s]+"
CONTEXT = r"@[^\s]+"
KWARGS = r"([^\s:]+):([^\s]+)"
TAGS = re.compile("({})".format("|".join([
    PROJECT,
    CONTEXT,
    KWARGS])))

class Todo(object):
    """ Todo obj """
    def __init__(s, todo=""):
        s.priority = None
        s.done = False
        s.creation = None
        s.complete = None
        s.task = ""
        s.projects = []
        s.contexts = []
        s.extra = {}

        header = HEADER.search(todo)
        head_end = 0
        if header:
            s.complete = True if header.group("complete") else False
            priority = header.group("priority")
            s.priority = priority if priority else "M" # Pick default priority
            dates = re.findall(DATE, header.group("dates"))
            if dates:
                year, month, day = dates[0]
                if s.complete: # Date 1 will be completion
                    s.complete = datetime.date(int(year), int(month), int(day))
                    if len(dates) > 1:
                        year, month, day = dates[1]
                        s.creation = datetime.date(int(year), int(month), int(day))
                else:
                    s.creation = datetime.date(int(year), int(month), int(day))
            head_end = header.end(0)
        body = todo[head_end:]
        
# Rule 1: If priority exists, it ALWAYS appears first.

# Rule 2: A task's creation date may optionally appear directly after priority and a space.

# If there is no priority, the creation date appears first. If the creation date exists, it should be in the format YYYY-MM-DD.

# Rule 3: Contexts and Projects may appear anywhere in the line after priority/prepended date.
#
#     A context is preceded by a single space and an at-sign (@).
#     A project is preceded by a single space and a plus-sign (+).
#     A project or context contains any non-whitespace character.
#     A task may have zero, one, or more than one projects and contexts included in it.

test = ["(A) Thank Mom for the meatballs @phone",
"(B) Schedule Goodwill pickup +GarageSale @phone",
"Post signs around the neighborhood +GarageSale",
"@GroceryStore Eskimo pies",
"x 2011-03-02 2011-03-01 Review Tim's pull request +TodoTxtTouch @github",
"x 2011-03-02 Review Tim's pull request +TodoTxtTouch @github",
"Get things done @home",
"Get some other things done @work",
"Add task text to Chromodoro @home +Chromodoro tid:293",
"Fix retrieve password scenarios @home +Diaspora tid:292",
"[Significant coding] for Diaspora @home +Diaspora tid:275"]

for t in test:
    Todo(t)
