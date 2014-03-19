#!/usr/bin/env python
from __future__ import division # just like gangstas do 


from enthought.traits.api import *
import enthought.traits.ui.api import *
import wx 
import numpy as np 
import sys
from nibabel import load  
import nipype.pipeline.engine as pe
import nipype.interfaces.fsl as fsl
fsl.FSLCommand.set_default_output_type('NIFTI')
import nipype.interfaces.matlab as matlab
import os 





class IOFiles(HasTraits):
	"""
	GUI for IO. Do try/excepts n shit here. Basically the first step into the full GUI
	"""
	struct = Str
	funct = Str 

	try:
		print ""
	except IOError:
		print "No dice"


ourfiles = IOFiles()
ourfiles.configure_traits()