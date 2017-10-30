# Simple priority queue

from __future__ import print_function
import heapq

class Task(object):
    """ Ordered set of tasks """
    def __init__(s):
        s.heap = []
        s.id = 0
    def add(s, task, *priorities):
        """ Add a task. Provided a list of priorities to sort by """
        s.id += 1
        heapq.heappush(s.heap, priorities[:] + (s.id, task))
    def get(s):
        return heapq.heappop(s.heap)[-1]
    def __len__(s):
        return len(s.heap)
    def __iter__(s):
        while len(s.heap):
            yield s.get()

if __name__ == '__main__':
    t = Task()
    t.add("two", 2)
    t.add("one and half", 1, 5)
    t.add("one", 1)
    t.add("three", 3)
    for task in t:
        print(task)
