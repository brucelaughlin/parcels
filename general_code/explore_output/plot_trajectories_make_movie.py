import os
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import netCDF4
import argparse
from pathlib import Path

import parcels

save_dir = f"{os.getcwd()}/z_movie_frames_try1" 

os.makedirs(save_dir, exist_ok = True)

parser = argparse.ArgumentParser()
parser.add_argument("trackingfile", type=str)
args = parser.parse_args()

tracking_file = args.trackingfile
with xr.open_zarr(tracking_file) as ds:
    lons = ds.lon.values
    lats = ds.lat.values
#    ages = ds.age.values
#    times = ds.time.values
    zs = ds.z.values

grid_file = "/home/blaughli/tracking_project_v2/grid_data/wcr30test1_grd.nc"
with netCDF4.Dataset(grid_file,"r") as d:
    lat_rho = d[f"lat_rho"][:].data
    lon_rho = d[f"lon_rho"][:].data
    mask_rho = d[f"mask_rho"][:].data
#    h = d[f"h"][:].data

num_particles = lons.shape[0]

num_frames = 100

num_floats_per_frame = int(np.ceil(num_particles/num_frames))

float_dex_start = 0

for i_frame in range(num_frames):

    print(f"{i_frame:02d}/{num_frames}")

    fig,ax = plt.subplots()
    ax.set_title(f"{i_frame:02d}\n{Path(tracking_file).stem}")
    ax.pcolormesh(lon_rho,lat_rho,mask_rho)
   
    # Can't think
    if i_particle >= num_particles:
        break
    
    for i_particle in range(float_dex_start, float_dex_start + num_floats_per_frame):
        ax.plot(lons[i_particle,:],lats[i_particle,:])

    plt.savefig(f"{save_dir}/figure_{i_frame:02d}")
    plt.close(fig)

    float_dex_start += num_floats_per_frame


