# Load elements.

try:
    from element_maya import *
except ImportError:
    raise RuntimeError("Element not supported")
