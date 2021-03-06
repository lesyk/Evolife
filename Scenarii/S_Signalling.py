##############################################################################
# EVOLIFE  www.dessalles.fr/Evolife                    Jean-Louis Dessalles  #
#            Telecom ParisTech  2014                       www.dessalles.fr  #
##############################################################################



##############################################################################
#  S_Signalling                                                              #
##############################################################################


""" EVOLIFE: 'Signalling' Scenario:
			Individual A signals its competence
			Other individuals may choose to join A based on that competence.
			A benefits from their joining (e.g. protection)
			They get a profit correlated with A's competence 
			(think of it as an ability to anticipate danger)
"""
	#=============================================================#
	#  HOW TO MODIFY A SCENARIO: read Default_Scenario.py		 #
	#=============================================================#



import random

import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests
	
from Evolife.Tools.Tools import percent, noise_add, error
from Evolife.Scenarii.Default_Scenario import Default_Scenario

######################################
# specific variables and functions   #
######################################

class Interactions(object):
	" A few functions used to rule interactions between agents "

	def __init__(self, Parameters, FCompetence):
		self.Parameters = Parameters  # dict of (parameter, value) pairs
		self.FCompetence = FCompetence  # Competence function that computes the competence of individuals
		self.RankEffects = []   # table of decreasing investments in friendship
		self.RankEffect(0)
	
	def RankEffect(self, Rank):
		""" computes a decreasing coefficient depending on one's rank
			in another agent's address book.
		"""
		if self.RankEffects == []:
			# Initializing the table of social time given to friend
			# depending on friend's rank

			#   T: total amount of available time
			#   tn: social time devoted to nth friend
			#   Tn: occupied social time with n friends
			#   T1 = t1
			#   Tn = Tn-1 + tn * (1 - Tn-1 / T)
			#   Tn = Tn-1 (1 - tn / T) + tn
			# T controls overlap:
			# T= 1 ==> all social time is crowded within constant time
			#	   much overlap, more friends does not decrease
			#	   each friend's share significantly
			# T= 100  ==> no overlap, social times add to each other,
			#	   shares diminish as the number of friends increases
			
			RkEffect = self.Parameters('RankEffect')/100.0
			if RkEffect == 0:
				RkEffect = 0.000001
			if self.Parameters('SocialOverlap'):
				T = 100 * RkEffect / self.Parameters('SocialOverlap')
			else:
				T = 10000.0
			for n in range(self.Parameters('MaxGurus') + 2):
				tn = (RkEffect) ** (n+1)	# friend #0 gets time = RkEffect; friend #1 gets time = RkEffect**2;
				if n == 0:
					Tn = RkEffect
				else:
					Tn = self.RankEffects[n-1][0] * (1-tn/T)  + tn
				self.RankEffects.append((Tn,tn))
				
		if Rank >= 0:
			try:
				return self.RankEffects[Rank]
			except IndexError:
				error('S_Signalling: RankEffect', str('Rank == %d' % Rank))
		else:
			return (0,0)

	def NegotiateOffer(self,Agent,Partner):
		""" returns the ranks Agent and Partner are ready to assign to each other
			in their respective address book. Agent's rank recursively depends on
			Partner's attitude towards Agent.
		"""
		# non-recursive version
		MaxOffer = 100
		OldAgentOffer = OldPartnerOffer = (0,0) # (Rank, Offer)
		AgentOffer = PartnerOffer = (0, MaxOffer)	# AgentOffer = Agent's offer to Partner
		while (OldAgentOffer, OldPartnerOffer) != (AgentOffer,PartnerOffer):
			(OldAgentOffer, OldPartnerOffer) = (AgentOffer, PartnerOffer)
			PartnerOffer = self.Offer(Partner, AgentOffer, Apparent=True)
			if PartnerOffer[0] < 0:
				return (0,0)
			AgentOffer = self.Offer(Agent, PartnerOffer, Apparent=True)
			#print 'Negotiation2: %s offers %d and %s offers %d (at ranks %d, %d)' \
			#	 % (Agent.id,AgentOffer[1],Partner.id,PartnerOffer[1],AgentOffer[0], PartnerOffer[0])
			if AgentOffer[0] < 0:
				return (0,0)
		return (AgentOffer[1], PartnerOffer[1])			

	def SocialOffer(self, Competence, PartnerRank, nbFriends):	   
		""" An agent's social offer depends on its alleged or real competence,
			on the rank it offers in its address book, and on the number of friends already
			present in the address book (as it may influence available time)
		"""
		if PartnerRank < 0:
			return 0
		rankEffect = self.RankEffect(PartnerRank)[1]	# rank in address book matters
		sizeEffect = self.RankEffect(1 + nbFriends)[0] # size of address book matters
