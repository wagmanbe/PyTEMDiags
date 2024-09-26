import PyTEMDiags
import xarray as xr
import pdb
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt
import glob

# conda activate /nscratch/bmwagma/shared_conda_envs/pytem
case = 'v2.LR.WCYCL20TR.0211.trc.pmcpu.ens5'
input_root = f'/pscratch/bmwagma/p1_prog_v_presc_2024/long_historical_only/vrt_remap/fv/{case}'

def fill_fast(data):
    if data['plev'][0] > data['plev'][-1]:
        data  = data.reindex({'plev': data['plev'][::-1]}) # dim must be monotonic inc for interp. tem code will flip it back if needed. 
    print('starting relatively fast interpolation')
    data = data.interpolate_na( dim='plev', method='nearest',fill_value="extrapolate")
    print('finished relatively fast interpolation')
    return data


files  = sorted( glob.glob( os.path.join( input_root,'*h1*nc' )))
for yr in range(1980,2015):
    print(yr)
    yrfiles = [f for f in files if f'h1.{yr}' in f]
    data = xr.open_mfdataset(yrfiles)
    
    data['plev'] =  data['plev'] / 100.0

    if np.sum(np.isnan( data['T'])) > 0:
        print('nans detected. will fill with interpolation')
        data = fill_fast(data)
        #data = fill_slow(data)

    # 'lat variable and lon variable may be corrupted for some reason'
    data = data.drop_vars('lat')
    data = data.drop_vars('lon')
    cleanlat = xr.open_dataset( yrfiles[0])
    data['lat']=cleanlat['lat']
    data['lon']=cleanlat['lon']
    
    ua, va, ta, wap, lat = data['U'], data['V'], data['T'], data['OMEGA'], data['lat']

    # --- construct a diagnostics object
    tem = PyTEMDiags.TEMDiagnostics(ua, va, ta, wap, lat)

    # ---- compute various TEM diagnostics
    vtem = tem.vtem()           # the TEM northward residual velocity
    wtem = tem.wtem()           # the TEM vertical residual velocity
    psitem = tem.psitem()       # the TEM mass stream function
    utendwtem = tem.utendwtem() # the tendency of eastward wind due to TEM upward wind advection

    Path(f'prog_hist_output/{case}/{str(yr)}').mkdir(parents=True, exist_ok=True)
    tem.to_netcdf(loc=f'prog_hist_output/{case}/{str(yr)}')
