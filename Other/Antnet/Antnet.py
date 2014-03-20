##############################################################################
# EVOLIFE  www.dessalles.fr/Evolife                    Jean-Louis Dessalles  #
#            Telecom ParisTech  2014                       www.dessalles.fr  #
##############################################################################

##############################################################################
# Ants                                                                       #
##############################################################################

""" Antnet:
'Ants' travel through the network.
Messages choose nodes ants come from.
"""



import sys
from time import sleep
import random
		
sys.path.append('..')
sys.path.append('../../..')
import Evolife.Scenarii.Parameters			as EPar
import Evolife.Ecology.Observer				as EO
import Evolife.Ecology.Individual			as EI
import Evolife.Ecology.Group				as EG
import Evolife.Ecology.Population			as EP
import Evolife.QtGraphics.Evolife_Window	as EW
import Evolife.Tools.Tools					as ET
import Landscapes

print ET.boost()	# significantly accelerates python on some platforms


# two functions to convert from complex numbers into (x,y) coordinates
c2t = lambda c: (int(round(c.real)),int(round(c.imag))) # converts a complex into a couple
t2c = lambda (x,y): complex(x,y) # converts a couple into a complex

#################################################
# Aspect of ants, food and pheromons on display
#################################################
AntAspect = ('black', 6)	# 6 = size
AntAspectWhenOld = ('red1', 7)	# 6 = size
FoodDepletedAspect = ('brown', 14)
PPAspect = (17, 2)	# 17th colour
NPAspect = ('blue', 2)
	
