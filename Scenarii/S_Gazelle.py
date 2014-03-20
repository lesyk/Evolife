##############################################################################
# EVOLIFE  www.dessalles.fr/Evolife                    Jean-Louis Dessalles  #
#            Telecom ParisTech  2014                       www.dessalles.fr  #
##############################################################################



""" EVOLIFE: Gazelle Scenario

Imagine two species, call them gazelles and lions. Gazelles have the genetically choice to invest energy in jumping vertically when lions approach. Of course, this somewhat reduces their ability to run away in case of pursuit. If lions prefer to chase non jumping gazelles, and poorly jumping ones among those who are jumping, show that investment in jumping evolves, at least for healthy individuals.	

	http://icc.enst.fr/IC/Intranet/projects/P08111502.html 

"""

	#=============================================================#
	#  HOW TO MODIFY A SCENARIO: read Default_Scenario.py		 #
	#=============================================================#

import random

import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests

from Evolife.Scenarii.Default_Scenario import Default_Scenario
from Evolife.Tools.Tools import error, noise_add, percent


######################################
# specific variables and functions   #
######################################


class Scenario(Default_Scenario):

	######################################
	# All functions in Default_Scenario  #
	# can be overloaded				  #
	######################################


	
	def genemap(self):
		""" Defines the name of genes and their position on the DNA.
		Accepted syntax:
		['genename1', 'genename2',...]:   lengths and coding are retrieved from configuration
		[('genename1', 8), ('genename2', 4),...]:   numbers give lengths in bits; coding is retrieved from configuration
		[('genename1', 8, 'Weighted'), ('genename2', 4, 'Unweighted'),...]:	coding can be 'Weighted', 'Unweighted', 'Gray', 'NoCoding'
		"""
		return ['GazelleThreshold', 'LionThreshold'] 	

	def phenemap(self):
		""" Defines the set of non inheritable characteristics
		"""
		# Elements in phenemap are integers between 0 and 100 and are initialized randomly
		# Lions and gazelles belong to the same species (!)
		# Their nature is decided at birth by the Phene 'Lion'
		return ['Lion', 'GazelleStrength', 'ChaseNumber']

	def gazelle(self, indiv):
		if indiv:
			return indiv.Phene_value('Lion') < self.Parameter('GazelleToLionRatio')	# typically more gazelles than lions 
		return False
	
	def initialization(self):
		self.Jumps = 0 

	def prepare(self, indiv):
		""" defines what is to be done at the individual level before interactions
			occur - Used in 'life_game'
		"""
		indiv.score(self.Parameter('PreyCost')*self.Parameter('GroupMaxSize')*self.Parameter('Rounds'), FlagSet=True)
		# if not self.gazelle(indiv):	indiv.Phene_value('ChaseNumber', 1)
		if not self.gazelle(indiv):	indiv.Phene_value('ChaseNumber', self.Parameter('Rounds'))

	def partner(self, indiv, members):
		""" a gazelle's partner must be a lion
		"""
		if self.gazelle(indiv):
			lions = [L for L in members if not self.gazelle(L)]
			if lions != []:	return random.choice(lions)
			else:			return None
		else:
			gazelles = [G for G in members if self.gazelle(G)]
			if gazelles != []:	return random.choice(gazelles)
			else:			return None
		
		
	def jump(self, gazelle):
		" Gazelles shows its strength only if it exceeds its signaling threshold "
		return  (gazelle.Phene_value('GazelleStrength') > gazelle.gene_relative_value('GazelleThreshold')	# Will
				 and gazelle.Phene_value('GazelleStrength') > self.Parameter('JumpThreshold'))				# Capacity
	
	def interaction(self, indiv1, indiv2):

		if indiv1 is None or indiv2 is None:	return
		if self.gazelle(indiv1):	(gazelle, lion) = (indiv1, indiv2)
		else:						(gazelle, lion) = (indiv2, indiv1)

		if lion.Phene_value('ChaseNumber') <= 0: return
		
		# A lion is approaching - The gazelle decides whether it should jump
		GazelleCurrentStrength = gazelle.Phene_value('GazelleStrength')
		GazelleJump = self.jump(gazelle)
		# the gazelle pays the price
		if GazelleJump:	GazelleCurrentStrength -= self.Parameter('JumpCost')
		
		# The lion makes its own decision
		if GazelleJump:	chase = (random.randint(0,100) > lion.gene_relative_value('LionThreshold'))
		else:	chase = True
		if chase:
			lion.Phene_value('ChaseNumber', lion.Phene_value('ChaseNumber')-1)
			# the lion is not impressed - the hunt begins
			if GazelleCurrentStrength > self.Parameter('CatchLevel'):
				# Unsuccessful hunt - Both partner get penalized
				lion.score(-self.Parameter('LostPreyCost'))
				gazelle.score(-self.Parameter('RunAwayCost'))
			else:	# Successful hunt
				lion.score(self.Parameter('HunterReward'))
				gazelle.score(-self.Parameter('PreyCost'))
				

	def couples(self, members):						
		"""	Lions and gazelles should not attempt to make babies together
			(because the selection of both subspecies operates on different scales)
		"""
		gazelles = [G for G in members if self.gazelle(G)]
		lions = [L for L in members if not self.gazelle(L)]
		Couples = Default_Scenario.couples(self, gazelles) + Default_Scenario.couples(self, lions)
		#print sorted(["%d%d" % (1*self.gazelle(C[0]),1*self.gazelle(C[1])) for C in Couples])
		return Couples
					
	def lives(self, members):
		""" Lions and gazelles should be evaluated separately
		"""
		gazelles = [G for G in members if self.gazelle(G)]
		lions = [L for L in members if not self.gazelle(L)]
		Default_Scenario.lives(self, gazelles)
		Default_Scenario.lives(self, lions)

	# def end_game(self, members):
		# jumpinggazelles = [G for G in members if self.gazelle(G) and self.jump(G)]
		# if jumpinggazelles:
			# self.Jumps = sum([self.jump(G) for G in jumpinggazelles]) / len(jumpinggazelles)
	
	def update_positions(self, members, groupLocation):
		" Allows to define spatial coordinates for individuals. "
		for m in enumerate(members):
			if self.gazelle(m[1]):	# gazelles in blue
				m[1].location = (groupLocation + m[1].Phene_value('GazelleStrength'), 
					10 + 25 * (self.jump(m[1]) != 0), 'blue')
			else:	m[1].location = (groupLocation + (100*m[0])/len(members), 1, 'red')	# lions in red

	def default_view(self):	return ['Field']
	
	def wallpaper(self, Window):
		" displays background image or colour when the window is created "
		# Possible windows are: 'Field', 'Curves', 'Genome', 'Log', 'Help', 'Trajectories', 'Network'
		if Window == 'Field':	return 'Scenarii/lion_gazelle_bkg.jpg'
		return Default_Scenario.wallpaper(self, Window)
		
	def local_display(self, ToBeDisplayed):
		" allows to diplay locally defined values "
		if ToBeDisplayed == 'Jumps':
			return self.Jumps
		return None	
					
	def display_(self):
		""" Defines what is to be displayed. 
			It should return a list of pairs (C,X)
			where C is the curve colour and X can be
			'best', 'average', 'n' (where n is any string processed by local_display, e.g. 'Jumps'),
			any gene name defined in genemap or any phene defined in phenemap
		"""
		return [('blue', 'GazelleThreshold'), ('red', 'LionThreshold')]
		

		
###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print __doc__ + '\n'
	SB = Scenario()
	raw_input('[Return]')
	
