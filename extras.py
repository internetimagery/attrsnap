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
        template.markers = [[b.replace("FROM:", ns_select[0]).replace("TO:", ns_select[1]) for b in a] for a in template.markers]
        template.attributes = [{a: b.replace("FROM:", ns_select[0]).replace("TO:", ns_select[1]) if a == "obj" else b for a,b in a.items()} for a in template.attributes]

    def winFactory(*args, **kwargs):
        kwargs["title"] = "Match %s <- %s" % (ns_select[0], ns_select[1])
        return gui.MiniWindow(*args, **kwargs)

    fix = gui.Fixer(templates, winFactory)
    if not fix.missing:
        winFactory(templates)
