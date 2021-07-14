------------------------
Tools to use CP2K from GRRM.
------------------------


Contents
------------------------

	scripts   : Interface software written in Python.
	tests     : Sample run including all input and output files.


How to use
------------------------

1. Set up GRRM input file

(1) header

	%link=non-supported

(2) OPTIONS

	sublink = cp2k_grrm_interface.py

See the GRRM manual for more details to use external codes.

(2) After all the "OPTIONS" specifications, add an empty line and write the following information for CP2K run:

	&cp2k_template : template for CP2K input. e.g., cp2k.tmp
	&cp2k_exe : CP2K execution type. e.g., cp2k.popt
	&cp2k_runtype : CP2K runtype. e.g., mpirun
	&cp2k_np : number of processers. e.g., 8
	&cp2k_basis : Basis set to use. e.g., EMSL_BASIS_SETS
	&cp2k_potential Potential type: e.g., POTENTIAL


2. Prepare template for CP2K input

A template for CP2K input files is necessary. The file name (e.g., cp2k.tmp) has to be specified in the GRRM input file (see above).
Geometry data of the template is replaced with that from GRRM-output.


3. Edit interface script (cp2k_grrm_interface.py)

One may need to edit this script to adjust your environment for CP2K run.
See the comments in the script.


Notes
------------------------

The script was tested for those options with GRRM17:

	min
	addf

**********

	August 2019: First version was developed.
	July 2021: Release as free open-source.

by H.S.
