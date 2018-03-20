# Base vlasses for Abstracted Elements
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

class Attribute(object):
    """ An Attribute """
    def set_value(s, val):
        """ Set attribute value. Returns float. """
        raise NotImplementedError

    def get_value(s):
        """ Get current value """
        raise NotImplementedError

    def get_bias(s):
        """ Get bias value """
        raise NotImplementedError

    def key(s, value):
        """ Keyframe value at current time """
        raise NotImplementedError

class Marker_Set(object):
    """ Collection of two markers """
    def get_pos_distance(s):
        """ Get positional distance """
        raise NotImplementedError

    def get_rot_distance(s, sum=sum, zip=zip):
        """ Get rotational distance """
        raise NotImplementedError

    def __iter__(s):
        """ Loop over entries """
        raise NotImplementedError
