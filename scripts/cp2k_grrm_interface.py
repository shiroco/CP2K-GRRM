#! /usr/bin/env python

#
# This is a Python script to use CP2K instead of Gaussian (default) from GRRM. 
# It is free and open-source software licensed under the MIT-lisence. 
# We assume no responsibility or liability whatsoever arising from actual use.
#
# To use CP2K from GRRM, write in GRRM input file: 
# "%link=non-supported" at the header, and
# "sublink = cp2k_grrm_interface.py" after "OPTIONS".
# See the GRRM manual for more details to use external codes.
#
# After all the "OPTIONS" specifications, add an empty line 
# and write the following information for CP2K run: 
#
# &cp2k_template : template for CP2K input. e.g., cp2k.tmp
# &cp2k_exe : CP2K execution type. e.g., cp2k.popt
# &cp2k_runtype : CP2K runtype. e.g., mpirun
# &cp2k_np : number of processers. e.g., 8
# &cp2k_basis : Basis set to use. e.g., EMSL_BASIS_SETS
# &cp2k_potential Potential type: e.g., POTENTIAL 
#
# A template for CP2K input files is necessary.
# The file name (e.g., cp2k.tmp) has to be specified in the GRRM input file.
# Geometry data of the template is replaced with that from GRRM-output.
# One may need to edit this script to adjust your environment for CP2K run.
#
# The script was tested for those options with GRRM17:
#  min
#  addf
#
# --------------------------------------------
# August 2019: First version was developed.
# July 2021: Release as free open-source.
#
# Hiroko Satoh @ Zurich, CH
# -------------------------------------------- 

import sys
import math
import copy
import string
import os.path
import shlex, subprocess
import shutil
import glob

f = sys.argv[1]
#if os.path.isfile(f) == False:
#	print (f, "does not exist.")
#	sys.exit()

fin= f + "_INP4GEN.rrm"
fin_out="INP4GEN.out"

fout = f + "_OUT4GEN.rrm"
fout_final="OUT4GEN.out"

firc= f + "_IRCInfo.rrm"
firc_out="IRCInfo.out"

flink= f + "_LinkJOB.rrm"
flink_out="LinkJOB.out"

fopt= f + "_OPTInfo.rrm"
fopt_out="OPTInfo.out"

fshs= f + "_SHSInfo.rrm"
fshs_out="SHSInfo.out"

fcp2k_in = f + "_cp2k.inp"
fcp2k_out = f + "_cp2k.out"

#print (fin, fin_out, fout, fcp2k_in, fcp2k_out)

if os.path.isfile(fin) == False:
	print ("%s does not exist." % fin)
	sys.exit()
else:
	f1 = open(fin, 'r')
	g1 = open(fin_out, 'a')
	contents = f1.read()
	g1.write(contents)
	f1.close()
	g1.close()

if os.path.isfile(firc) == True:
	f1 = open(firc, 'r')
	g1 = open(firc_out, 'a')
	contents = f1.read()
	g1.write(contents)
	f1.close()
	g1.close()

if os.path.isfile(flink) == True:
	f1 = open(flink, 'r')
	g1 = open(flink_out, 'a')
	contents = f1.read()
	g1.write(contents)
	f1.close()
	g1.close()

if os.path.isfile(fopt) == True:
	f1 = open(fopt, 'r')
	g1 = open(fopt_out, 'a')
	contents = f1.read()
	g1.write(contents)
	f1.close()
	g1.close()

if os.path.isfile(fshs) == True:
	f1 = open(fshs, 'r')
	g1 = open(fshs_out, 'a')
	g1.write(contents)
	g1.write(contents)
	f1.close()
	g1.close()

file_com = glob.glob("*.com")
input_com = file_com[0]
if os.path.isfile(input_com) == False:
	print ("grrm input file %s does not exist." % input_com)
	sys.exit()	

# read method, basis set, charge, and spin from input_com

