# Dict that gets values based on nearest key.

class Dict(dict):
    def __init__(s, func, *args, **kwargs):
        """ Provide function to do the sorting """
        s.func = func
        dict.__init__(s, *args, **kwargs)
    def near(s, key):
        """ Return nearest keys value """
        near_key = None
        near_dist = None
        for k in s:
            if near_dist is None:
                near_dist = s.func(key, k)
                near_key = k
            else:
                test = s.func(key, k)
                if test < near_dist:
                    near_dist = test
                    near_key = k
        return s[near_key]
