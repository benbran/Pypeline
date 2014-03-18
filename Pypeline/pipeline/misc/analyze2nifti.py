#!/usr/bin/env python
from __future__ import division
import nibabel as nib 
from os import getcwd 




def analyze2nifti(file_string): 
	"""
	Convert analyze to nifti, feed it fname as string 
	"""
	if ('.hdr' in file_string) or ('.img' in file_string):
		im = nib.load(file_string)
		data = im.get_data()
		affine = im.get_affine()
		nifti_name = file_string.replace('.hdr', '')
		nib.nifti1.Nifti1Image(data, affine).to_filename(nifti_name)
		print "Converted file: {0}".format((getcwd + '/nifti_name' + '.nii.gz'))
	elif ('.nii' in file_string):
		print "This file is already in nifti format"
	else:
		print "Could not convert, {0} is not an Spm2Analyze image\n".format(file_string)



