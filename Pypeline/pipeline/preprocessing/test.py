#!/usr/bin/env python



from __future__ import division
import nipype.interfaces.fsl as fsl         # the spm interfaces
import nipype.pipeline.engine as pe         # the workflow and node wrappers
from enthought.traits.api import *

class SomeClass(HasTraits):
	realigner = pe.Node(interface=fsl.FLIRT(), name='realign')
	realigner.inputs.in_file = 'empty.nii'
	
