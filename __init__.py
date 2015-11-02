from functools import partial
import maya.cmds as cmds
import maya.mel as mel
import math as m

# Created by Jason Dixon 14/03/14
# http://internetimagery.com

debug = False

	#obj = [ [object, object] , [object, object] ]
	#attr = { 'object.attribute' : [ upper , lower ] }
	#timerange = range of time to scan over
	#steps = number of steps to take for each refinement. more steps = longer more refined search
	#accuracy = how close should the match be to exact
class attrSnap(object):
	def __init__(self, obj, attr, text, steps = 10, accuracy = 0.001):
		self.working = True #allow canceling
		self.attr = attr.copy()
		self.loc = []
		self.accuracy = accuracy
		self.progress = Progress( text, 30 )
		#create locators constrainted to objects
		for pair in obj:
			p = []
			for o in pair:
				loc = cmds.spaceLocator()[0]
				cmds.parentConstraint( o , loc )
				p.append( {'loc':loc, 'obj': o} )
			self.loc.append(p)
		#steps
		if steps < 3:
			self.steps = 3
		else:
			self.steps = steps
		if accuracy <= 0:
			self.accuracy = 0.001
		else:
			self.accuracy = accuracy
		cmds.select(cl=True)

	#clean up locators etc
	def __del__(self):
		for pair in self.loc: #run through each pair
			for p in pair:
				cmds.delete( p['loc'] )

	#snap attributes with brute force
	def snapbrute(self):
		attr = self.attr.keys() #generate list of attributes
		longest = 0
		for at in self.attr: #get the largest range
			longest = max(longest, (self.attr[at][1]-self.attr[at][0]) )
		for step in range(30): #work out how many steps it will take to reach accuracy
			longest*=(1.0/self.steps)*2
			if longest < self.accuracy:
				break
		combination = 0
		for i in range(len(attr)): #work out the number of combinations
			combination+=self.steps**(len(attr)-i)
		self.prog = 1.0 / (combination*step) #progress bar step
		for i in range(step):
			snap = self.runbrute( attr, self.attr, [9999]*len(self.loc) )[0]['attr']
			for at in snap: #update limits
				self.attr[at] = snap[at]
		for at in self.attr: #set the attributes
			cmds.setAttr( at, ((self.attr[at][1]-self.attr[at][0])*0.5+self.attr[at][0]) )
			(obj, dot, attr) = at.rpartition('.')
			cmds.setKeyframe( obj, at=attr )
		self.progress.cancel()

	#run through all combinations in cache checking distance
	# i = position in attribute list
	# at = attribute list
	# cache = cache of all positions, ranges etc
	# current = current combination, always updated
	# snap = snapshot of current, when a shorter distance is found
	# dist = the shortest distance working with currently

	#run through all combinations with brute force checking distance
	def runbrute(self, at, limit, single_dist, total_dist = 9999, current = {}, snap = {}, i=0 ):
		if self.working: #make sure we don't loop forever
			step = (limit[at[i]][1]-limit[at[i]][0])*(1.0/(self.steps-1)) #get search incriment
			cache = []
			for s in range( self.steps ): #run through each step
				self.progress.update( self.prog )
				s=limit[at[i]][0]+s*step #each step
				cmds.setAttr( at[i], s ) #set attribute
				#get range to store
				if s <= limit[at[i]][0]: #don't go below lower boundary
					r = [s,(s+(step*2))]
				elif s >= limit[at[i]][1]: # or upper boundary
					r = [(s-(step*2)),s]
				else:
					r = [(s-step),(s+step)]
				current[at[i]] = r #update attr list
				if (i+1) < len(at):
					(snap,current,single_dist,total_dist)=self.runbrute(at,limit,single_dist,total_dist,current,snap,(i+1))
				entry = {'attr':current.copy(), 'loc':[]}
				for n,p in enumerate(self.loc): #run through each object pair
					entry['loc'].append([cmds.getAttr((p[0]['loc']+'.t'))[0],cmds.getAttr((p[1]['loc']+'.t'))[0]])
				cache.append(entry)

			for i in range(len(cache)):
				new_dist = 0.0
				for p in range(len(cache[i]['loc'])):
					new_dist+= Distance(cache[i]['loc'][p][0], cache[i]['loc'][p][1])