##        if abs(rankEffect - sizeEffect) > 0.0001:
##            print rankEffect, sizeEffect, Competence, PartnerRank, nbFriends
		return float(Competence * rankEffect) / sizeEffect

	def Offer(self, Agent, (PartnerRankOffer, PartnerSocialOffer), Apparent=True):
		""" Agent is going to make an offer to Partner, based on Partner's offer
		"""
		if Agent.followers.accepts(PartnerSocialOffer) < 0:
			# I don't follow you if I even don't want you to follow me
			OfferedRank = -1
		else:
			OfferedRank = Agent.gurus.accepts(PartnerSocialOffer)
		if self.Parameters('SocialSymmetry') > 0 and OfferedRank >= 0:
			# Social symmetry supposes that friends put themselves at identical levels in their address book
			OfferedRank = max(PartnerRankOffer, OfferedRank) # worst of the two ranks
		SocialOffer = self.SocialOffer(self.FCompetence(Agent, Apparent), OfferedRank, Agent.nbFriends())
		#print Agent.id, Agent.Signal, OfferedRank, SocialOffer
		return (OfferedRank, SocialOffer)

		
	def groom(self, Indiv, Partner):
		""" The two individuals negotiate partnership.
			First they signal their competence.
			Then, they make a "social offer" based on the rank
			(in their "address book") they are ready to assign to each other.
			Lastly, each one independently decides to join the other or not.
			cf. Dunbar's "grooming hypothesis"
		"""
##        #if histogram[Indiv.gurus.performance(Friend)] > 1:
##        Ia = Indiv.gurus.signature()
##        Fa = Partner.gurus.signature()

		# new interaction puts previous ones into question
		if Indiv in Partner.gurus.names():
##            print '\nBefore talking: %d quits %d' % (Partner.Phene_value('Signal'),Indiv.Phene_value('Signal'))
			Partner.quit_(Indiv)
		if Partner in Indiv.gurus.names():
##            print 'Before talking: %d quits %d' % (Indiv.Phene_value('Signal'),Partner.Phene_value('Signal'))
			Indiv.quit_(Partner)

##        if Indiv.nbFriends() > 1:
##            print "%d has %d friends" % (Indiv.id, Indiv.nbFriends()), Indiv.friends()
##        if Partner.nbFriends() > 1:
##            print "%d has %d friends_" % (Partner.id, Partner.nbFriends()), Partner.friends()

		# Negotiation takes place
		(IndivOffer, PartnerOffer) =  self.NegotiateOffer(Indiv, Partner)

		# social links are established accordingly
		if IndivOffer == 0 or PartnerOffer == 0:
			# One doesn't care about the other
##            print "\nNo deal: %s(%d)->%d, %s(%d)->%d" % \
##                (Indiv.id, Indiv.Phene_value('Signal'), IndivOffer,\
##                Partner.id, Partner.Phene_value('Signal'), PartnerOffer)
			return # the deal is not made

		IndivFriends = Indiv.friends()
		if not Indiv.follows(IndivOffer, Partner, PartnerOffer):
			# this may occur if Partner has too many followers
			print ("***** Scenario Signalling:", "Negotiation not respected")
			print Indiv.id, Indiv.Phene_value('Signal'), 'was accepted by', Partner.id,
			print 'with offer-:', IndivOffer
			print Indiv.id, sorted(Indiv.gurus.performances()),
			print sorted(Indiv.followers.performances())
			print Partner.id, sorted(Partner.gurus.performances()),
			print sorted(Partner.followers.performances())
			error('S_Signalling', "Negotiation not respected")
			return # the deal is not made

		PartnerFriends = Partner.friends()
		if not Partner.follows(PartnerOffer, Indiv, IndivOffer):
			# this may occur if Indiv has too many followers
			Indiv.quit_(Partner)
			error('S_Signalling', "Negotiation not respected")
			return # the deal is not made

