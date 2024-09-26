import PyTEMDiags
import xarray as xr
import pdb
import numpy as np
import os
from pathlib import Path
import matplotlib.pyplot as plt

# conda activate /nscratch/bmwagma/shared_conda_envs/pytem
input_root = '/pscratch/bmwagma/p1_prog_v_presc_2024/full_fv_daily'

def fill_fast(data):
    if data['plev'][0] > data['plev'][-1]:
        data  = data.reindex({'plev': data['plev'][::-1]}) # dim must be monotonic inc for interp. tem code will flip it back if needed. 
    print('starting relatively fast interpolation')
    data = data.interpolate_na( dim='plev', method='nearest',fill_value="extrapolate")
    print('finished relatively fast interpolation')
    return data
    
#for case in ['v2.LR.WCYCL20TR.0211.trc.ctools.boca.ens13.nc']:
for case in os.listdir(input_root):
    case_path = os.path.join( input_root, case )
    data = xr.open_dataset(case_path)
    data = data.drop_vars('cases')

    data = data.isel(time=(data.time.dt.year.isin([1990,1991,1992]))) # production
    #data = data.isel(time=(data.time.dt.year.isin([1990]))).isel(time=slice(0,3))  # testing. 

    data['plev'] =  data['plev'] / 100.0

    if np.sum(np.isnan( data['T'])) > 0:
        print('nans detected. will fill with interpolation')
        data = fill_fast(data)
        #data = fill_slow(data)
    ua, va, ta, wap, lat = data['U'], data['V'], data['T'], data['OMEGA'], data['lat']

    # --- construct a diagnostics object
    tem = PyTEMDiags.TEMDiagnostics(ua, va, ta, wap, lat)

    # ---- compute various TEM diagnostics
    vtem = tem.vtem()           # the TEM northward residual velocity
    wtem = tem.wtem()           # the TEM vertical residual velocity
    psitem = tem.psitem()       # the TEM mass stream function
    utendwtem = tem.utendwtem() # the tendency of eastward wind due to TEM upward wind advection

    savecase = case.removesuffix('.nc')
    Path(f'prog_ens_output/{savecase}').mkdir(parents=True, exist_ok=True)
    tem.to_netcdf(loc=f'prog_ens_output/{savecase}')
