##############################################################################
# EVOLIFE  www.dessalles.fr/Evolife                    Jean-Louis Dessalles  #
#            Telecom ParisTech  2014                       www.dessalles.fr  #
##############################################################################

##############################################################################
# Cocktail Party                                                             #
##############################################################################


""" Emergence of noise level and of discussion group at a 'cocktail party':
Individuals must talk louder to be heard, and may move to smaller discussion groups.
"""

import sys
sys.path.append('..')
sys.path.append('../../..')

import Evolife.Ecology.Observer				as EO
import Evolife.Scenarii.Parameters 			as EPar
import Evolife.Scenarii.Default_Scenario	as ED
import Evolife.QtGraphics.Evolife_Window 	as EW
import Evolife.QtGraphics.Curves			as EC
import Evolife.Ecology.Individual			as EI
import Evolife.Ecology.Group				as EG
import Evolife.Ecology.Population			as EP
import Landscapes

from Evolife.Tools.Tools import boost
print boost()   # A technical trick that sometimes provides impressive speeding up

	
import random
import math

# global functions
#	Sound level (voice) is displayed in blue shades
#	Noise level (due to others' voices) is displayed in red shades
def soundToColour(SoundLevel):	return 45-int(10*SoundLevel/101.0)	# 10 blue shades
def ColourToSound(Colour):		return int(((21-Colour)*100)/11)
def noiseToColour(NoiseLevel):	
	if NoiseLevel:	return 33-int(8*NoiseLevel/101.0)	# 8 red shades
	else:	return 2	# white colour == invisible


class Scenario(EPar.Parameters):
	def __init__(self):
		# Parameter values
		EPar.Parameters.__init__(self, CfgFile='_Params.evo')	# loads parameters from configuration file
		#############################
		# Global variables		    #
		#############################
		# add global parameters here if you don't want them to be in the configuration file
		# self.addParameter('MyParameter', Value)

		
class Cocktail_Observer(EO.Observer):
	""" Stores global variables for observation
	"""
	def __init__(self, Scenario):
		EO.Observer.__init__(self, Scenario) # stores global information
		self.CurrentChanges = []	# stores temporary changes
		self.recordInfo('CurveNames', [(3, 'Average Voice level')])

	def record(self, Info):
		# stores current changes
		# Info is a couple (InfoName, Position) and Position == (x,y)
		self.CurrentChanges.append(Info)

	def get_data(self, Slot):
		" this is called when display is required "
		if Slot == 'Positions':
			CC = self.CurrentChanges
			self.CurrentChanges = []
			return tuple(CC)
		else:	return EO.Observer.get_data(self, Slot)
			
			
	def get_info(self, Slot):
		if Slot == 'PlotOrders':
			return [(3, (self.StepId, int(self.Statistics['VoiceLevel']['average'][0])))]	# curve
		else:	return EO.Observer.get_info(self, Slot)

		
class LandCell(Landscapes.LandCell):
	" Defines what is stored at a given location "

	# Cell content is defined as a couple  (VoiceLevel, NoiseLevel)

	def __init__(self):
		self.VoidCell = (0, 0)
		self.setContent(self.VoidCell, Record=False)

	def free(self):	
		return (self.Content()[0] == 0)

		