##        print '%d (%02.02f) is accepted by %d' % (Indiv.id, Indiv.Signal, Partner.id), '////',
##        print IndivFriends, 'becomes', Indiv.friends()
##        print ' %d (%02.02f) is accepted by %d' % (Partner.id, Partner.Signal, Indiv.id), '///',
##        print PartnerFriends, 'becomes', Partner.friends()

		# suppression of broken links
		for Friend in IndivFriends:
##            print 'launching symmetry checking for %d...' % Friend.id,
			Friend.restore_symmetry()
		for Friend in PartnerFriends:
##            print 'launching symmetry checking for %d_...' % Friend.id,
			Friend.restore_symmetry()

##        Ib = Indiv.gurus.signature()
##        Fb = Partner.gurus.signature()
##        I = zip(Ia+[('0',0)],Ib)
##        F = zip(Fa+[('0',0)],Fb)
##        print 'Indiv: ', Indiv.id, int(self.FCompetence(Indiv, Apparent=False)), int(self.FCompetence(Indiv,Apparent=True))
##        print '\n'.join([str(f[0])+'\t'+str(f[1]) for f in I])
##        print 'Friend:', Partner.id, int(self.FCompetence(Partner, Apparent=False)), int(self.FCompetence(Partner,Apparent=True))
##        print '\n'.join([str(f[0])+'\t'+str(f[1]) for f in F])
##        raw_input('________')

##        Indiv.follows(self.SocialOffer(Indiv, 0), Partner, self.SocialOffer(Partner, 0))
##        Partner.follows(self.SocialOffer(Partner, 0), Indiv, self.SocialOffer(Indiv, 0))

##        print "\nNegotiation result: %s(%d)->%d rank %d, %s(%d)->%d rank %d" % \
##                (Indiv.id, Indiv.Phene_value('Signal'), IndivOffer, Indiv.gurus.rank(Partner),\
##                Partner.id, Partner.Phene_value('Signal'), PartnerOffer, Partner.gurus.rank(Indiv))
##        raw_input('.')        

		return

######################################
# Description of the scenario        #
######################################