#					if i:
#						pass
#						p1 = cache[(i-1)]['loc'][o] #point 1
#						p2 = cache[i]['loc'][o] # point 2
#						a1 = cache[(i-1)]['attr'][at[i]]
#						a2 = cache[i]['attr'][at[i]]
#						at, pos, dist = self.LinearDistance(a1,p1,a2,p2)
#						if at: #if linear check picked up something, add that
#							new_dist+= dist
#						else: #otherwise back to brute force we go
#							new_dist+= Distance(o[0], o[1])
#					else:
#						new_dist+= Distance(o[0], o[1])
				if new_dist < single_dist:
					single_dist = new_dist
					snap['attr'] = cache[i]['attr']
					snap['loc'] = cache[i]['loc']
		return snap, current, single_dist, total_dist

	def LinearDistance(self,a1, p1, a2, p2): #check distance of object by projecting line a = attribute, p = [loc1, loc2]
		v1 = VectorMath(lambda x,y:y-x,p1[0],p2[0]) #velocity 1
		v2 = VectorMath(lambda x,y:y-x,p1[1],p2[1]) #velocity 2
		point = ClosestPoint(p1[0], v1, p1[1], v2) #closest point between two (linear)
		if 0.0 <= point <= 1.0: #point is within line range
		    chk1 = VectorMath(lambda x,y: x+y, p1[0],VectorMath(lambda x,y: x*point, v1)) # pick location
		    chk2 = VectorMath(lambda x,y: x+y, p1[1],VectorMath(lambda x,y: x*point, v2)) # pick location
		    dist = Distance(chk1, chk2)
		    return (a2-a1)*point+a1, [chk1,chk2], dist #return Attr, pos, dist
		return False, False, False

########################################

