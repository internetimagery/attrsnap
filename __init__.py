from functools import partial
import maya.cmds as cmds
import maya.mel as mel
import math as m

# Created by Jason Dixon 14/03/14
# http://internetimagery.com

	#obj = [object, object]
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
		self.progress = progress( text, 30 )
		#create locators constrainted to objects
		if len(obj) == 2:
			for o in obj:
				loc = cmds.spaceLocator()[0]
				cmds.parentConstraint( o , loc )
				self.loc.append( {'loc':loc, 'obj': o} )
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
		for loc in self.loc:
			cmds.delete( loc['loc'] )

	#snap attributes with brute force
	def snapbrute(self):
		attr = self.attr.keys() #generate list of attributes
		olddist = 999 #distance last time
		longest = 0
		for at in self.attr: #get the largest range
			longest = max(longest, (self.attr[at]['max']-self.attr[at]['min']) )
		for step in range(20): #work out how many steps it will take to reach accuracy
			longest*=(1.0/self.steps)*2
			if longest < self.accuracy:
				break
		combination = 0
		for i in range(len(attr)): #work out the number of combinations
			combination+=self.steps**(len(attr)-i)
		self.prog = 1.0 / (combination*step) #progress bar step
		for i in range(step):
			(current, snap, newdist) = self.runbrute(0, attr, self.attr, {}, {}, 999 )
			for at in snap: #update limits
				self.attr[at] = snap[at]
			olddist = newdist
		for at in self.attr: #set the attributes
			cmds.setAttr( at, ((self.attr[at]['max']-self.attr[at]['min'])*0.5+self.attr[at]['min']) )
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
	def runbrute(self, i, at, limit, current, snap, dist ):
		if i < len(at) and self.working: #make sure we don't loop forever
			step = (limit[at[i]]['max']-limit[at[i]]['min'])*(1.0/(self.steps-1)) #get search incriment
			for s in range( self.steps ): #run through each step
				self.progress.update( self.prog )
				s=limit[at[i]]['min']+s*step #each step
				cmds.setAttr( at[i], s ) #set attribute
				#get range to store
				if s <= limit[at[i]]['min']: #don't go below lower boundary
					r = {'min':s,'max':(s+(step*2))}
				elif s >= limit[at[i]]['max']: # or upper boundary
					r = {'min':(s-(step*2)),'max':s}
				else:
					r = {'min':(s-step),'max':(s+step)}
				current[at[i]] = r #update current combination
				(current, snap, dist) = self.runbrute( (i+1), at, limit, current, snap, dist )
				loc = []
				for l in self.loc:
					loc.append( cmds.getAttr( (l['loc']+'.translate') )[0] )
				test = self.measure( loc[0], loc[1] )
				if test < dist: #are we closer than before?
					dist = test
					snap = current.copy()

		return current, snap, dist
	#do math on lists
	def math(self, pos1, pos2, method):
		new = []
		for i in range(len(pos1)):
			new.append( method( pos1[i], pos2[i] ) )
		return new
	#measure distance
	def measure(self, p1, p2):
		d=0
		for i in range(len(p1)):
			d+=(p2[i]-p1[i])**2
		return m.sqrt(d)

########################################

