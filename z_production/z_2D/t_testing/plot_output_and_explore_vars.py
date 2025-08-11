import os
import matplotlib.pyplot as plt
import numpy as np
import trajan as ta
import xarray as xr
from IPython.display import HTML
from matplotlib.animation import FuncAnimation
import netCDF4

import parcels
import argparse

grid_file = "/home/blaughli/tracking_project_v2/grid_data/mercator_diy_grid_withDepths.npz"

#tracking_file = "/home/blaughli/parcels/spinup/mercator_2D/z_output/x_old/x_old1/test_output_fullDomain_5days_mpiTest2/proc00.zarr"
#tracking_file = "/home/blaughli/parcels/z_production/z_2D/t_testing/z_output/test_age_v2.zarr"
#tracking_file = "/home/blaughli/parcels/z_production/z_2D/t_testing/z_output/test_age_v1.zarr"


#'''
parser = argparse.ArgumentParser()
parser.add_argument("trackingfile", type=str)
#parser.add_argument("gridfile", type=str)
args = parser.parse_args()

tracking_file = args.trackingfile
#grid_file = args.gridfile
#'''

with np.load(grid_file) as ds:
    mask_rho = ds["mask_rho"]
    lon_rho = ds["lon_rho"]
    lat_rho = ds["lat_rho"]



lon,lat = np.meshgrid(lon_rho,lat_rho)

mask_ocean = mask_rho == 1
mask_land = mask_rho == 0


plt.pcolormesh(lon_rho,lat_rho,mask_rho)


with xr.open_zarr(tracking_file) as ds:

    lons = ds.lon
    lats = ds.lat
    zs = ds.z
    times = ds.time
    #dt = ds.dt

'''
plt.plot(ds.lon.T, ds.lat.T)


plt.scatter(lon[mask_land], lat[mask_land], c='w', zorder=3)
plt.scatter(lon[mask_ocean], lat[mask_ocean], c='k', zorder=3)

plt.scatter(ds.lon.values[:,0], ds.lat.values[:,0],c='r', zorder=3)


plt.show()
'''