class GUI(object):
	def __init__(self):
		#DATA
		self.working = None #currently running through?
		self.GUI = {} #gui elements
		self.GUI['obj'] = {} #recorded objects
		self.GUI['attr'] = {}#recorded attribute entries

		self.GUI['window'] = cmds.window( title = 'Attribute Snap', rtf=True, s=False)
		self.GUI['layout3'] = cmds.rowColumnLayout( nc=2 )
		self.GUI['layout1'] = cmds.columnLayout( adjustableColumn=True, w=120 ) #buttons in here
		self.GUI['text1'] = cmds.text( label = 'Load up two Objects.', h=20 )
		self.GUI['button1'] = cmds.button( label = 'Load Object Pair', h=30, c=self.loadobj )
		self.GUI['button2'] = cmds.button( label = 'Load Attributes', h=30, c=self.loadattr )
		self.GUI['float1'] = cmds.floatFieldGrp( el = 'Accuracy', v1=(0.001), cw2 = (60,60), pre=3 )
		self.GUI['int1'] = cmds.intFieldGrp( el = 'Steps', v1=(10), cw2 = (60,60) )
		self.GUI['button4'] = cmds.button( label = 'Run Scan!', c= self.runscan, height = 60 )
		cmds.setParent('..')
		self.GUI['layout4'] = cmds.columnLayout( adjustableColumn=True ) # objects and attributes in here
		self.GUI['text2'] = cmds.text(l='Object Pairs' , h=20)
		cmds.separator()
		self.GUI['layout5'] = cmds.rowColumnLayout( nc=2, cw=[(1,20)], bgc=[0.2,0.2,0.2] ) # objects in here
		cmds.setParent('..')
		self.GUI['text3'] = cmds.text(l='Attributes', h=20)
		cmds.separator()
		self.GUI['layout2'] = cmds.rowColumnLayout( nc=5, cw=[(1,20),(2,150),(3,70),(4,60),(5,60)], cal=[(1,'center'),(2,'left'),(3,'left'),(4,'center'),(5,'center')], bgc=[0.15,0.15,0.15] ) #attributes in here
		cmds.setParent('..')
		cmds.setParent('..')
		cmds.showWindow( self.GUI['window'] )

	#add attribute to list
	def attrCreate(self, o, at):
		#work out limits
		name = o+'.'+at
		if not name in self.GUI['attr']:
			mini = cmds.attributeQuery(at,n=o,min=True)[0] if cmds.attributeQuery(at,n=o,mne=True) else -999.0
			maxi = cmds.attributeQuery(at,n=o,max=True)[0] if cmds.attributeQuery(at,n=o,mxe=True) else 999.0
			if 'rotate' in at:
				mini = 0.0
				maxi = 360.0
			#create list entry
			p = self.GUI['layout2']
			entry = {}
			entry['button1'] = cmds.button(l='X',h=20,p=p,bgc=[0.4,0.4,0.4],c=partial(self.removeEntry,name,'attr'))
			entry['text1'] = cmds.text(l=o,p=p,bgc=[0.2,0.2,0.2] )
			entry['text2'] = cmds.text(l=(cmds.attributeQuery(at,n=o,nn=True)),p=p,bgc=[0.2,0.2,0.2] )
			entry['num1'] = cmds.floatField(v=mini,pre=3,p=p,) #min
			entry['num2'] = cmds.floatField(v=maxi,pre=3,p=p,) #max
			self.GUI['attr'][name] = entry

	#delete attribute from list
	def removeEntry(self, at, lst, *button):
		for l in self.GUI[lst][at]:
			DeleteUI(self.GUI[lst][at][l])
		del self.GUI[lst][at]
		self.helpfulMessage()

	#update value
	def update(self, gui, val):
		if gui == 'float1':
			self.accuracy = val
		elif gui=='int1':
			self.steps = val

	#load up attributes
	def loadattr(self, *button):
		obj = cmds.ls(sl=True)
		if obj:
			attr = cmds.channelBox( 'mainChannelBox' , sma = True, query = True )
			if attr:
				for o in obj:
					for at in attr:
						if cmds.attributeQuery( at, node = o ,ex = True ): #check the channel exists
							self.attrCreate( o, cmds.attributeQuery( at, n=o, ln=True) )
				self.helpfulMessage()
			else:
				Message('select some channels in the channel box')
	#load objects
	def loadobj(self, *button):
		sel = cmds.ls(sl=True)
		if len(sel) == 2:
			for p in self.GUI['obj']:
				check = p.partition('||')
				if check[0] in sel and check[-1] in sel:
					Message('Objects already loaded.')
					return
			ui = {}
			name = sel[0]+'||'+sel[1]
			parent = self.GUI['layout5']
			ui['button']=cmds.button(p=parent,l='X',bgc=[0.4,0.4,0.4],c=partial(self.removeEntry,name,'obj'))
			ui['layout'] = cmds.columnLayout( adjustableColumn=True, p=parent)
			ui['text'] = cmds.text( l=sel[0], p=ui['layout'], bgc=[0.2,0.2,0.2],h=20)
			ui['text'] = cmds.text( l=sel[1], p=ui['layout'], bgc=[0.2,0.2,0.2])
			self.GUI['obj'][name] = ui
			self.helpfulMessage()
		else:
			Message('Select two objects.' )

	def helpfulMessage(self): #ever changing helpful message
		msg = 'Hmm something wrong?'
		if len(self.GUI['obj']):
			if len(self.GUI['attr']):
				msg = 'Set Value Ranges.'
			else:
				msg = 'Load Attributes.' #no attributes loaded
		else:
			msg = 'Load up two Objects.' #no objects loaded

		cmds.text( self.GUI['text1'], e=True, l= msg )

	#run a scan
	def runscan(self, *button):
		if not self.working: #is the button for scanning or not?
			slider = mel.eval('$tempvar = $gPlayBackSlider')
			if cmds.timeControl( slider, rangeVisible = True, query=True ): #get time range
				timerange = cmds.timeControl ( slider, query = True, rangeArray = True )
			else:
				timerange = [cmds.currentTime(q=True)]

			########### grab values
			objects = []
			for ob in self.GUI['obj']:
				obj = ob.partition('||')
				if cmds.objExists(obj[0]) and cmds.objExists(obj[-1]):
					objects.append([ obj[0], obj[-1] ])
				else:
					self.removeEntry(ob,'obj')

			attributes = {}
			for at in self.GUI['attr'].copy(): #build attribute list
				(obj, dot, attr) = at.rpartition('.')
				if cmds.objExists(obj) and cmds.attributeQuery( attr, node = obj ,ex = True ):
					mini = cmds.floatField( self.GUI['attr'][at]['num1'], q=True, v=True)
					maxi = cmds.floatField( self.GUI['attr'][at]['num2'], q=True, v=True)
					if mini == maxi:
						maxi+=1
					if mini > maxi:
						mini, maxi = maxi, mini
					attributes[at] = [mini,maxi]
				else:
					self.removeEntry(at,'attr')

			steps = cmds.intFieldGrp(self.GUI['int1'],q=True,v1=True ) #steps value
			accuracy = cmds.floatFieldGrp(self.GUI['float1'],q=True,v1=True) # accuracy value

			if objects:
				if attributes:
					if len(attributes) < 4 or cmds.confirmDialog( title = 'HOLD UP...', message = 'Using this many attributes will be slow.\nAre you sure you want to do this?' ) == 'Confirm':
						 #dim GUI - turn off autokey
						 autokey = AutoKey(False)
						 cmds.button( self.GUI['button1'], e=True, en=False)
						 cmds.button( self.GUI['button2'], e=True, en=False)
						 cmds.button( self.GUI['button4'], e=True, l='Cancel!')

						 for t in range( (timerange[-1]-timerange[0]+1) ):
						 	cmds.currentTime( (t+timerange[0] ))
						 	self.working = attrSnap( objects, attributes, self.GUI['text1'], steps, accuracy)
						 	self.working.snapbrute()
						 	if not self.working: #if canceled, stop
						 		break
						 self.working = None
						 cmds.button( self.GUI['button1'], e=True, en=True)
						 cmds.button( self.GUI['button2'], e=True, en=True)
						 cmds.button( self.GUI['button4'], e=True, l='Run Scan!')
				else:
					Message('Load at least one attribute.' )
			else:
				Message('Load at least one pair of objects.' )
		else:
			self.working.working = False
			self.working = None
			cmds.button( self.GUI['button4'], e=True, l='Run Scan!')