class Landscape(Landscapes.Landscape):
	" Defines a 2D square grid "

	def __init__(self, Size):
		Landscapes.Landscape.__init__(self, Width=Size, CellType=LandCell)	# calls local LandCell definition

	def randomPosition(self):
		" picks an element of the grid with 'Content' in it "
		for ii in xrange(10):
			Row = random.randint(0,self.Size-1)
			Col = random.randint(0,self.Size-1)
			Cell = self.Ground[Col][Row]
			if Cell.free():	return (Col, Row)
			# print 'Cell at %d,%d is not free' % (Col, Row), Cell.Content()
		return None

	def attenuation(self, Level0, Pos0, Pos1):
		" Computes how noise emitted at Pos0 is perceived from a distance, at Pos1 "
		(sx, sy) = self.segment(Pos0, Pos1) 	# computes the shorter segment between the two position on the tore
		distance = sx + sy	# Manhattan distance
		if distance:
			# Level = (Level0 * Influence)/100 / math.log(1+distance,10)
			Level = (Level0 * Gbl.Parameter('Influence'))/100.0 / distance
		else:	Level = 0 # one is not noisy to oneself
		# print Level0, 'gives', int(Level), 'at distance', distance,
		return int(Level)
		
	def activate(self, Pos0):
		" Cell located at position 'Pos' has been modified and now produces its effect on neighbouring cells "
		Voice = self.Cell(Pos0).Content()[0]
		InfluenceRadius = (Gbl.Parameter('Influence')*Voice)//100	# distance at which maximal noisesource (100) is attenuated to 1
		# print 'radius around', Pos0, '= %d for Voice %d' % (InfluenceRadius, Voice)
		InfluenceRadius = min(InfluenceRadius, Gbl.Parameter('LandSize') // 2 - 1)
		for Pos1 in self.neighbours(Pos0, InfluenceRadius):
			if Pos1 == Pos0:	continue	# one is not noise to oneself
			NoiseDifference = self.attenuation(Voice, Pos0, Pos1)
			(Voice1, Noise1) = self.Content(Pos1)	# old values
			# print Pos1, 'goes from %d to %d' % (Noise, Noise+NoiseDifference)
			self.Modify(Pos1, (Voice1, min(100, Noise1+NoiseDifference)), check=False, record=False)
						
	def noiseLevel(self, (x,y)):	############ unused
		" computes the cumulative sound contribution of all sound sources "
		# sound is supposed to decrease proportionnally to the inverse of distance (true in dB)
		# Manhattan distance is considered
		Noise = 0
		# for ((Col,Row), Cell) in self.travel():	# too slow to embed iterators
		for Row in range(self.Size):
			for Col in range(self.Size):
				Cell = self.Ground[Col][Row]
				if Cell.Content() and Cell.Content()[0]:
					Noise += self.attenuation(Cell.Content()[0], (Col, Row), (x,y))
		return min(Noise, 100)
						
				
class Individual(EI.Individual):
	""" Defines individual agents
	"""
	def __init__(self, Scenario, ID=None):
		EI.Individual.__init__(self, Scenario, ID=ID)
		self.VoiceLevel = self.Scenario.Parameter('SNR')	# current sound level at which the individual is speaking
		self.Colour = soundToColour(self.VoiceLevel)	# colour reveals voice level
		# print 'creating', self.ID
		self.moves()	# gets a location
	
	def locate(self, NewPosition):
		" place individual at a specific location on the ground "
		# print 'locating', self, 'to', NewPosition
		(Voice, Noise) = Land.Content(NewPosition)
		if not Land.Modify(NewPosition, (self.VoiceLevel, Noise), check=False, record=True): # new position on Land
			# print Land.Ground[NewPosition[0]][NewPosition[1]].Content()
			return False		 # NewPosition is not available  
		if self.location and (NewPosition != self.location):
			# erasing previous position on Land
			(Voice, Noise) = Land.Content(self.location)	# old location must be erased
			if not Land.Modify(self.location, (0, Noise), check=False, record=True):
				print 'Error, agent %s badly placed' % self.ID
		self.location = NewPosition
		Observer.record((self.ID, self.location + (self.Colour, self.Scenario.Parameter('DotSize')))) # for ongoing display
		return True

	def erase(self):
		" erase individual from the ground "
		# print 'erasing', self
		if self.location:
			(Voice, Noise) = Land.Content(self.location)
			if not Land.Modify(self.location, (0, Noise), check=False, record=True):	# erase on Land
				print 'Error, agent %s was badly placed' % self.ID, self.location
			# sending negative colour to display to erase the agent
			# Observer.record((self.ID, self.location + (-self.Colour, self.Scenario.Parameter('DotSize'))))

	def soundChange(self, VoiceLevel):
		" changing voice level "
		# print '.',
		if VoiceLevel != self.VoiceLevel:
			# print 'changing voice level of %s from %d to %d' % (self, self.VoiceLevel, VoiceLevel)
			self.VoiceLevel = VoiceLevel
			# self.erase()	# moves away from Land
			self.Colour = soundToColour(VoiceLevel)
			# print self
			return self.locate(self.location)
		return False

	def voiceLevel(self):
		" Computes voice level to speak above noise "
		if self.location:
			oldLevel = self.VoiceLevel
			# Newlevel = min(100, Land.noiseLevel(self.location, self.Scenario.Parameter('Influence')) + self.Scenario.Parameter('SNR'))
			Newlevel = min(100, Land.Content(self.location)[1] + self.Scenario.Parameter('SNR'))
			if not self.soundChange(Newlevel) and Newlevel != oldLevel:
				print 'Error: voice level change impossible for %s from %d to %d' % (self, oldLevel, Newlevel) 
				return False
			return (Newlevel != oldLevel)
	
	def decisionToMove(self):
		# to be rewritten
		if self.location is None:	return False # may happen if there is no room left	
		return False
	
	def moves(self, Position=None):
		# print 'moving', self
		if Position:
			return self.locate(Position)
		else:
			# pick a random location and go there
			for ii in xrange(10): # 10 chances to find a free location
				Landing = Land.randomPosition()
				if Landing and self.locate(Landing):
					return True
			# print "Unable to move to", Position,
			return False

	def dies(self):
		" get off from the Land when dying "
		self.erase()
		EI.Individual.dies(self)
		
	def observation(self, Examiner):
		# this information will be sent to the Observer, which will perform statistics
		Examiner.store('VoiceLevel',(self.VoiceLevel,))
			
	def __repr__(self):
		" string representation of an individual "
		return "(%s,%s,%d) --> " % (self.ID, self.Colour, self.VoiceLevel) + str(self.location)

class Group(EG.Group):
	# The group is a container for individuals.
	# Individuals are stored in self.members

	def createIndividual(self, ID=None, Newborn=True):
		# calling local class 'Individual'
		Indiv = Individual(self.Scenario, ID=self.free_ID())	# call to local class 'Individual'
		# Individual creation may fail if there is no room available
		if Indiv.location == None:	return None
		return Indiv
					
	
class Population(EP.Population):
	" defines the population of agents "
	
	def __init__(self, Scenario, Observer):
		" creates a population of agents "
		EP.Population.__init__(self, Scenario, Observer)	# creates one group by callng 'createGroup'
		print "population size: %d" % self.popSize
		self.Changes = 0  # counts the number of times agents have changed their voice
		self.CallsSinceLastChange = 0  # counts the number of times agents were proposed to move since last actual move

	def createGroup(self, ID=0, Size=0):
		return Group(self.Scenario, ID=ID, Size=Size)	# Calls local class 'Group'

	def One_Decision(self):
		""" This function is repeatedly called by the simulation thread.
			One agent is randomly chosen and decides what it does
		"""

		EP.Population.one_year(self)	# performs statistics
		
		# for agent in self.members():
		agent = self.selectIndividual()	# agent who will play the game	
		self.CallsSinceLastChange += 1
		if agent.voiceLevel():	
			# Voice level has changed
			self.Changes += 1
			self.CallsSinceLastChange = 0

		if self.CallsSinceLastChange > 50 * self.popSize:
			return False	# situation is probably stable

		Land.update()	# Let's update noise

		if self.Scenario.Parameter('NoiseDisplay') and (self.year % self.Scenario.Parameter('NoiseDisplay')) == 0:
			for (Position, Cell) in Land.travel():
				Observer.record(('C%d_%d' % Position, Position + (noiseToColour(Cell.Content()[1]), 4))) # for display
			# redisplaying agents
			for Indiv in self.members():
				Observer.record((Indiv.ID, Indiv.location + (-Indiv.Colour, self.Scenario.Parameter('DotSize'))))	# negative colour deletes the graphic avatar
				Observer.record((Indiv.ID, Indiv.location + (Indiv.Colour, self.Scenario.Parameter('DotSize'))))	# recreate the avatar

		# Selecting one agent that is allowed to move
		# Uncomment the following two lines to see individuals moving
		# self.selectIndividual().moves()
			  
		return True
			


if __name__ == "__main__":
	print __doc__

	
	#############################
	# Global objects			#
	#############################
	Gbl = Scenario()
	Observer = Cocktail_Observer(Gbl)	  # Observer contains statistics
	Land = Landscape(Gbl.Parameter('LandSize'))	  # 2D square grid
	# Land.setAdmissible(range(101))	# sound levels
	Pop = Population(Gbl, Observer)   
	
	# Observer.recordInfo('BackGround', 'white')
	Observer.recordInfo('FieldWallpaper', 'white')
	
	EW.Start(Pop.One_Decision, Observer, Capabilities='RPC')

	print "Bye......."
	
__author__ = 'Dessalles'