class Scenario(Default_Scenario):

	######################################
	# Most functions below overload some #
	# functions of Default_Scenario	  #
	######################################


	def initialization(self):
		self.CompetenceAvgDistance = 0  # average difference in competence between best friends
		self.RiskByCompetence = [[0,0] for x in range(self.Parameter('ControlGeneNumber'))]
		self.GlobalComm = 0 # Average investment in communication by actual individuals
		self.CompetenceHistogram = [[0,0] for ii in range(self.Parameter('ControlGeneNumber'))]
		# stores individual repartition by competence
		self.PopSize = 0	# number of individuals currently present
		self.Interactions = Interactions(self.Parameter, self.Competence)

	def genemap(self):
		""" Defines the name of genes and their position on the DNA.
		Accepted syntax:
		['genename1', 'genename2',...]:   lengths and coding are retrieved from configuration
		[('genename1', 8), ('genename2', 4),...]:   numbers give lengths in bits; coding is retrieved from configuration
		[('genename1', 8, 'Weighted'), ('genename2', 4, 'Unweighted'),...]:	coding can be 'Weighted', 'Unweighted', 'Gray', 'NoCoding'
		"""
		Gmap = []
		for ControlGene in range(self.Parameter('ControlGeneNumber')):
			Gmap.append('ControlGene'+str(ControlGene))
		return [(G,0) for G in Gmap]

	def phenemap(self):
		""" Defines the set of non inheritable characteristics
		"""
		return ['Competence',   # (non heritable) ability to be relevant 
				'Strength',	 # non heritable quality, used to introduce an irrelevant criterion in the construction of social networks
				'Signal',	   # stores the signal that the individual actually emits
				'SignalInvestment', # stores the individual's propensity to communicate
				'Risk']		 # stores the individual's exposure to life hazards
		
	def new_agent(self, Child, parents):
		" initializes newborns "
		# determination of the newborn's signal level
		#   Investment in communication is genetically controlled
		#	   Genetic control may vary according to competence range
		SignalInvestment = Child.gene_relative_value('ControlGene'
														 +str(self.CompetenceRange(Child)))
		Child.Phene_value('SignalInvestment', int(SignalInvestment), Levelling=True)
		
		#   The signal is based on the signaller's competence
		Signal = self.Competence(Child, Apparent=True)
		Signal = noise_add(Signal,self.Parameter('Noise'))
		Child.Phene_value('Signal', int(Signal), Levelling=True)

	def CompetenceRange(self, Indiv):
		" assigns an individual to a category depending on its competence "
		return int((Indiv.Phene_relative_value('Competence') *
							   self.Parameter('ControlGeneNumber')) / 100.01)
	
	def Competence(self, Indiv, Apparent=False):
		" Adds a bottom value to competence "
		BC = self.Parameter('BottomCompetence')
		Comp = percent(100-BC) * Indiv.Phene_relative_value('Competence') + BC
		VisibleCompetence = percent(Comp * Indiv.Phene_relative_value('SignalInvestment'))
		CompSign = self.Parameter('CompetenceSignificance')
		Attractiveness = percent(100-CompSign) * Indiv.Phene_relative_value('Strength') \
						 + percent(CompSign) * VisibleCompetence
		if Apparent:
			return Attractiveness
##            return VisibleCompetence
		else:
			return Comp
	
	def season(self, year, members):
		""" This function is called at the beginning of each year
		"""
		self.GlobalComm = 0
		self.CompetenceHistogram = [[0,0] for ii in range(self.Parameter('ControlGeneNumber'))]
		self.RiskByCompetence = [[0,0] for x in range(self.Parameter('ControlGeneNumber'))]
		self.PopSize = 0	# number of individuals currently present
		self.CompetenceAvgDistance = 0

	def start_game(self,members):
		""" defines what is to be done at the group level before interactions
			occur
		"""
 
		for Indiv in members:
			Indiv.score(self.Parameter('SignallingCost'), FlagSet=True)	# resetting scores
			SigInv = Indiv.Phene_value('SignalInvestment')
			self.GlobalComm += SigInv
			SignalCost = percent(SigInv * self.Parameter('SignallingCost'))
			Indiv.score(-SignalCost)
			# friendship links (lessening with time) are updated 
			#Indiv.lessening_friendship()
			# links are reset
			#Indiv.detach()

			# Monitoring competence distribution
			self.CompetenceHistogram[self.CompetenceRange(Indiv)][0] += SigInv
			self.CompetenceHistogram[self.CompetenceRange(Indiv)][1] += 1
				
		self.PopSize += len(members)	# number of individuals currently present
			
		# Individuals first interact one more time with their current friends
		for Indiv in members:
##            Offers = Indiv.gurus.performances()
##            histogram = [(O,Offers.count(O)) for O in list(set(Offers))]
##            histogram.sort(key=lambda x: x[1], reverse=True)
##            histogram = dict(histogram)
			for Friend in Indiv.friends():
				self.Interactions.groom(Indiv, Friend)

	
			
	def interaction(self, Indiv, Partner):
		""" Individuals talk to each other and make the decision
			to become friends to a certain extent
		"""

		# Indiv and Partner attempt to become friends by talking to each other
		self.Interactions.groom(Indiv, Partner)
##        else:
##            # This implements standard costly signalling theory:
##            # Indiv  'sings' and Partner decides whether to join
##            if Indiv in Partner.gurus.names():
##                Partner.quit_(Indiv)
##            IndivOffer = self.SocialOffer(self.Competence(Indiv,Apparent=True), 0, Indiv.followers.size())
##            Partner.follows(0, Indiv, IndivOffer)
			
		
		# Since the new friend may take another friend's place in
		# Indiv's heart, Individuals interact then with their former partners 
##        for Friend in Indiv.friends():
##            if Indiv.gurus.rank(Friend) > Indiv.gurus.rank(Partner):
##                self.Interactions.groom(Indiv, Friend)
##
##        for Friend in Partner.friends():
##            if Partner.gurus.rank(Friend) > Partner.gurus.rank(Indiv):
##                self.Interactions.groom(Partner, Friend)
			

	

	def end_game(self, members):
		""" Individuals get benefit from their alliances
		"""
		# computing inclusive strength
		# Followers get benefit from following; that benefit is
		# correlated with the competence of the signaller. 

		for Agent in members:
			# self-service
			#Agent.Phene_value('Risk',100-self.SocialOffer(Agent, 0, Apparent=False))
			Agent.Phene_value('Risk',100)
		for Agent in members:
##            print 'end game', '%s(%d)' % (Agent.id, self.Competence(Agent,Apparent=False)),
##            print Agent.gurus
			for (Rank,Friend) in enumerate(Agent.friends()):
##                Friend.score(self.SocialOffer(Agent, Rank, Apparent=False))
				AgentSocialOffer = self.Interactions.SocialOffer(self.Competence(Agent, Apparent=False), Rank, Agent.nbFriends())
				Risk = percent(Friend.Phene_value('Risk') * (100 - percent(self.Parameter('CompetenceImpact')
																		   * AgentSocialOffer)))
				Friend.Phene_value('Risk',Risk)
##                print 'Friend', Friend.id, 'gets protection', self.SocialOffer(Agent, Rank, Apparent=False)
##                raw_input('.')
		for Agent in members:
			# agent get scores depending on their risk,
			# i.e. that grow with their accumulated protection
			Agent.score((100 - Agent.Phene_value('Risk')))
			# Monitoring average distance between best friends
			Friend = Agent.best_friend()
			if Friend is not None:
				self.CompetenceAvgDistance += abs(Friend.Phene_value('Competence')-Agent.Phene_value('Competence'))

			
		# monitoring scores depending on competence
		for Agent in members:
			CR = self.CompetenceRange(Agent)
			self.RiskByCompetence[CR][0] += 1
			self.RiskByCompetence[CR][1] += Agent.Phene_value('Risk')

##    def lives(self, members):
##        " converts scores into life points "
##        # Scores are modified to reflect the particulars of hominin politics
##        # Weakest individuals are exploited, strongest ones are favoured
##        # and medium ones are protected
##
##        if len(members) == 0:
##            return
####        from Evolife.Tools.Tools import ChildrenSlide
####        # ranking individuals
####        ranking = members[:]      # duplicates the list, not the elements
####        ranking.sort(key=lambda x: x.score(),reverse=False)
####        for RankedIndiv in enumerate(ranking):
####            RankedIndiv[1].LifePoints = self.Parameter('SelectionPressure') * \
####                                        ChildrenSlide((RankedIndiv[0] * 1.0)/len(members),
####                                                      0.1, 0.25, 0.999, Slope=0.2)
##    
####        BestScore = max([i.score() for i in members])
####        if BestScore == 0:
####            return
####        for Indiv in members:
####            merit = (Indiv.score() * 1.0) / BestScore
####            Indiv.LifePoints = ChildrenSlide(merit,0.1, 0.3, 0.999, Slope=0.2)
####            Indiv.LifePoints *= self.Parameter('SelectionPressure')
####
######        Default_Scenario.lives(self, members)
######        for Indiv in members:
######            Indiv.LifePoints = ChildrenSlide(Indiv.LifePoints,0.1, 0.25, 0.999, Slope=0.2)
####        return
##
####        Default_Scenario.lives(self, members)
##        for Indiv in members:
##            CompRange = self.CompetenceRange(Indiv) 
##            Indiv.LifePoints = percent(self.Parameter('SelectionPressure') * (100-Indiv.Phene_value('Risk')))
####        for Indiv in members:
####            print 'Indiv:',Indiv, 'Indiv.LivePoints:',Indiv.LifePoints
####            for F in Indiv.friends():
####                print F.id, 
####                print "Friend's competence:", self.Competence(F,Apparent=False)
####            raw_input('-')

	def update_positions(self, members, start_location):
		""" locates individuals on an horizontal line
		"""
		best_score = max(max([m.score() for m in members]),1)
		# sorting individuals by gene value (provisory)
		duplicate = members[:]
		duplicate.sort(key=lambda x: x.Phene_value('Competence'))
		for m in enumerate(duplicate):
##            m[1].location = (1+start_location + m[0], m[1].Phene_value('SignalInvestment'))
##            m[1].location = (1+start_location + m[0], m[1].score(), min(1+m[1].Phene_value('Sociability'),20))            
			F = m[1].best_friend()
			if F:
				# computing distance to best friend
##                m[1].location = (1+start_location + m[0], distance,
##                                 9+int((11*m[1].score())//best_score))
##                m[1].location = (1+start_location + m[0], 
				m[1].location = (1+start_location + m[1].Phene_value('Competence'), # PROVISOIRE
								 m[1].Phene_value('Signal'),
								 self.CompetenceRange(m[1])+1)
##                                 10 + min(m[1].Phene_value('SignalInvestment')//9,10)) # PROVISOIRE                  
##                                 10 + F.gurus.rank(m[1]))
##                m[1].location = (1+start_location + m[1].Phene_value('Competence'), # PROVISOIRE              
##                                 m[1].Phene_value('SignalInvestment'), # PROVISOIRE                  
##                                 10 + int(min(m[1].Phene_value('Risk')//7,10))) # PROVISOIRE                  
			else:
##                m[1].location = (1+start_location + m[0], 0, 20)
				m[1].location = (1+start_location + m[0], 
								 m[1].Phene_value('Signal'),
								 self.CompetenceRange(m[1])+1)
##                                 10 + min(m[1].Phene_value('SignalInvestment')//9,10)) # PROVISOIRE                  

	def local_display(self,VariableID):
		" allows to display locally defined values "
		if VariableID == 'Assortativeness':
			if self.PopSize:
				self.CompetenceAvgDistance /= float(self.PopSize)
				return int(100*(self.CompetenceAvgDistance/33.333))
			else:
				return -1
		elif VariableID == 'RiskByCompetence':
			for CR in range(self.Parameter('ControlGeneNumber')):
				if self.RiskByCompetence[CR][0]:
					self.RiskByCompetence[CR][1] /= float(self.RiskByCompetence[CR][0])
			return int(self.RiskByCompetence[3][1])
		elif VariableID == 'AvgCommunicationInvestment':
			if self.PopSize:
				self.GlobalComm /= float(self.PopSize)
				return int(self.GlobalComm)
			else:
				return -1
		elif VariableID.startswith('TrueControlGene'):
			if self.CompetenceHistogram[int(VariableID.split('TrueControlGene')[1])][1] < 7:
				return -1   # not enough representants
			else:
				return int(self.CompetenceHistogram[int(VariableID.split('TrueControlGene')[1])][0] / \
					   float(self.CompetenceHistogram[int(VariableID.split('TrueControlGene')[1])][1]))
			
 
	def display_(self):
		# Merely display all genes of GeneMap
		disp = [(2,'Assortativeness'),(1,'AvgCommunicationInvestment'),
				(4,'Risk')]
		disp += [(2*i+10,'TrueControlGene'+str(i)) for i in range(self.Parameter('ControlGeneNumber'))]
##        disp += [(2*i+10,G.name) for (i,G) in enumerate(self.GeneMap)]
##        disp.append((len(self.GeneMap)+1,'SignalInvestment'))
		return disp


###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print __doc__ + '\n'
	raw_input('[Return]')
	
