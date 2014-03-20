##############################################################################
# EVOLIFE  www.dessalles.fr/Evolife                    Jean-Louis Dessalles  #
#            Telecom ParisTech  2014                       www.dessalles.fr  #
##############################################################################


##############################################################################
#  Alliances                                                                 #
##############################################################################

""" EVOLIFE: Module Alliances:
		Individuals inherit this class
		which determines who is friend with whom
"""

import sys
if __name__ == '__main__':  sys.path.append('../..')  # for tests


from sys import maxint
from Evolife.Tools.Tools import error

class club(object):
	""" class club: list of individuals associated with their performance.
		The performance is used to decide who gets acquainted with whom.
	"""

	def __init__(self, owner, sizeMax = 0):
		self.__members = []   # list of couples (individual,performance)
		self. sizeMax = sizeMax
		if sizeMax == 0:
			self.sizeMax = maxint

	def names(self):
		return [T[0] for T in self.__members]

	def performances(self):
		return [T[1] for T in self.__members]
		
	def present(self, (Member, Perf)):
		return (Member, Perf) in self.__members
			
	def ordered(self):
		return [T[0] for T in sorted(self.__members,key = lambda x: x[1],
									 reverse=True)]
	def rank(self, Member):
		try:
			return self.ordered().index(Member)
		except ValueError:
			return -1

	def performance(self, Member):
		try:
			return self.__members[self.names().index(Member)][1]
		except ValueError:
			error('Alliances', 'Searching for non-member')
	
	def size(self):
		return len(self.__members)

	def minimal(self):
		" returns the minimal performance among members "
		if self.size():
			return min([T[1] for T in self.__members])
		return -1

	def maximal(self):
		" returns the maximal performance among members "		
		if self.size():
			return max([T[1] for T in self.__members])
		return -1

	def best(self):
		" returns the member with the best performance "
		if self.size():
			return self.ordered()[0]
		return None

	def worst(self):
		" returns the member with the worst performance "
		if self.size():
			return self.ordered()[-1]
		return None

	def accepts(self, performance):
		" signals that the new individual can be accepted into the club "
		if self.size() >= self.sizeMax and performance <= self.minimal():
			return -1   # Note: priority given to former members
		# returning the rank that the candidate would be assigned
		#  return sorted([performance] + self.performances(),reverse=True).index(performance)
		rank = self.size() - sorted([performance] + self.performances()).index(performance)
		if rank <= self.sizeMax:
			return rank
		error('Alliances', 'accept')
		
	def enters(self, newMember, performance):
		if self.accepts(performance) >= 0:
			# First, check whether newMember is not already a member
			if newMember in self.names():
				self.exits(newMember)   # to prepare the come-back
			self.__members.append((newMember, performance))
			if self.size() > self.sizeMax:
				return self.worst() # the redundant individual will be ejected
			return None
		error("Alliances: unchecked admittance")
		return None

	def exits(self, oldMember):
		" a member goes out from the club "
		for (M,Perf) in self.__members[:]:  # safe to copy the list as it is changed within the loop
			if M == oldMember:
				self.__members.remove((oldMember,Perf))
				return True
		print 'members: ', [(str(F[0]),F[1]) for F in self.__members],
		print 'exiled: ', str(oldMember)
		error('Alliances: non-member attempting to quit a club')
		return False

	def weakening(self, Factor = 0.9):  # temporary value
		" all performances are reduced (represents temporal erosion)  "
		for (M,Perf) in self.__members[:]:  # safe to copy the list as it is changed within the loop
			self.__members.remove((M, Perf))
			self.__members.append((M, Perf * Factor))

	def __repr__(self):
		# return "[" + '-'.join([T.id for T in self.ordered()]) + "]"
		return "[" + '-'.join([str(T) for T in self.names()]) + "]"
		
class Alliances(object):
	"   class Alliances: defines an individual's acqaintances "

	def __init__(self, MaxGurus, MaxFollowers):
		self.gurus = club(self, MaxGurus)
		self.followers = club(self, MaxFollowers)

	#################################
	# hierarchical links			#
	#################################
	def follows(self, perf, G, G_perf):
		""" the individual wants to be G's disciple because of some of G's performance
			G may evaluate the individual's performance too
		"""

##        print (self.id,perf), "wants to follows", (G.id, G_perf),
		if self.gurus.accepts(G_perf)>=0 and G.followers.accepts(perf)>=0:
			# the new guru is good enough and the individual is good enough for the guru
			RG = self.gurus.enters(G,G_perf)
			RF = G.followers.enters(self,perf)
			if RG is not None:
##                 print 'redundant guru: ',RG.id,
##                print 'its followers: ',[F.id for F in RG.followers.names()], ' > ',
##                print 'self: ',self.id, "self's gurus: ",Alliances.signature(self)
				self.quit_(RG)   # some redundant guru is disowned
			if RF is not None and RF in G.followers.names(): # could have quit if RG==RF
##                print 'redundant follower: ',RF.id,
##                print 'its gurus', Alliances.signature(RF), ' >> ',
##                print 'self: ',self.id, "self's gurus: ",Alliances.signature(self)
				RF.quit_(G)   # some redundant follower is dismissed
##            print "OK"
##            self.consistency()
			return True
		else:
##            print "refusal"
##            if self.gurus.accepts(G_perf)<0:
##                print 'Refusal by', self, 'to accept performance %d in gurus' % G_perf
##            elif G.followers.accepts(perf)<0:
##                print 'Refusal by', self, 'to accept performance %d in followers' % perf
			return False

	def quit_(self, Guru = None):
		""" the individual no longer follows its guru
		"""
		if Guru == None:
			Guru = self.gurus.worst()
		if Guru is not None:
##            Guru.consistency()
##            print self.id,' quits ', Guru.id
##            print 'Guru.followers1: ', [F.id for F in Guru.followers.names()]
			Guru.followers.exits(self)
##            print 'Guru.followers2: ', [F.id for F in Guru.followers.names()]
##            print 'self.gurus1: ', [F.id for F in self.gurus.names()]
			self.gurus.exits(Guru)
##            print 'self.gurus2: ', [F.id for F in self.gurus.names()]
		return Guru

	#################################
	# horizontal links			  #
	#################################
	def new_friend(self, F, Fperf):
		""" the individual considers F as a friend because of some performance of F
		"""
		return self.follows(0, F, Fperf)

	def best_friend(self):
		return self.gurus.best()
	
	def friends(self):
		return self.gurus.ordered()

	def nbFriends(self):
		return self.gurus.size()

	def lessening_friendship(self, Factor=0.9):
		self.gurus.weakening(Factor)					

	def best_friend_symmetry(self):
		" Checks whether self is its best friend's friend "
		BF = self.best_friend()
		if BF:  return self == BF.best_friend()
		return False
	
	def restore_symmetry(self):
		" Makes sure that self is its friends' friend - Useful for symmmtrical relations "
		for F in self.gurus.names()[:]:	 # need to copy the list, as it is modified within the loop
			#print 'checking symmetry for %d' % F.id, F.gurus.names()
			if self not in F.gurus.names():
				#print self.id, 'quits', F.id,
				#print '*****  because absent from ', F.gurus.names()
				self.quit_(F)   # no hard feelings 

		
	#################################
	# link processing			   #
	#################################
	def detach(self):
		""" The individual quits its guru and its followers
		"""
		for G in self.gurus.names():
			self.quit_(G)
		for F in self.followers.names():
			F.quit_(self)
		if self.gurus.names() != []:
			error("Alliances: recalcitrant guru")
		if self.followers.names() != []:
			error("Alliances: sticky followers")
		
	def consistency(self):
		if self.gurus.size() > self.gurus.sizeMax:
			error("Alliances", "too many gurus: %d" % self.gurus.size())
		if self.followers.size() > self.followers.sizeMax:
			error("Alliances", "too many followers: %d" % self.followers.size())
		for F in self.followers.names():
			if self not in F.gurus.names():
				error("Alliances: non following followers")
			if self == F:
				error("Alliances: Narcissism")
##            print self.id, ' is in ', F.id, "'s guru list: ", [G.id for G in F.gurus.names()]
		for G in self.gurus.names():
			if self not in G.followers.names():
				print 'self: ',str(self), "self's gurus: ",Alliances.signature(self)
				print 'guru: ',str(G), 'its followers: ',[str(F) for F in G.followers.names()]
				error("Alliances: unaware guru")
			if self == G:
				error("Alliances: narcissism")
##            print self.id, ' is in ', G.id, "'s follower list: ", [F.id for F in G.followers.names()]
##        print '\t', self.id, ' OK'
		if self.gurus.size() > 0:
			if not self.gurus.present((self.gurus.best(), self.gurus.maximal())):
					error("Alliances: best guru is ghost")
			
		
	def signature(self):
##        return [F.id for F in self.gurus.names()]
		return self.gurus.ordered()
			
###############################
# Local Test                  #
###############################

if __name__ == "__main__":
	print __doc__ + '\n'
	print Alliances.__doc__ + '\n\n'
	raw_input('[Return]')


__author__ = 'Dessalles'
