# Gui!

try:
    from gui_maya import *
except ImportError:
    raise RuntimeError("No usable gui")
