# Perform a match by broadly casting a net. Then within that net, getting finer and finer detailself.
from __future__ import print_function


def match(group):
    """ Cast a wide net. Slowly narrow down after the fact """
    chunks = 11 # Number of chunks to split range into
    chunk_scale = 1 / chunks
    attr_chunks = [(a.max - a.min) * chunk_scale for a in group.attributes]
    for i in range(chunks + 1) * chunks:
