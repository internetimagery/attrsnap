# Extra functionality for niche situations

import groups
import utility
import match

def FROM_TO_Namespace(path=None):
    """ Load match file. Replace "FROM:" and "TO:"
        with selected objects namespaces. Open mini window.
        Maya specific.
    """
    import gui_maya as gui

    selection = utility.get_selection(2)
    if path:
        templates = groups.load(path)
    else:
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

class Match(object):
    """ Nicely reading matching ie:
    Match("obj1", "obj2").using("attr1.tx").position()
    Match(["obj1", "obj2"]).using("attr1.tx").rotation(1, 123)
    """
    def __init__(s, mkr1, *mkr2):
        if mkr2:
            s.markers = [(mkr1, mkr2[0])]
        else:
            s.markers = mkr1
        s.attrs = []
        s._type = groups.POSITION
    def using(s, *attrs):
        split = (a.rsplit(".", 1) for a in attrs)
        s.attrs = [{"obj":a, "attr":b} for a, b in split]
        return s
    def position(s, Fstart=None, Fend=None):
        s._go(Fstart, Fend, groups.POSITION)
    def rotation(s, Fstart=None, Fend=None):
        s._go(Fstart, Fend, groups.ROTATION)
    def _go(s, Fstart, Fend, type_):
        template = groups.Template(
            match_type=type_,
            markers=s.markers,
            attributes=s.attrs)
        with utility.progress() as prog:
            for progress in match.match([template], start_frame=Fstart, end_frame=Fend):
                prog(progress)
