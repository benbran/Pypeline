#!/usr/bin/env python
from __future__ import division # just like gangstas do 


 
import enthought.traits.ui
import numpy as np 
import sys
from nibabel import load  
import nipype.pipeline.engine as pe
from nipype.interfaces.base import traits, TraitedSpec, CommandLineInputSpec, CommandLine
# traits is the module containing the traits, TraitedSpec is the class you can inherit from
import nipype.interfaces.fsl as fsl
fsl.FSLCommand.set_default_output_type('NIFTI')
import os 



########
## Make it so that you input just the string filenames from the terminal or whatever
## Keep it as generalizable as possible
## Here it goes
# We have 5 nodes to worry about, all in fsl. Can extend to afni n shit later
####### 




############################### Helper/grabber functions and variables#######################

tolist = lambda x: [x] # quick int/string/float to list
cwd = os.getcwd() # for joining paths and shit
search = {0: [0,0], 1: [-90,90], 2: [-180,180]} # search function type; 1=none, 2=half, 3=full
cost_func = {0:'corratio', 1:'mutualinfo', 2:'normmi', 3:'normcorr', 4:'leastsq'}



def itrpfnirt(interp):
	interp = interp.lower() # remove upper case problem
	interp = interp.strip() # remove trailing whitespace
	if interp == "l":
    	interp = "trilinear"
	return interp

def itrpflirt(interp):
	interp = interp.lower() 
	interp = interp.strip() 
	if interp == "s":
		interp = "sinc"
	elif interp == "l":
		interp = "trilinear"
	elif interp == "nn":
	   	interp = "nearestneighbour"
	else:
		interp = "sinc" # default to sinc
	return interp

def sincwindow(window):
	if window =='h':
		window = 'hanning'
	elif window =='b':
		window = 'blackman'
	elif window =='r':
		window = 'rectangular'
	else:
		window = 'hanning'
	return window 


#############################################################################################


def bet_img(fname, frac=0.5, m=False, center=False, out_file=False, remove_eyes=False): 
	"""
	Extract brain using fsl's BET

	Emulate the following command for standard BET:
	$bet in_file out_file  -f 0.5 
	"""
	bet = fsl.BET()
	if remove_eyes==True or bool(remove_eyes)==True: # so input True or 1 or whatever
		bet.inputs.remove_eyes = True
	if m!=False:
		bet.inputs.mask= True	
	bet.inputs.in_file = fname
	if out_file!=False and type(out_file)==str:
		bet.inputs.out_file = out_file 
	bet.inputs.frac = frac
	if center!=False and type(center)==list and len(center)<=3: # eg [120,120,10]
		bet.inputs.center = center
	else: 
		print "InputError: {0} is an invalid center for {1}, resorted to BET's default\n".format(center,fname)
	return bet.run()




def flirt_imgs(templ_img, ref_img, interp='s', sinc_width=5, sinc_window='h', cost=0,
 dof=6, mat_name=0, search_type=1):
	"""
	Linearly register images using fsl's FLIRT

	Emulate the following command:
	$flirt -in in_file -ref ref_file -out out_name -omat mat_name -bins 256 -cost mutualinfo
	 -searchrx -90 90 -searchry -90 90 -searchrz -90 90 -dof 6  -interp sinc -sincwidth 5
	 -sincwindow hanning

	Yup thats a long command
	"""

	intrp = itrpflirt(interp)
	if intrp=='sinc':
		flirt.inputs.sinc_width = sinc_width
		flirt.inputs.sinc_window = sincwindow(sinc_window)	

	flirt=fsl.FLIRT()
	flirt.inputs.in_file = templ_img
	flirt.inputs.reference = ref_img
	flirt.inputs.interp = intrp

	if dof in range(3,13):
		flirt.inputs.dof = dof 
	else: 
		print "InputError: {0} is an invalid model, defaulting to rigid 6 parameter\n".format(dof)
		flirt.inputs.dof = 6

	if cost in range(5):
		flirt.inputs.cost_func = cost_func[cost]
	else:
		print "InputError: {0} is an invalid cost function, resorting to default {1}\n".format(cost, cost_func[0])
		flirt.inputs.cost_func = cost_func[0]

	if mat_name!=0 and type(mat_name)==str:
		flirt.inputs.out_matrix_file = mat_name
	else:
		print "InputError: {0} is and invalid mat name, resorting to FSL's default naming convention\n".format(mat_name)

	if search_type in range(2): # default is 1 which is [-90,90] (half)
	 
		flirt.inputs.searchr_x = search[search_type]
		flirt.inputs.searchr_y = search[search_type]
		flirt.inputs.searchr_z = search[search_type]
	else:
		print "InputError: {0} is an invalid search type, valid types are 0, 1 and 2. Resorting to default half search\n".format(search_type)
		flirt.inputs.searchr_x = search[1]
		flirt.inputs.searchr_y = search[1]
		flirt.inputs.searchr_z = search[1]

	return flirt.run()




def spatial_smooth(brain, fwhm):
	gauss = fsl.Smooth()
	if os.path.isfile(brain)==True:
		continue
	else:
		print "IOError: {0} is an invalid file".format(brain)
	gauss.inputs.in_file = brain 
	try:
		gauss.inputs.fwhm = fwhm 
	except TraitError:
		try: 
			fwhm = float(fwhm)
			gauss.inputs.fwhm = fwhm
		except ValueError:
			print "ValueError: {0} is not a valid FWHM for Gaussian Smoothing".format(fwhm)
			raise SystemExit



def temporal_smooth(in_file, sigma_low, sigma_high):
	"""
	Bandpass filter-maker... kinda. For RS data you want to low pass so create a 
	low pass bandpass filter, if that makes sense 

	essentially you want  2>sigma>4 seconds
	"""
	in_time = fsl.TemporalFilter()
	in_time.inputs.in_file = in_file
	in_time.inputs.lowpass_sigma = sigma_low
	in_time.inputs.highpass_sigma = sigma_high






def preprocess_RS(fmr_file, anat_file, monkey=True, human=False):
	"""
	------------------------------------------------------------------------------------------
	Preprocessing resting state data. These steps are best suited to monkey EPI data.

	Major steps are as follows:
	1) Motion correct (6 param affine rigid register fmr_file to anat_file)
	
	2) Brain extract

	3) Spatial smooth (Gaussian FWHM=3-6 mm, usually 3 is good)

	3) Low pass temp filter (Gaussian HWHM=2-4 s, usually 2.8 is good) 

	4) Spatial normalization (12 param linear affine with appropriate template, for macaque 
	monkeys F99	is good)

	------------------------------------------------------------------------------------------
	"""
	if os.path.isfile(fmr_file)==True and os.path.isfile(anat_file)==True:
		continue
	else:
		print "IOError: {0} and/or {1} are invalid files\n".format(fmr_file, anat_file)
		raise SystemExit


	# Step 1, I think it's best to register the anat to itself to fix further motion hence reducing artifacts in func
	flirt_imgs(anat_file, anat_file, cost=1, mat_name=anat_file.replace('.nii', '_mat'), search_type=2) #full search
	flirt_imgs(fmr_file, anat_file, cost=1, mat_name=fmr_file.replace('.nii', '_mat'), search_type=2) #full search

	# Step 2, extract both anatomical and functional at this point 
	bet_img(fmr_file)
	bet_img(anat_file)

	# Step 3, smooth in xyz
	





# Test the function 
#preprocess_RS(sys.argv[1], sys.argv[2])












