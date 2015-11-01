# Check with brute force the distance of objects
import math
import time
import maya.cmds as cmds
from pprint import pprint

def distance(objs):
    pos = [[cmds.xform(b, q=True, ws=True, t=True) for b in a] for a in objs]
    return math.sqrt(sum([(a[0][b] - a[1][b])**2 for a in pos for b in range(3)]))

def chunks(range_, steps):
    if not steps: raise RuntimeError, "Cannot have a zero stepsize."
    scale = (range_[1] - range_[0]) * (1.0 / (steps - 1.0))
    return [a * scale + range_[0] for a in range(steps)]


class AutoKey(object):
    def __enter__(s):
        s.state = cmds.autoKeyframe(q=True, st=True)
        cmds.autoKeyframe(st=False)
    def __exit__(s, *err):
        cmds.autoKeyframe(st=s.state)

class Progress(object):
    def __init__(s, title):
        s.title = title
        s.canceled = False
    def __enter__(s):
        s.win = cmds.window(t=s.title)
        cmds.columnLayout(w=200, bgc=(0.2,0.2,0.2))
        s.bar = cmds.columnLayout(w=1, h=40, bgc=(0.8,0.4,0.5))
        cmds.showWindow(s.win)
        return s
    def update(s, progress):
        if not progress: progress = 1
        if cmds.layout(s.bar, ex=True):
            cmds.columnLayout(s.bar, e=True, w=progress * 2)
        else:
            s.canceled = True
        cmds.refresh()
    def __exit__(s, *err):
        if cmds.window(s.win, ex=True): cmds.deleteUI(s.win)

class Marker(object):
    def __init__(s, objs):
        s.objs = objs
    def __enter__(s):
        s.locators = dict((c, cmds.spaceLocator()[0]) for c in set(b for a in s.objs for b in a))
        for a, b in s.locators.items(): cmds.pointConstraint(a, b)
        return [[s.locators[b] for b in a] for a in s.objs]
    def __exit__(s, *err):
        for a, b in s.locators.items():
            if cmds.objExists(b): cmds.delete(b)

class Undo(object):
    def __enter__(s): cmds.undoInfo(openChunk=True)
    def __exit__(s, *err): cmds.undoInfo(closeChunk=True)

print chunks([3,400], 20)

    #
	# #snap attributes with brute force
	# def snapbrute(self):
	# 	attr = self.attr.keys() #generate list of attributes
	# 	longest = 0
	# 	for at in self.attr: #get the largest range
	# 		longest = max(longest, (self.attr[at][1]-self.attr[at][0]) )
	# 	for step in range(30): #work out how many steps it will take to reach accuracy
	# 		longest*=(1.0/self.steps)*2
	# 		if longest < self.accuracy:
	# 			break
	# 	combination = 0
	# 	for i in range(len(attr)): #work out the number of combinations
	# 		combination+=self.steps**(len(attr)-i)
	# 	self.prog = 1.0 / (combination*step) #progress bar step
	# 	for i in range(step):
	# 		snap = self.runbrute( attr, self.attr, [9999]*len(self.loc) )[0]['attr']
	# 		for at in snap: #update limits
	# 			self.attr[at] = snap[at]
	# 	for at in self.attr: #set the attributes
	# 		cmds.setAttr( at, ((self.attr[at][1]-self.attr[at][0])*0.5+self.attr[at][0]) )
	# 		(obj, dot, attr) = at.rpartition('.')
	# 		cmds.setKeyframe( obj, at=attr )
	# 	self.progress.cancel()
    #
# 	#run through all combinations in cache checking distance
# 	# i = position in attribute list
# 	# at = attribute list
# 	# cache = cache of all positions, ranges etc
# 	# current = current combination, always updated
# 	# snap = snapshot of current, when a shorter distance is found
# 	# dist = the shortest distance working with currently
#
# 	#run through all combinations with brute force checking distance
# 	def runbrute(self, at, limit, single_dist, total_dist = 9999, current = {}, snap = {}, i=0 ):
# 		if self.working: #make sure we don't loop forever
# 			step = (limit[at[i]][1]-limit[at[i]][0])*(1.0/(self.steps-1)) #get search incriment
# 			cache = []
# 			for s in range( self.steps ): #run through each step
# 				self.progress.update( self.prog )
# 				s=limit[at[i]][0]+s*step #each step
# 				cmds.setAttr( at[i], s ) #set attribute
# 				#get range to store
# 				if s <= limit[at[i]][0]: #don't go below lower boundary
# 					r = [s,(s+(step*2))]
# 				elif s >= limit[at[i]][1]: # or upper boundary
# 					r = [(s-(step*2)),s]
# 				else:
# 					r = [(s-step),(s+step)]
# 				current[at[i]] = r #update attr list
# 				if (i+1) < len(at):
# 					(snap,current,single_dist,total_dist)=self.runbrute(at,limit,single_dist,total_dist,current,snap,(i+1))
# 				entry = {'attr':current.copy(), 'loc':[]}
# 				for n,p in enumerate(self.loc): #run through each object pair
# 					entry['loc'].append([cmds.getAttr((p[0]['loc']+'.t'))[0],cmds.getAttr((p[1]['loc']+'.t'))[0]])
# 				cache.append(entry)
#
# 			for i in range(len(cache)):
# 				new_dist = 0.0
# 				for p in range(len(cache[i]['loc'])):
# 					new_dist+= Distance(cache[i]['loc'][p][0], cache[i]['loc'][p][1])
# #					if i:
# #						pass
# #						p1 = cache[(i-1)]['loc'][o] #point 1
# #						p2 = cache[i]['loc'][o] # point 2
# #						a1 = cache[(i-1)]['attr'][at[i]]
# #						a2 = cache[i]['attr'][at[i]]
# #						at, pos, dist = self.LinearDistance(a1,p1,a2,p2)
# #						if at: #if linear check picked up something, add that
# #							new_dist+= dist
# #						else: #otherwise back to brute force we go
# #							new_dist+= Distance(o[0], o[1])
# #					else:
# #						new_dist+= Distance(o[0], o[1])
# 				if new_dist < single_dist:
# 					single_dist = new_dist
# 					snap['attr'] = cache[i]['attr']
# 					snap['loc'] = cache[i]['loc']
# 		return snap, current, single_dist, total_dist
