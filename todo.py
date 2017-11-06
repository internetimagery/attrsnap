# Unrelated todo.txt parser
import datetime
import re

PRIORITY = re.compile(r"^(x|\(([A-Z])\))")
DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})\s")
PROJECT = re.compile(r"\s\+([^\s]+)")
CONTEXT = re.compile(r"\s@([^\s]+)")
KEYVAL = re.compile(r"\s([^\s:]+):([^\s:]+)")

EXTRA = re.compile(r"(\+|@|[^\s:]:)([^\s]+)")


https://github.com/EpocDotFr/todotxtio/blob/master/todotxtio.py

class Todo(object):
    """ Todo obj """
    def __init__(s):
        s.reset()

    def reset(s):
        """ Set default values """
        s._priority = None
        s._done = False
        s._creation = None
        s._complete = None
        s._task = ""
        s._projects = []
        s._contexts = []
        s._extra = {}

    def parse(s, line):
        """ Parse line of todo """
        tokens = re.split(r"\s", line)
        num_tokens = len(tokens)
        task = []

        if num_tokens > 0:
            # Check for completed or priority
            token = PRIORITY.match(tokens[0])
            if token:
                if token.group(1) == "x":
                    s._done = True
                else:
                    s._priority = token.group(2)

            token = DATE.match(tokens[1])
            if token:
                date = datetime.date(token.group(1), token.group(2), token.group(3))
                if s._done: # Date is completion date
                    s._complete = date

# Rule 1: If priority exists, it ALWAYS appears first.

# Rule 2: A task's creation date may optionally appear directly after priority and a space.

# If there is no priority, the creation date appears first. If the creation date exists, it should be in the format YYYY-MM-DD.

# Rule 3: Contexts and Projects may appear anywhere in the line after priority/prepended date.
#
#     A context is preceded by a single space and an at-sign (@).
#     A project is preceded by a single space and a plus-sign (+).
#     A project or context contains any non-whitespace character.
#     A task may have zero, one, or more than one projects and contexts included in it.


(A) Thank Mom for the meatballs @phone
(B) Schedule Goodwill pickup +GarageSale @phone
Post signs around the neighborhood +GarageSale
@GroceryStore Eskimo pies
x 2011-03-02 2011-03-01 Review Tim's pull request +TodoTxtTouch @github
Get things done @home
Get some other things done @work
Add task text to Chromodoro @home +Chromodoro tid:293
Fix retrieve password scenarios @home +Diaspora tid:292
[Significant coding] for Diaspora @home +Diaspora tid:275
