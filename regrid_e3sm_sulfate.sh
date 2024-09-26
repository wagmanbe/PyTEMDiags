# Get monthly SO2 and sulfate vars on the 37-level pressure grid for comparison to brewer dobson circulation. 

FULLHISTDIR=/gpfs/cldera/data/e3sm/e3sm-cldera/CLDERA-historical/v2.LR.WCYCL20TR.0211.trc.pmcpu/archive/atm/hist
INDIR=/pscratch/bmwagma/p1_prog_v_presc_2024/vrt_remap_1980_1999/in
OUTDIR=/pscratch/bmwagma/p1_prog_v_presc_2024/vrt_remap_1980_1999/out

# symlink the files i want to remap to their own dir. 
ln -sf $FULLHISTDIR/*h0*19[89]* $INDIR

# remap to 37 pressure levels, stay on native lat-lon grid. 
ncremap -I $INDIR -O $OUTDIR -v Mass_so4,SO2,EXTINCT,area,lat,lon --vrt_fl=plevs/ERAI_L37.nc

