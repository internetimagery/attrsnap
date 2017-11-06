# Unrelated todo.txt parser
import datetime
import re

PRIORITY = re.compile(r"(x|\([A-Z]\))\s")
DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})\s")
PROJECT = re.compile(r"\s\+([^\s]+)")
CONTEXT = re.compile(r"\s@([^\s]+)")
KEYVAL = re.compile(r"\s([^\s:]+):([^\s:]+)")

EXTRA = re.compile(r"(\+|@|[^\s:]:)([^\s]+)")

class Todo(object):
    """ Todo obj """
    def __init__(s):
        s.priority = None
        s.complete = False
        s.creation = None
        s.note = ""
        s.projects = []
        s.contexts = []
        s.extra = {}

    def parse(s, line):
        """ Parse line of todo """

        if line[0] == "x": # Note is complete
            pass
        else:
            pass


# Rule 1: If priority exists, it ALWAYS appears first.

# Rule 2: A task's creation date may optionally appear directly after priority and a space.

# If there is no priority, the creation date appears first. If the creation date exists, it should be in the format YYYY-MM-DD.

# Rule 3: Contexts and Projects may appear anywhere in the line after priority/prepended date.
#
#     A context is preceded by a single space and an at-sign (@).
#     A project is preceded by a single space and a plus-sign (+).
#     A project or context contains any non-whitespace character.
#     A task may have zero, one, or more than one projects and contexts included in it.


# (A) Thank Mom for the meatballs @phone
# (B) Schedule Goodwill pickup +GarageSale @phone
# Post signs around the neighborhood +GarageSale
# @GroceryStore Eskimo pies
# x 2011-03-02 2011-03-01 Review Tim's pull request +TodoTxtTouch @github
# Get things done @home
# Get some other things done @work
# Add task text to Chromodoro @home +Chromodoro tid:293
# Fix retrieve password scenarios @home +Diaspora tid:292
# [Significant coding] for Diaspora @home +Diaspora tid:275
