#!/usr/bin/env python
from __future__ import division 
from nibabel import load 
from numpy import floor 





def center(file_string):
	"""
	This is to grab the center of a volume in order to estimate center of brain, or 
	if you simply want to KNOW where the center is without having to load it and do it 
	manually
	"""
	try:
		im = load(file_string)
		dat = im.get_data() # numpy memmap quicker then numpy array, should look into 
		shape = im.shape # tuple
		center = int(floor(shape[0]/2)), int(floor(shape[1]/2)), int(floor(shape[2]/2))
		return center
	except IOError:
		print "IOERROR: 'center()' could not locate {0}, ensure it is in your dir".format(file_string)
		raise SystemExit
	