fcp2k_tmp="cp2k_inp.tmp"
cp2k_exe="cp2k.popt"
cp2k_run="mpirun"
cp2k_basis="EMSL_BASIS_SETS"
cp2k_potential="POTENTIAL"
cp2k_np=1
f1 = open(input_com, 'r')
for line in f1:
	if line[0:1] == '#':
		line=line.rstrip('\n')
		parts=line.split('/')	
		method=parts[1]
		if len(parts) == 3:
			basisset=parts[2]
		line=f1.readline()
		line=f1.readline()
		parts=line.split()
		charge=parts[0]
		spin=parts[1]
	if line[0:1] == '&':
		line=line.rstrip('\n')
		parts=line.split()
		if parts[0].casefold() == '&cp2k_template':
			fcp2k_tmp=parts[1]
		elif parts[0].casefold() == '&cp2k_exe':
			cp2k_exe=parts[1]
		elif parts[0].casefold() == '&cp2k_runtype':
			cp2k_run=parts[1]
		elif parts[0].casefold() == '&cp2k_np':
			cp2k_np=parts[1]
		elif parts[0].casefold() == '&cp2k_basis':
			cp2k_basis=parts[1]
		elif parts[0].casefold() == '&cp2k_potential':
			cp2k_potential=parts[1]
f1.close()
#print (fcp2k_tmp, cp2k_exe, cp2k_run, cp2k_np)

# read task and xyz geometry from xxx_INP4GEN.rrm
flag_energy=0
flag_gradient=0
flag_hessian=0
flag_guess=0
nstate=0
natom_active=0
natom_move=0
asym = []
ax = []
ay = []
az = []
natom_frozen=0
asym_frozen = []
ax_frozen = []
ay_frozen = []
az_frozen = []

f1 = open(fin, 'r')
for line in f1:
	line=line.rstrip('\n')
	line=line.replace(",", "")
#	print(line)
	parts=line.split()
#	print(parts)

	if parts[0] == 'TASK:':
		for i in range(len(parts)):
			if parts[i] == 'ENERGY':
				flag_energy=1
			elif parts[i] == 'GRADIENT':
				flag_gradient=1
			elif parts[i] == 'HESSIAN':
				flag_hessian=1
	if parts[0] == 'GUESS:':
		if parts[1] == 'READ':
			flag_guess=1
	if parts[0] == 'STATE:':
		nstate=int(parts[1])
	if parts[0] == 'NACTIVEATOM':
		natom_active= int(parts[3])
		natom_move= int(parts[5])
		for k in range(natom_move):
			line=f1.readline()
			line=line.rstrip('\n')
			parts=line.split()
			asym.append(parts[0])
			ax.append(float(parts[1]))
			ay.append(float(parts[2]))
			az.append(float(parts[3]))
	if parts[0] == 'NFROZENATOM:':
		natom_frozen=int(parts[1])
		if natom_frozen > 0:
			for k in range(natom_frozen):
				line=f1.readline()
				line=line.rstrip('\n')
				parts=line.split()
				asym_frozen.append(parts[0])
				ax_frozen.append(float(parts[1]))
				ay_frozen.append(float(parts[2]))
				az_frozen.append(float(parts[3]))
		break
f1.close()
#print (flag_energy, flag_gradient, flag_hessian)
#print (flag_guess)
#print (nstate)
#print (natom_active, natom_move)
#print (asym, ax, ay, az)
#print (natom_frozen)
#print (asym_frozen, ax_frozen, ay_frozen, az_frozen)
				

# make cp2k input file

space6 = '      '
space1 = ' '

if os.path.isfile(fcp2k_tmp) == False:
	print ("cp2k template file %s does not exist." % fcp2k_tmp)
	sys.exit()
f1 = open(fcp2k_tmp, 'r')
g1 = open(fcp2k_in, 'w')