class Antnet_Observer(EO.Observer):
	""" Stores global variables for observation
	"""
	def __init__(self, Scenario):
		EO.Observer.__init__(self, Scenario)
		self.CurrentChanges = []	# stores temporary changes
		self.recordInfo('CurveNames', [('yellow', 'Year (each ant moves once a year on average)\n\t\tx\n\t\tAmount of food collected')])
		self.FoodCollected = 0

	def recordChanges(self, Info):
		# stores current changes
		# Info is a couple (InfoName, Position) and Position == (x,y) or a longer tuple
		self.CurrentChanges.append(Info)

	def get_info(self, Slot):
		" this is called when display is required "
		if Slot == 'PlotOrders':	return [('yellow', (self.StepId//Gbl.Parameter('PopulationSize'), self.FoodCollected))]	# curve
		else:	return EO.Observer.get_info(self, Slot)
		
	def get_data(self, Slot):
		if Slot == 'Positions':
			CC = self.CurrentChanges
			# print CC
			self.CurrentChanges = []
			return tuple(CC)
		else:	return EO.Observer.get_data(self, Slot)
		
class LandCell(Landscapes.LandCell):
	""" Defines what's in one location on the ground
	"""

	# Cell content is defined as a triple  (Food, NegativePheromon, PositivePheromon)

	def __init__(self, F=0, NP=0, PP=0):
		self.VoidCell = (0, 0, 0)	# content of a void cell
		self.setContent((F,NP,PP))

	def clean(self):	
		return self.setContent((self.Content()[0],0,0))


class Node:
	"""	Defines a node of the network
	"""
	def __init__(self, Name, Location):
		self.Name = Name
		self.Location = Location
		
class Network:
	"""	Defines a network as a graph
	"""
	def __init__(self, Size, NbNodes=0):
		if NbNodes:
			self.Nodes = [Node('N%n' % i, (random.randint(0,Size), random.randint(0,Size))) for n in range(NbNodes)]
			self.Links = []
			if NbNodes > 1:
				for n in self.Nodes:
					OtherNodes = self.Nodes[:].remove(n)	# does not need to be efficient
					self.Links.append((n, random.choice(OtherNodes)))
					self.Links.append((n, random.choice(OtherNodes)))
			self.Links = list(set(self.Links))	# to remove duplicates
		else:
			self.Nodes = [
						Node('A', (int(Size*0.25), int(Size*0.25))),
						Node('B', (int(Size*0.25), int(Size*0.75))),
						Node('C', (int(Size*0.75), int(Size*0.75))),
						Node('D', (int(Size*0.75), int(Size*0.25))),
						Node('E', (int(Size*0.5), int(Size*0.5)))	]
			self.Links = [(self.Nodes[i], self.Nodes[j]) for (i,j) in \
				[(0,1), (1,2), (2,3), (3,0), (0,5), (1,5), (2,5), (3,5), (5,0), (5,1), (5,2), (5,3)]]

	def Neighbours(self, Node):
		if not Node in self.Nodes:	ET.error('Network', 'Non existing node has no neighbours')
		return [n for n in self.Nodes if (Node, n) in self.Links]
			
	
	
class Landscape(Landscapes.Landscape):
	""" A 2-D grid with cells that contains food or pheromone
	"""
	def __init__(self, Size, NbFoodSources):
		Landscapes.Landscape.__init__(self, Size, CellType=LandCell)
		def Network

	def 
	   
	   
class Ant(EI.Individual):
	""" Defines individual agents
	"""
	def __init__(self, Scenario, IdNb, InitialPosition):
		EI.Individual.__init__(self, Scenario, ID=IdNb)
		self.Colony = InitialPosition # Location of the colony nest
		self.location = InitialPosition
		self.PPStock = Gbl.Parameter('PPMax') 
		self.Action = 'Move'
		self.moves()

	def Sniff(self):
		" Looks for the next place to go "
		Neighbourhood = Land.neighbours(self.location, self.Scenario.Parameter('SniffingDistance'))
		random.shuffle(Neighbourhood) # to avoid anisotropy
		acceptable = None
		best = -Gbl.Parameter('Saturation')	# best == pheromone balance found so far
		for NewPos in Neighbourhood:
			# looking for position devoid of negative pheromon
			if NewPos == self.location: continue
			if Land.food(NewPos) > 0:
				# Food is always good to take
				acceptable = NewPos
				break
			found = Land.ppheromone(NewPos)   # attractiveness of positive pheromone
			found -= Land.npheromone(NewPos)   # repulsiveness of negative pheromone
			if found > best:			  
				acceptable = NewPos
				best = found
		return acceptable

	def returnHome(self):
		" The ant heads toward the colony "
		Direction = t2c(self.Colony) - t2c(self.location)   # complex number operation
		Distance = abs(Direction)
		if Distance >= Gbl.Parameter('SniffingDistance'):
			# Negative pheromone
			if Gbl.Parameter('NPDeposit'):
				Land.npheromone(self.location, Gbl.Parameter('NPDeposit')) # marking current position as visited with negative pheromone
			# Positive pheromone
			Land.ppheromone(self.location, self.PPStock) # marking current posiiton as interesting with positive pheromone
			Direction /= Distance	# normed vector
			# MaxSteps = int(Gbl.Parameter('LandSize') / 2 / Distance)	# 
			Decrease = int(self.PPStock / Distance)	# Linear decrease
			self.PPStock -= Decrease
			# if self.PPStock <= Gbl.Parameter('PPMin'):   self.PPStock = Gbl.Parameter('PPMin')	# always lay some amount of positive pheromone
			self.location = c2t(t2c(self.location) + 2 * Direction)	# complex number operation
			self.location = Land.ToricConversion(self.location)		# landscape is a tore
			Observer.recordChanges((self.ID, self.location + AntAspectWhenLaden)) # for ongoing display of ants
		else:
			# Home reached
			self.PPStock = Gbl.Parameter('PPMax') 
			self.Action = 'Move'
		
	def moves(self):
		""" Basic behavior: move by looking for neighbouring unvisited cells.
			If food is in sight, return straight back home.
			Lay down negative pheromone on visited cells.
			Lay down positive pheromone on returning home.
		"""
		if self.Action == 'BackHome':
			self.returnHome()
		else:
			NextPos = self.Sniff()
			# print self.ID, 'in', self.location, 'sniffs', NextPos
			if NextPos is None or random.randint(0,100) < Gbl.Parameter('Exploration'): 
				# either all neighbouring cells have been visited or in the mood for exploration
				NextPos = c2t(t2c(self.location) + complex(random.randint(-1,1),random.randint(-1,1)))
				NextPos = Land.ToricConversion(NextPos)
			# Marking the old location as visited
			if Gbl.Parameter('NPDeposit'):
				Land.npheromone(self.location, Gbl.Parameter('NPDeposit'))
				# Observer.recordChanges(('NP%d_%d' % self.location, self.location + NPAspect)) # for ongoing display of negative pheromone
			self.location = NextPos
			if Land.food(self.location) > 0:	
				Land.food(self.location, -1)	# consume one unit of food
				Observer.FoodCollected += 1
				self.Action = 'BackHome'	# return when having found food
			Observer.recordChanges((self.ID, self.location + AntAspect)) # for ongoing display of ants

	def position(self):
		return c2t(self.Position)

		
class Group(EG.Group):
	# The group is a container for individuals.
	# Individuals are stored in self.members

	def __init__(self, Scenario, ColonyPosition, ID=1, Size=100):
		self.ColonyPosition = ColonyPosition
		EP.Group.__init__(self, Scenario, ID=ID, Size=Size)
		
	def createIndividual(self, ID=None, Newborn=True):
		# calling local class 'Individual'
		return Ant(self.Scenario, self.free_ID(Prefix='A'), self.ColonyPosition)	# call to local class 'Ant'
					
					
class Population(EP.Population):
	" defines the population of agents "
	
	def __init__(self, Scenario, Observer, ColonyPosition):
		self.ColonyPosition = ColonyPosition
		EP.Population.__init__(self, Scenario, Observer)
		" creates a population of ant agents "
		self.AllMoved = 0  # counts the number of times all agents have moved on average
		self.SimulationEnd = 400 * self.popSize
		# allows to run on the simulation beyond stop condition

	def createGroup(self, ID=0, Size=0):
		return Group(self.Scenario, self.ColonyPosition, ID=ID, Size=Size)	# Call to local class 'Group'
		
	def One_Decision(self):
		""" This function is repeatedly called by the simulation thread.
			One ant is randomly chosen and decides what it does
		"""
		EP.Population.one_year(self)	# performs statistics
		ant = self.selectIndividual()
		ant.moves()
		Moves = self.year // self.popSize	# One step = all Walkers have moved once on average
		# print (self.year, self.AllMoved, Moves),
		if Moves > self.AllMoved:
			Land.evaporation()
			self.AllMoved = Moves
		if (Land.foodQuantity() <= 0):	self.SimulationEnd -= 1
		return self.SimulationEnd > 0	 # stops the simulation when True

		
if __name__ == "__main__":
	print __doc__

	#############################
	# Global objects			#
	#############################
	Gbl = EPar.Parameters('_Params.evo')	# Loading global parameter values
	Observer = Ant_Observer(Gbl)   # Observer contains statistics
	Land = Landscape(Gbl.Parameter('LandSize'), Gbl.Parameter('NbFoodSources'))
	Pop = Population(Gbl, Observer, (Gbl.Parameter('LandSize')//2, Gbl.Parameter('LandSize')//2))   # Ant colony
	Observer.recordChanges(('Dummy',(Gbl.Parameter('LandSize'), Gbl.Parameter('LandSize'), 0, 1)))	# to resize the field

	Observer.recordInfo('FieldWallpaper', 'Grass1.jpg')
	# Observer.recordInfo('FieldWallpaper', 'white')

	EW.Start(Pop.One_Decision, Observer, Capabilities='RPC')

	print "Bye......."
	sleep(1.0)
##	raw_input("\n[Return]")

__author__ = 'Dessalles'
