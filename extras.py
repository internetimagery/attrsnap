# Extra functionality for niche situations


# WIP
import utility
import gui

def quick_B_to_A():
    """ Quick selection matching """
    selection = utility.get_selection(2)
    templates = utility.load_prompt()
    # TODO: Get namespace of selected
    # TODO: rename "TO" and "FROM" to namespaces
    for template in templates:
        pass
    fix = Fixer(templates, gui.MiniWindow)
    if not fix.missing:
        gui.MiniWindow(templates)
