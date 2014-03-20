#########################################################################
# Walks through a file system tree and execute a command on files       #
#   Jean-Louis Dessalles 2012                                           #
#########################################################################
"""
	Walks through a file system tree and execute a command on files
"""

import os
import os.path
import re
import Replace

def Filtered(Name, Filter):
	" checks whether a file Name is Filtered "
	if not isinstance(Filter, list):	
		Filter =  [Filter]
	for Pattern in Filter:
		if re.match(Pattern, Name, re.IGNORECASE) is not None:
			return True
	return False

def Browse(StartDir, Action, SelectFilter=[], AvoidFilter=[], Verbose=True, Recursive=True):
	" Walks through the tree under StartDir and performs Action on files - Filters are lists of regular expressions "
	for (R,D,F) in os.walk(StartDir):
		for Dir in D[:]:
			if Filtered(Dir, AvoidFilter):
				if Verbose:	print('\tPruning {0}'.format(os.path.join(R,Dir)))
				D.remove(Dir)	# don't dig into subtree
		for fich in F:
			if Filtered(fich, AvoidFilter): continue
			if SelectFilter and not Filtered(fich, SelectFilter): continue
			try:
				fname = os.path.abspath(os.path.join(R,fich))
				if Verbose:	print fname
				Action(fname)
			except (WindowsError, IOError):
				print("\nXXXXXXX Erreur sur {0}/{1}".format(R,fich))
		if not Recursive:
			break

def SubstituteInTree(StartDir, FilePattern, OldString, NewString, Verbose=True, CommentLineChars=''):
	"""	Replaces OldString by NewString anywhere in all file below 'StartDir' with extension 'Extension'
	"""
	Action = lambda x: Replace.SubstituteInFile(x, OldString, NewString, Verbose=1, CommentLineChars=CommentLineChars)
	Browse(StartDir, Action, FilePattern, Verbose=Verbose)


if __name__ == '__main__':
	
	print("Do you want to replace all tabs by spaces in python source files")
	if raw_input('? ').lower().startswith('y'):
		# Detabify
		# SubstituteInTree('.', '.*.py$', '\\t', ' '*4, CommentLineChars='#')
		# ReTabify
		Walk.SubstituteInTree('.', '.*.py$', ' '*4, '\\t', CommentLineChars='#')
		print('Done')
	else:
		print ('Nothing done')
		
		




__author__ = 'Dessalles'
