#!/bin/bash
# conda activate /nscratch/bmwagma/shared_conda_envs/pytem

# MAP=map_merra_to_180x360.nc
# INROOT=/gpfs/cldera/data/MERRA-2/inst3_3d_asm_Np/1982
# OUTDIR=/nscratch/bmwagma/remap_tmp
# OUTDIR=/nscratch/bmwagma/remap_test
# for d in $INROOT/*/; do
#     echo $d
#     ncremap -m $MAP -I $d -O $OUTDIR
# done

# Do the whole 1980s without interfering with code running now in 1980-1981
MAP=map_merra_to_180x360.nc
INROOT=/gpfs/cldera/data/MERRA-2/inst3_3d_asm_Np
OUTDIR=/nscratch/bmwagma/remap_tmp
#OUTDIR=/nscratch/bmwagma/remap_test
for yr in $INROOT/198[23456789]/; do
    for mo in $yr/*; do
	echo $mo
	ncremap -v T,U,V,OMEGA,PS -m $MAP -I $mo -O $OUTDIR
    done
done