class GUI(object):
	def __init__(self):
		#DATA
		self.working = None #currently running though?
		self.GUI = {} #gui elements
		self.GUI['obj'] = {} #recorded objects
		self.GUI['attr1'] = [] #recorded attribute entries
		self.GUI['attr'] = {}

		self.GUI['window'] = cmds.window( title = 'Attribute Snap', rtf=True, s=False)
		self.GUI['layout3'] = cmds.rowColumnLayout( nc=2 )
		self.GUI['layout1'] = cmds.columnLayout( adjustableColumn=True, w=120 ) #buttons in here
		self.GUI['text1'] = cmds.text( label = 'Load up two Objects.', h=20 )
		self.GUI['button1'] = cmds.button( label = 'Load Objects', h=30, c=self.load )
		self.GUI['float1'] = cmds.floatFieldGrp( el = 'Accuracy', v1=(0.001), cw2 = (60,60), pre=3 )
		self.GUI['int1'] = cmds.intFieldGrp( el = 'Steps', v1=(10), cw2 = (60,60) )
		self.GUI['button4'] = cmds.button( label = 'Run Scan!', c= self.runscan, height = 60 )
		cmds.setParent('..')
		self.GUI['layout4'] = cmds.columnLayout( adjustableColumn=True ) # objects and attributes in here
		self.GUI['text2'] = cmds.text(l='Objects' , h=20)
		cmds.separator()
		self.GUI['layout5'] = cmds.columnLayout( adjustableColumn=True, bgc=[0.2,0.2,0.2] ) # objects in here
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
		entry = {}

		if cmds.attributeQuery(at,n=o,mne=True):#check if there is a minimum range
			entry['min'] = cmds.attributeQuery(at,n=o,min=True)[0]
		elif 'rotate' in at:
			entry['min'] = -360.0
		else:
			entry['min'] = -999.0
		if cmds.attributeQuery(at,n=o,mxe=True):#check if there is a maximum range
			entry['max'] = cmds.attributeQuery(at,n=o,max=True)[0]
		elif 'rotate' in at:
			entry['max'] = 360.0
		else:
			entry['max'] = 999.0
		#create list entry
		p = self.GUI['layout2']
		entry['entry'] = []
		entry['entry'].append( cmds.button(l='X',h=20,p=p,bgc=[0.4,0.4,0.4],c=partial(self.attrRemove,name)) )
		entry['entry'].append( cmds.text(l=o,p=p,bgc=[0.2,0.2,0.2] ))
		entry['entry'].append( cmds.text(l=(cmds.attributeQuery(at,n=o,nn=True)),p=p,bgc=[0.2,0.2,0.2] ))
		entry['entry'].append( cmds.floatField(v=entry['min'],pre=3,p=p,cc=partial(self.attrUpdate, 'min', name))) #min
		entry['entry'].append( cmds.floatField(v=entry['max'],pre=3,p=p,cc=partial(self.attrUpdate, 'max', name))) #max

		self.GUI['attr'][name] = entry

	#update values as they change
	def attrUpdate(self, con, at, val):
		self.GUI['attr'][at][con] = val

	#delete attribute from list
	def attrRemove(self, at, *arg):
		for l in self.GUI['attr'][at]['entry']:
			cmds.deleteUI( l, control=True )
		del self.GUI['attr'][at]

	#update value
	def update(self, gui, val):
		if gui == 'float1':
			self.accuracy = val
		elif gui=='int1':
			self.steps = val

	#load things
	def load(self, blah):
		if self.working: #cancel button
			self.working.working = False
			self.working = None
		else:
			if self.GUI['obj']: #load attribute button
				self.loadattr()
			else:
				self.loadobj() # load object
	#load up attributes
	def loadattr(self):
		obj = cmds.ls(sl=True)
		if obj:
			attr = cmds.channelBox( 'mainChannelBox' , sma = True, query = True )
			if attr:
				for o in obj:
					for at in attr:
						if cmds.attributeQuery( at, node = o ,ex = True ): #check the channel exists
							self.attrCreate( o, cmds.attributeQuery( at, n=o, ln=True) )
	#load objects
	def loadobj(self):
		sel = cmds.ls(sl=True)
		if len(sel) == 2:
			if self.GUI['obj']:
				clear = cmds.layout( self.GUI['layout5'], q=True, ca=True)
				for c in clear:
					cmds.deleteUI( ( self.GUI['layout5']+'|'+c ), control = True )
			for o in sel:
				self.GUI['obj'][o] = cmds.text( l=o, p=self.GUI['layout5'])
			cmds.text( self.GUI['text1'], e=True, label = 'Load Attributes.' )
			cmds.button( self.GUI['button1'], e=True, label = 'Load Attribute' )
		else:
			cmds.confirmDialog( title = 'Darn...', message = 'Select two objects.' )

	#run a scan
	def runscan(self, arg):
		if not self.working:
			slider = mel.eval('$tempvar = $gPlayBackSlider')
			if cmds.timeControl( slider, rangeVisible = True, query=True ): #get time range
				timerange = cmds.timeControl ( slider, query = True, rangeArray = True )
			else:
				timerange = [cmds.currentTime(q=True)]

			if self.GUI['attr']: #warning if using many attributes
				if len(self.GUI['attr']) < 4 or cmds.confirmDialog( title = 'HOLD UP...', message = 'Using this many attributes will be slow.\nAre you sure you want to do this?' ) == 'Confirm':
					#run script
					cmds.button( self.GUI['button1'], e=True, l='Cancel')
					autokey = cmds.autoKeyframe( st=True, q=True) # we're going to turn off autokey. So record if it was on before to turn it back on when done
					cmds.autoKeyframe( st=False )
					for t in range( (timerange[-1]-timerange[0]+1) ):
						cmds.currentTime( (t+timerange[0] ))
						self.working = attrSnap( (self.GUI['obj'].keys()), self.GUI['attr'], self.GUI['text1'], (cmds.intFieldGrp(self.GUI['int1'],q=True,v1=True )), (cmds.floatFieldGrp(self.GUI['float1'],q=True,v1=True)))
						self.working.snapbrute()
						if not self.working: #if canceled, stop
							break
					cmds.autoKeyframe( st=autokey )
					self.working = None
					cmds.button( self.GUI['button1'], e=True, l='Load Attribute')
			else:
				if self.GUI['obj']:
					cmds.confirmDialog( title = 'Darn...', message = 'Load at least one attribute.' )
				else:
					cmds.confirmDialog( title = 'Darn...', message = 'Load two objects.' )

#progress bar
class progress(object):
	def __init__(self, text, length ):
		self.text = text
		self.length = int(length)
		self.label = '.'*self.length
		self.active = True
		self.step = 0
		self.previous = cmds.text( self.text, l=True, q=True ) #previous text
	def refresh(self, label): #update text
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
