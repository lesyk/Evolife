##############################################################################
# EVOLIFE  www.dessalles.fr/Evolife                    Jean-Louis Dessalles  #
#            Telecom ParisTech  2014                       www.dessalles.fr  #
##############################################################################

##############################################################################
# Example to show how to use Evolife's ecology (population and groups)       #
##############################################################################


""" This class defines a 2D square grid on which agents can move
"""

import random
		
class MySet:
	" Defines a list without duplicates "
	def __init__(self): self.reset()

	def reset(self):	self.Content = []

	def append(self, Item):
		if not Item in self.Content:	self.Content.append(Item)

	def remove(self, Item): self.Content.remove(Item) 	# Item is supposed to be present		
	
	def list(self):	return self.Content

class LandCell:
	""" Defines what's in one location on the ground
	"""
	def __init__(self, Content=None):
		self.VoidCell = None
		self.setContent(Content, Record=False)

	def Content(self):	return self.History[-1]	# History should never get empty

	def free(self):	return (self.Content() == self.VoidCell)
	
	def clean(self):	return self.setContent(self.VoidCell)
	
	def setContent(self, Content=None, Record=False):
		if not Record:	self.History = [self.VoidCell]	# contains the history of successive contents
		if Content != self.Content():	
			self.History.append(Content)
			return True
		return False

	def history(self):
		while(len(self.History) > 1):	# always keep 'None' at the bottom of 'History'
			yield self.History.pop(1)

	def forget(self):
		self.setContent(self.Content())	# erases history
		
