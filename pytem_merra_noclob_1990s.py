import PyTEMDiags
import xarray as xr
import pdb
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt
import glob
import shutil

# Turned off first regridding. Retaining 2nd regridding.  Can run this over and over as regridding script progresses. 

# conda activate /nscratch/bmwagma/shared_conda_envs/pytem


input_root = '/gpfs/cldera/data/MERRA-2/inst3_3d_asm_Np/'

def fill_fast(data):
    if data['plev'][0] > data['plev'][-1]:
        data  = data.reindex({'plev': data['plev'][::-1]}) # dim must be monotonic inc for interp. tem code will flip it back if needed. 
    print('starting relatively fast interpolation')
    data = data.interpolate_na( dim='plev', method='nearest',fill_value="extrapolate")
    print('finished relatively fast interpolation')
    return data


tmp_remap_dir = '/nscratch/bmwagma/remap_tmp'
native_remap_dir = '/nscratch/bmwagma/native_tmp'
for yr in range(1999,2001):
    print(yr)
    yrfiles  = glob.glob( os.path.join( input_root,str(yr),'**','*nc4' ),recursive=True)
    # Opening all of these is too slow, so we'll do a month at a time.
    for mo in ['01','02','03','04','05','06','07','08','09','10','11','12']:
        print(mo)

        # Check if pytem file exists for this year and month.
        # If it does, end.
        temfile = glob.glob( os.path.join( f'merra_output/{str(yr)}/{mo}/TEM*nc'))
        if not len(temfile)>0:

            yrmofiles = glob.glob( os.path.join( input_root,str(yr),mo,'*nc4' ),recursive=True)

            # # Disabling remap since I'm running it in a separate job. 
            for f in yrmofiles:
                filename = os.path.basename( f )
                cmd1 = f'ncremap -v T,U,V,OMEGA,PS -i {f} -m map_merra_to_180x360.nc -O {tmp_remap_dir}'
                if not os.path.isfile(os.path.join(tmp_remap_dir, filename )):
                     os.system(cmd1)
                cmd2 = f'ncremap -i {os.path.join(tmp_remap_dir, filename)} -O {native_remap_dir} -m map_180x360_to_ne30pg2.nc'
                if not os.path.isfile(os.path.join(native_remap_dir, filename )):
                     os.system(cmd2)
            
            remapped_files  = sorted( glob.glob( os.path.join( native_remap_dir,f'*{yr}{mo}*nc4' )))
            remapped_files = [i for i in remapped_files if os.path.getsize( remapped_files[4] ) > 88000000 ] # To make sure its done writing. 
            not_done_files = [i for i in remapped_files if os.path.getsize( remapped_files[4] ) < 88000000 ] # To make sure its done writing. 


            if len(remapped_files)>0:
                if len(not_done_files)==0:
                    data = xr.open_mfdataset(remapped_files)
                    data = data.resample(time="1D").mean()
                    
                    data = data.rename({'lev':'plev'})
        
                    # Merra has nans underground, so fill those. 
                    if np.sum(np.isnan( data['T'])) > 0:
                        print('nans detected. will fill with interpolation')
                        data = fill_fast(data)

                    # If it still has nans, something else is up. 
                    if np.sum(np.isnan( data['T'])) == 0:
                
                        ua, va, ta, wap, lat = data['U'], data['V'], data['T'], data['OMEGA'], data['lat']
        
                        # --- construct a diagnostics object
                        tem = PyTEMDiags.TEMDiagnostics(ua, va, ta, wap, lat)

                        # ---- compute various TEM diagnostics
                        vtem = tem.vtem()           # the TEM northward residual velocity
                        wtem = tem.wtem()           # the TEM vertical residual velocity
                        psitem = tem.psitem()       # the TEM mass stream function
                        utendwtem = tem.utendwtem() # the tendency of eastward wind due to TEM upward wind advection

                        Path(f'merra_output/{str(yr)}/{mo}').mkdir(parents=True, exist_ok=True)
                        tem.to_netcdf(loc=f'merra_output/{str(yr)}/{mo}')
                    else:
                        print('skipping TEM due to nans detected')