iflag_force_eval=0
iflag_print=0
iflag_dft=0
iflag_subsys=0
iflag_coord=0
iflag_global=0
iflag_motion=0
iflag_constraint=0
for line in f1:
	parts=line.split()	
	if parts[0].casefold() == '&force_eval':
		iflag_force_eval=1
		g1.write(line)
		while iflag_force_eval == 1:
			line=f1.readline()
			parts=line.split()
			if len(parts) > 0 and parts[0].casefold() == '&print':
				iflag_print=1
				g1.write(line)
				while iflag_print == 1:
					line=f1.readline()
					parts=line.split()
					if len(parts) > 0 and parts[0].casefold() == '&grrm':
						g1.write(line)
						line=f1.readline()
						new_line="     filename =" + fout +"\n"
						g1.write(new_line)
						line=f1.readline()
						new_line="    &END GRRM\n"
						g1.write(new_line)
					elif len(parts) == 2 and parts[0].casefold() == '&end' and parts[1].casefold() == 'print':
						iflag_print=2
						g1.write(line)
					else:
						g1.write(line)
			elif len(parts) > 0 and parts[0].casefold() == '&dft':
				iflag_dft=1
				g1.write(line)
				while iflag_dft == 1:
					line=f1.readline()
					parts=line.split()
					if len(parts) > 0 and parts[0].casefold() == 'basis_set_file_name' and cp2k_basis != []:
						new_line="    BASIS_SET_FILE_NAME " + cp2k_basis + "\n"
						g1.write(new_line)
					elif len(parts) > 0 and parts[0].casefold() == 'potential_file_name' and cp2k_potential != []:
						new_line="    POTENTIAL_FILE_NAME " + cp2k_potential + "\n"
						g1.write(new_line)
					elif len(parts) > 0 and parts[0].casefold() == 'charge':
						new_line="    CHARGE " + str(charge) + "\n"
						g1.write(new_line)
					elif len(parts) > 0 and parts[0].casefold() == 'multiplicity':
						new_line="    MULTIPLICITY " + str(spin) + "\n"
						g1.write(new_line)
					elif len(parts) == 2 and parts[0].casefold() == '&end' and parts[1].casefold() == 'dft':
						iflag_dft=2
						g1.write(line)
					else:
						g1.write(line)
			elif len(parts) > 0 and parts[0].casefold() == '&subsys':
				iflag_subsys=1
				g1.write(line)
				while (iflag_subsys == 1):
					line=f1.readline()
					parts=line.split()
					if len(parts) > 0 and parts[0].casefold() == '&coord':
						iflag_coord=1
						g1.write(line)
						for k in range(natom_move):
							xc = '%18.12f' %ax[k]
							yc = '%18.12f' %ay[k]
							zc = '%18.12f' %az[k]
							g1.write(space1 + str(asym[k]) + space6 + xc + space6 + yc + space6 + zc + "\n")
						for k in range(natom_frozen):
							xc = '%18.12f' %ax_frozen[k]
							yc = '%18.12f' %ax_frozen[k]
							zc = '%18.12f' %ax_frozen[k]
							g1.write(space1 + str(asym_frozen[k]) + space6 + xc + space6 + yc + space6 + zc + "\n")
						while iflag_coord == 1:
							line=f1.readline()
							parts=line.split()
							if len(parts) == 2 and parts[0].casefold() == "&end" and parts[1].casefold() == 'coord':
								iflag_coord=2
								g1.write(line)
					elif len(parts) == 2 and parts[0].casefold() == '&end' and parts[1].casefold() == 'subsys':
						iflag_subsys=2
						g1.write(line)
					else:
						g1.write(line) 
			elif len(parts) == 2 and parts[0].casefold() == '&end' and parts[1].casefold() == 'force_eval':
				iflag_force_eval=2
				g1.write(line)
			else:
				g1.write(line)
	elif parts[0].casefold() == '&global':
		iflag_global=1
		g1.write(line)
		while (iflag_global == 1):
			line=f1.readline()
			parts=line.split()
			if len(parts) > 0 and parts[0].casefold() == 'project':
				new_line="  PROJECT " + f + "_cp2k\n"
				g1.write(new_line)	
			elif len(parts) > 0 and parts[0].casefold() == 'run_type':
				#print (flag_energy, flag_gradient, flag_hessian)
				if flag_energy == 1 and flag_gradient == 0 and flag_hessian == 0:
					new_line="  RUN_TYPE ENERGY\n"
				elif flag_energy == 1 and flag_gradient == 1 and flag_hessian == 0:
					new_line="  RUN_TYPE ENERGY_FORCE\n"
				elif flag_energy == 1 and flag_gradient == 1 and flag_hessian == 1:
					new_line="  RUN_TYPE VIBRATIONAL_ANALYSIS\n"
				else:
					new_line="  RUN_TYPE ENERGY\n"
				#print (new_line)
				g1.write(new_line)
			elif len(parts) == 2 and parts[0].casefold() == '&end' and parts[1].casefold() == 'global':
				iflag_global=2
				g1.write(line)
			else:
				g1.write(line)
	elif parts[0].casefold() == '&motion':
		iflag_motion=1
		g1.write(line)
		if natom_frozen > 0:
			new_line = "  &CONSTRAINT\n"
			g1.write(new_line)
			new_line = "    &FIXED_ATOMS\n"
			g1.write(new_line)
			first=str(int(natom_move+1))
			last=str(int(natom_move+natom_frozen))
			new_line = "      LIST " +  first + ".." + last + "\n"
			g1.write(new_line)
			new_line = "    &END FIXED_ATOMS\n"
			g1.write(new_line)
			new_line = "  &END CONSTRAINT\n"
			g1.write(new_line)
		while iflag_motion == 1:
			line=f1.readline()
			parts=line.split()
			if len(parts) == 2 and parts[0].casefold() == '&end' and parts[1].casefold() == 'motion':
				iflag_motion = 2
				g1.write(line)
			elif len(parts) > 0 and parts[0].casefold() == '&constraint':
				iflag_constraint = 1
				while iflag_constraint == 1:
					line=f1.readline()
					parts=line.split()
					if len(parts) == 2 and parts[0].casefold() == "&end" and parts[1].casefold() == 'constraint':
						iflag_constraint = 2
			else:
				g1.write(line)
	else:
		g1.write(line)
