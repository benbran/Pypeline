#!/usr/bin/env python

import nipype.interfaces.fsl as fsl
import os
from nibabel import load
from nibabel import nifti1 
import sys 

def fix_fake_4D(filename): # Get rid of the extra 1 as a fourth dimension if just 3d file
	if os.path.isfile(filename)==True:
		try:
			img = load(filename)
			data = img.get_data()
			if img.shape[3]<2:
				data = data.squeeze()
			nifti1.Nifti1Image(data, img.get_affine()).to_filename(filename)
		except IndexError: # actually a 3D file 
			print "Fix not needed, {0} is already a 3D file".format(filename)


# test it
#fix_fake_4D(sys.argv[1])