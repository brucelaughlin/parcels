import xarray as xr
import numpy as np
import netCDF4
import argparse
import os
from pathlib import Path

#parser = argparse.ArgumentParser()
#parser.add_argument("modelfile", type=str)
#args = parser.parse_args()

#model_file = args.modelfile
#model_file = "/home/blaughli/parcels/modify_input/t_testing/z_input/wcr30_u_v_avg.nc"
model_file = "/home/blaughli/parcels/modify_input/t_testing/z_input/roms_avg_wcr30_ERA.nc"

cwd = os.getcwd()
output_dir = os.path.join(cwd, "z_output")
os.makedirs(output_dir, exist_ok = True)

grid_name = Path(model_file).stem
model_file_extension = os.path.splitext(model_file)[-1]
output_file = os.path.join(output_dir,f"{grid_name}_UVavgToRho.nc")

with netCDF4.Dataset(model_file,"a") as d:

    if "u_rho" not in d.variables:
        u_rho = d.createVariable('u_rho', 'float', ('ocean_time', 's_rho', 'eta_rho', 'xi_rho'))
        v_rho = d.createVariable('v_rho', 'float', ('ocean_time', 's_rho', 'eta_rho', 'xi_rho'))

        rho_i = d.dimensions['eta_rho'].size
        rho_j = d.dimensions['xi_rho'].size
        rho_k = d.dimensions['s_rho'].size

        u_new = np.empty((rho_k, rho_i, rho_j))
        v_new = np.empty((rho_k, rho_i, rho_j))

        for i_time in range(d.dimensions['ocean_time'].size):
            print(f"timestep {i_time}/{d.dimensions['ocean_time'].size - 1}")
            u_timestep = d["u"][i_time,:,:,:].data
            v_timestep = d["v"][i_time,:,:,:].data

            u_new[:,:,1:-1] = (u_timestep[:,:,:-1] + u_timestep[:,:,1:])/2
            u_new[:,:,0] = u_new[:,:,1]
            u_new[:,:,-1] = u_new[:,:,-1]

            v_new[:,1:-1,:] = (v_timestep[:,:-1,:] + v_timestep[:,1:,:])/2
            v_new[:,0,:] = u_new[:,1,:]
            v_new[:,-1,:] = u_new[:,-1,:]

            u_rho[i_time,:,:,:] = u_new
            v_rho[i_time,:,:,:] = v_new

        d["u_rho"].units = d.variables["u"].units
        d["u_rho"].long_name = f"{d.variables["u"].long_name} averaged to RHO points"
        d["u_rho"].coordinates = "lon_rho lat_rho s_rho"

        d["v_rho"].units = d.variables["v"].units
        d["v_rho"].long_name = f"{d.variables["v"].long_name} averaged to RHO points"
        d["v_rho"].coordinates = "lon_rho lat_rho s_rho"


