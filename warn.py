# Visual popup on errors. Not an error handler!
# Can be used by passing the function and args to "run" or in a "with" block
# Created 11/10/15 Jason Dixon
# http://internetimagery.com

import sys

class Warn(object):
    def _err(s, title, message):
        import maya.cmds as cmds
        cmds.confirmDialog(
            t="Uh oh... %s" % title,
            m=message
        )
    def __call__(s, *args, **kwargs):
        with s:
            if len(args) and callable(args[0]):
                return args[0](*args[1:], **kwargs)
            else:
                raise RuntimeError, "Function not provided as first argument."
    def __enter__(s):
        pass
    def __exit__(s, eType, eName, eTrace):
        if eType:
            s._err(eType.__name__, str(eName))
sys.modules[__name__] = Warn()