f1.close()
g1.close()

# --start------ Setting for CP2K run --------------- 
# Edit this part adjusting your CP2K environments
#
# Reset environment variables for CP2K
# This is needed when your CP2K uses a different mpi environment from that of GRRM.

envvar_del=["I_MPI_FABRICS", "I_MPI_FALLBACK", "I_MPI_HYDRA_BOOTSTRAP", "I_MPI_ROOT"]
envvar_rev=["LD_LIBRARY_PATH","PATH","MANPATH"]

for y in envvar_del:
	del os.environ[y]
cp2k_env=dict(os.environ)
for y in envvar_rev:
	env_new=[]
	env_new=":".join([x for x in os.environ[y].split(':') if "GRRM" not in x])
	cp2k_env[y]=env_new

# print (cp2k_env)

# run cp2k
# Default command: "mpirun -np 1 cp2k.popt xxx_cp2k.inp > xxx_cp2k.out"


output = subprocess.run([cp2k_run,'-np',cp2k_np,cp2k_exe,'-i',fcp2k_in,'-o',fcp2k_out],stdout = subprocess.PIPE, stderr = subprocess.PIPE,env=cp2k_env)

# --end------ Setting for CP2K run ----------------

g1 = open('cp2k_standard_out', 'w')
g1.write(output.stdout.decode("utf8"))
g1.close()
g1 = open('cp2k_standard_err', 'w')
g1.write(output.stderr.decode("utf8"))
g1.close()

#if os.path.isfile(fout) == True:
#	f1 = open(fout, 'r')
#	g1 = open(fout_final, 'a')
#	contents = f1.read()
#	g1.write(contents)
#	f1.close()
#	g1.close()

#if os.path.isfile(fcp2k_in) == True:
#	f1 = open(fcp2k_in, 'r')
#	g1 = open("cp2k_in", 'a')
#	contents = f1.read()
#	g1.write(contents)
#	f1.close()
#	g1.close()
#if os.path.isfile(fcp2k_out) == True:
#	f1 = open(fcp2k_out, 'r')
#	g1 = open("cp2k_out", 'a')
#	contents = f1.read()
#	g1.write(contents)
#	f1.close()
#	g1.close()

# xxx_OUT4GEN.rrm file is output from cp2k
# *** example of the input file of cp2k to output xxx_OUT4GEN.rrm ***
# **********
#&FORCE_EVAL
#  METHOD Quickstep
#  &PRINT
#   &GRRM
#    filename =xxx
#   &END GRRM
#  &END PRINT
# **********
 
# copy MO file to xxx_MO2GEN.rrm
