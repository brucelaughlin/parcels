import os
import matplotlib.pyplot as plt
import numpy as np
import trajan as ta
import xarray as xr
from IPython.display import HTML
from matplotlib.animation import FuncAnimation
import netCDF4
import argparse
import geopy.distance
from pathlib import Path

import parcels

static_file = "/data04/cedwards/forcing/mercator/reanalysis12/cmems_mod_glo_phy_my_0.083deg_static_depths.nc"

tracking_file = "/home/blaughli/parcels/processing/w_explore/z_output/tracking_data_problematic_particles_singleParticle.zarr"

if os.path.splitext(tracking_file)[-1] == ".zarr":
    with xr.open_zarr(tracking_file) as ds:
        lon_all = ds.lon.values
        lat_all = ds.lat.values
elif os.path.splitext(tracking_file)[-1] == ".nc":
    with netCDF4.Dataset(tracking_file) as ds:
        lon_all = np.array(ds["lon"][:])
        lat_all = np.array(ds["lat"][:])




lon_valid_list = []
lat_valid_list = []

for i_particle in range(lon_all.shape[0]):
    lon_particle = lon_all[i_particle,:]
    lat_particle = lat_all[i_particle,:]
    mask = np.logical_not(np.isnan(lon_particle))

    lon_valid_list.append(lon_particle[mask])
    lat_valid_list.append(lat_particle[mask])



with netCDF4.Dataset(static_file) as ds:
    mask_rho = np.array(ds["mask"][:])[0]
    lon_rho = np.array(ds["longitude"][:])
    lat_rho = np.array(ds["latitude"][:])

'''
with np.load(grid_file) as ds:
    mask_rho = ds["mask_rho"]
    lon_rho = ds["lon_rho"]
    lat_rho = ds["lat_rho"]
'''

lon,lat = np.meshgrid(lon_rho,lat_rho)
mask_ocean = mask_rho == 1
mask_land = mask_rho == 0

fig,ax = plt.subplots()

ax.pcolormesh(lon_rho,lat_rho,mask_rho)

for i_particle in range(len(lon_valid_list)):
    ax.plot(lon_valid_list[i_particle], lat_valid_list[i_particle])
    #ax.scatter(lons[:,0], lats[:,0], c='g', s=1, zorder=3)
    #ax.scatter(lons[:,-1], lats[:,-1], c='r', s=1, zorder=3)
    ax.scatter(lon_valid_list[i_particle][0], lat_valid_list[i_particle][0], c='g', s=20)
    ax.scatter(lon_valid_list[i_particle][-1], lat_valid_list[i_particle][-1], c='r', s=20)

plt.show()


