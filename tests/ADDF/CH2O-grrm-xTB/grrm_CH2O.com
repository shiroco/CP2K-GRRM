%link=non-supported
# addf/xTB

0 1
 C   1.387055000000  -0.126719000000  -0.000008000000
 H   1.659071000000  -0.705631000000  -0.875048000000
 H   1.658981000000  -0.704949000000   0.875536000000
 O  -0.093518000000   0.122575000000  -0.000056000000
OPTIONS
sublink = cp2k_grrm_interface.py
nrun = 12

&cp2k_template cp2k.tmp
&cp2k_exe cp2k.popt
&cp2k_runtype mpirun
&cp2k_np 4
