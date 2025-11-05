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

#tracking_file = "/home/blaughli/parcels/processing/w_explore/z_output/tracking_data_problematic_particles_singleParticle.zarr"
tracking_file = "/home/blaughli/parcels/processing/w_explore/z_output/tracking_data_problematic_particles_v1.zarr"

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

lon_problematic_list = []
lat_problematic_list = []


for i_particle in range(len(lon_valid_list)):
    if lon_valid_list[i_particle][-1] > -120.64 and lon_valid_list[i_particle][-1] < -120.54 and lat_valid_list[i_particle][-1] > 34.43 and  lat_valid_list[i_particle][-1] < 34.64:
        lon_problematic_list.append(lon_valid_list[i_particle])
        lat_problematic_list.append(lat_valid_list[i_particle])


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

fig,ax = plt.subplots()

ax.pcolormesh(lon_rho,lat_rho,mask_rho)

for i_particle in range(len(lon_problematic_list)):
    ax.plot(lon_problematic_list[i_particle], lat_problematic_list[i_particle])
    ax.scatter(lon_problematic_list[i_particle][0], lat_problematic_list[i_particle][0], c='g', s=20)
    ax.scatter(lon_problematic_list[i_particle][-1], lat_problematic_list[i_particle][-1], c='r', s=20)

plt.show()