class Landscape:
	""" A 2-D square grid 
	"""
	def __init__(self, Width=100, Height=0, CellType=LandCell):
		self.ContentType = None	# may constrain what content can be
		self.Size = Width	
		self.Width = Width
		if Height > 0:	self.Height = Height
		else:	self.Height = self.Size
		self.Ground = [[CellType() for y in xrange(self.Height)] for x in xrange(self.Width)]
		self.ActiveCells = MySet()   # list of Positions that have been modified
		self.Statistics = {}	# will contain lists of cells for each content type

	def setAdmissible(self, ContentType):	
		self.ContentType = ContentType
		self.statistics()	# builds lists of cell per content
	
	def Admissible(self, Content):
		if self.ContentType:	return (Content in self.ContentType)
		return True
		
	def ToricConversion(self, (x,y)):
		# toric landscape
		return (x % self.Width, y % self.Height)
	
	def Modify(self, (x,y), NewContent, check=True, record=False):
		" Changes content at a location "
		# print 'Modyfying', (x,y), NewContent
		if check:	
			if NewContent:	# put only admissible content only at free location
				if not self.Admissible(NewContent) or not self.Ground[x][y].free():
					return False
			else: # erase only when content is already there
				if self.Ground[x][y].free():	return False
		if self.Ground[x][y].setContent(NewContent, record) and record:
			# only activate cells that have actually changed state
			self.ActiveCells.append((x,y))
		return True

	def Content(self, (x,y)):
		return self.Ground[x][y].Content()

	def Cell(self, (x,y)):
		return self.Ground[x][y]
		
	def free(self, (x,y)):
		return self.Ground[x][y].free()
	
	def neighbours(self, (x,y), Radius=1):
		# returns the list of neighbouring cells
		L = []
		for distx in range(-Radius, Radius+1):
			for disty in range(-Radius, Radius+1):
				L.append(self.ToricConversion((x + distx, y + disty)))
		return L

	def segment(self, (x0,y0), (x1,y1)):
		" computes the shorter segment between two points on the tore "
		(vx,vy) = self.ToricConversion((x0-x1, y0-y1))
		(wx,wy) = self.ToricConversion((x1-x0, y1-y0))
		return (min(vx,wx), min(vy,wy))
		
	def InspectNeighbourhood(self, Pos, Radius):
		""" Makes statistics about local content 
			Returns a dictionary by Content.
			The center position is omitted
		"""
		Neighbourhood = self.neighbours(Pos, Radius)
		if self.ContentType:
			LocalStatistics = dict(map(lambda x: (x,0), self.ContentType))	# {Content_1:0, Content_2:0...}
		else:	LocalStatistics = dict()
		for NPos in Neighbourhood:
			if NPos == Pos: continue
			if self.Content(NPos):	
				if self.Content(NPos) in LocalStatistics:	LocalStatistics[self.Content(NPos)] += 1
				else: LocalStatistics[self.Content(NPos)] = 1
		return LocalStatistics

	def statistics(self):
		" scans ground and builds lists of cells depending on Content "
		if self.ContentType:
			self.Statistics = dict(map(lambda x: (x,[]), self.ContentType + [None]))	# {Content_1:[], Content_2:[]..., None:[]}
		for (Pos, Cell) in self.travel():
			if Cell.Content() in self.Statistics:
				self.Statistics[Cell.Content()].append(Pos)
			else:
				self.Statistics[Cell.Content()] = [Pos]

	def update(self):
		" updates the delayed effect of cells that have been modified "
		# print '\n%d active cells' % len(self.ActiveCells.list())
		for Pos in self.ActiveCells.list():
			self.activate(Pos)	# active cells perform their action
		# setting active cells to its last state
		for Pos in self.ActiveCells.list():
			self.Cell(Pos).forget()	# erases history, keeps last state
		self.ActiveCells.reset()

	def activate(self, Pos):
		" Cell located at position 'Pos' has been modified and now produces its effect, possibly on neighbouring cells "
		for State in self.Cell(Pos).history():
			pass	# to be overloaded	
				
	def randomPosition(self, Content=None, check=False):
		" picks an element of the grid with 'Content' in it "
		if check and self.Statistics:
			for ii in xrange(10): # as Statistics may not be reliable
				if self.Statistics[Content]:
					Pos = random.choice(self.Statistics[Content])
					if self.Content(Pos) == Content:	# should be equal if statistics up to date
						return Pos
			# at this point, no location found with Content in it - Need to update
			self.statistics()
		else:	# blind search
			for ii in xrange(10):
				Row = random.randint(0,self.Height-1)
				Col = random.randint(0,self.Width-1)
				if check: 
					if self.Content((Col,Row)) == Content:	return (Col, Row)
				else: return (Col, Row)
		return None		  

	def travel(self):
		" Iteratively returns Cells of the grid "
		Pos = 0	# used to travel over the grid
		for Pos in xrange(self.Height * self.Width):
			Col = Pos % self.Width
			Row = Pos // self.Width
			try:
				yield ((Col,Row), self.Ground[Col][Row])
			except IndexError:
				print self.Width, self.Height,
				print Col, Row, Pos
				raise
		   

class LandCell_3D(LandCell):
	""" Same as LandCell, plus a third dimension
	"""
	def __init__(self, Altitude=0, Content=None):
		LandCell.__init__(self, Content=Content)
		self.Altitude = Altitude
		
class Landscape_3D(Landscape):
	""" Same as Landscape, but stores a third dimension in cells
	"""
	def __init__(self, Altitudes=[], AltitudeFile='', CellType=LandCell_3D):
		Height = len(Altitudes)	# number of rows
		if Height == 0:
			# Altitudes are retrieved from file
			Rows = open(AltitudeFile).readlines()
			# Altitudes = [Row.split() for Row in Rows if len(Row.split()) > 1 ]
			Altitudes = [map(int,Row.split()) for Row in Rows]
			Height = len(Altitudes)	# number of rows
		Width = len(Altitudes[0])	# assuming rectangular array correct
		Landscape.__init__(self, Width=Width, Height=Height, CellType=CellType)
		for ((Col,Row), Cell) in self.travel():
			try:
				Cell.Altitude = Altitudes[Height-1-Row][Col]
			except IndexError:
				print Width, Height,
				print Col, Row
				raise
	

			   
if __name__ == "__main__":
	print __doc__

	
	
__author__ = 'Dessalles'
