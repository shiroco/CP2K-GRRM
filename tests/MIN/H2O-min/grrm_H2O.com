%link=non-supported
# min/B3LYP/6-31G*

0 1
 O                  0.00000000    0.00000000    0.11339900
 H                  0.00000000    0.75932800   -0.45359600
 H                  0.00000000   -0.75932800   -0.45359600
OPTIONS
sublink = cp2k_grrm_interface.py

&cp2k_template cp2k.tmp
&cp2k_exe cp2k.popt
&cp2k_runtype mpirun
&cp2k_np 4
&cp2k_basis EMSL_BASIS_SETS
&cp2k_potential POTENTIAL
