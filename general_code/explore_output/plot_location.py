import os
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import netCDF4
import argparse
from pathlib import Path


# ------------------------------------------------------------------------------------------------
#save_dir = f"{os.getcwd()}/z_figures_trajectoriesByLifetime" 
#os.makedirs(save_dir, exist_ok = True)

#lifetime_buffer = 5
# ------------------------------------------------------------------------------------------------


parser = argparse.ArgumentParser()
parser.add_argument("lon", type=float)
parser.add_argument("lat", type=float)
args = parser.parse_args()

lon = args.lon
lat = args.lat

grid_file = "/home/blaughli/tracking_project_v2/grid_data/wcr30test1_grd.nc"
with netCDF4.Dataset(grid_file,"r") as d:
    lat_rho = d[f"lat_rho"][:].data
    lon_rho = d[f"lon_rho"][:].data
    mask_rho = d[f"mask_rho"][:].data
    h = d[f"h"][:].data

fig,ax = plt.subplots()
ax.pcolormesh(lon_rho,lat_rho,mask_rho)
ax.scatter(lon,lat, c= 'r', s=50)
plt.show()

#plt.savefig(f"{save_dir}/figure_{i_frame:02d}")
#plt.close(fig)





