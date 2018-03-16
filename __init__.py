# Move two objects as close as possible using arbirary attributes.
# Created By Jason Dixon. http://internetimagery.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is a labor of love, and therefore is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

import gui
import utility

def main():
    """ Main window """
    gui.Window()

def mini(templates):
    """ Shotcut mini window prefilled """
    gui.Fixer(templates, gui.MiniWindow)
