# Extra functionality for niche situations


def FROM_TO_Namespace():
    """ Load match file. Replace "FROM:" and "TO:"
        with selected objects namespaces. Open mini window.
        Maya specific.
    """
    import gui_maya as gui
    import utility_maya as utility

    selection = utility.get_selection(2)
    templates = utility.load_prompt()

    ns_select = []
    for select in selection:
        parts = select.rsplit(":", 1)
        ns_select.append(parts[0]+":" if len(parts) == 2 else "")

    for template in templates:
        template.markers = [a.replace("FROM:", ns_select[0]).replace("TO:", ns_select[1]) for a in template.markers]
        template.attributes = [{a: b.replace("FROM:", ns_select[0]).replace("TO:", ns_select[1]) if a == "obj" else b for a,b in a.items()} for a in template.attributes]

    fix = Fixer(templates, gui.MiniWindow)
    if not fix.missing:
        gui.MiniWindow(templates)
