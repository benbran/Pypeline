#!/usr/bin/env python
from __future__ import division
from nibabel import load
from numpy import floor


def highest_pixel_idx(img): # highest pixel index, dunno you might want to know lol 
	try:
		im = load(img) 
		dat = im.get_data()
		max_idx = np.unravel_index(dat.argmax(), dat.shape)
	except ValueError, IOError:
		print "Error: Could not read the image {0}, exiting".format(img)
		raise SystemExit
	return max_idx