#progress bar
class Progress(object):
	def __init__(self, text, length ):
		self.text = text
		self.length = int(length)
		self.label = '.'*self.length
		self.active = True
		self.step = 0
		self.previous = cmds.text( self.text, l=True, q=True ) #previous text
	def refresh(self, label): #update text
		if cmds.control(self.text,ex=True):
			cmds.text( self.text , l=label, e=True)
		cmds.refresh( cv = True )
	def update(self, inc):
		if self.active:
			old = int(self.step)
			self.step+=self.length*inc
			new = int(self.step)
			if self.step < self.length:
				if old < new:
					self.refresh( ((':'*(new+(new%1)))+self.label[new:self.length]) )
					return True
				return True
		self.cancel()
		return False
	def cancel(self):
		self.active = False
		self.__del__()
	def __del__(self):
		self.refresh(self.previous)

#########################

class AutoKey(object): #avoid autokey
	def __init__(self, state):
		self.state = cmds.autoKeyframe( st=True, q=True)
		cmds.autoKeyframe( st=state )
	def __del__(self):
		cmds.autoKeyframe( st=self.state )

def DeleteUI(ui): # delete UI if exists
	if cmds.control(ui, ex=True):
		cmds.deleteUI(ui, control=True)

def Message(msg): #create a popup menu
	cmds.confirmDialog( title = 'HOLD UP...', message=msg)

def VectorMath(method,p1,p2=None): #perform math on vector
	new = []
	for i in range(3):
		try:
			new.append( method(p1[i],p2[i]) )
		except TypeError:
			new.append( method(p1[i],p2) )
	return new

def Distance(p1, p2): # get distance between two vectors
	return m.sqrt(sum(VectorMath(lambda x,y: (y-x)**2, p1,p2)))

def ClosestPoint(p1, v1, p2, v2): #get closest point between two lines p = start point, v = velocity(or last point)
	dv = VectorMath(lambda x,y: y-x, v1, v2)
	dv2 = sum(p*q for p,q in zip(dv,dv))
	if dv2 < 0.00001: #tracks are parallel
		return 0.0
	orig = VectorMath(lambda x,y: x-y, p1, p2)
	return sum(p*q for p,q in zip(orig,dv)) / dv2
