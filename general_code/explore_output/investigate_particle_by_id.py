import os
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import netCDF4
import argparse
from pathlib import Path
from glob import glob

import parcels


parser = argparse.ArgumentParser()
parser.add_argument("trackingdir", type=str)
parser.add_argument("particleid", type=int)
args = parser.parse_args()

tracking_dir = args.trackingdir
particle_id = args.particleid


tracking_files = sorted(glob(f'{tracking_dir}/*.zarr'))
num_files = len(tracking_files)
'''
tracking_file = tracking_files[1]
#tracking_file = tracking_files[0]
with xr.open_zarr(tracking_file) as ds:
    lons = ds.lon.values
    lats = ds.lat.values
    zs = ds.z.values
    ages = ds.age.values
    times = ds.time.values
    trajectorys = ds.trajectory.values
'''

#print(lons.shape)

file_dex = 0

for tracking_file in tracking_files:
#for tracking_file in tracking_files[1:]:

    with xr.open_zarr(tracking_file) as ds:
        lons = ds.lon.values
        lats = ds.lat.values
        zs = ds.z.values
        ages = ds.age.values
        times = ds.time.values
        trajectorys = ds.trajectory.values

    if particle_id in trajectorys:
        break

    file_dex += 1



particle_dex = int(np.where(trajectorys==particle_id)[0][0])

lons_p = lons[particle_dex]
lats_p = lats[particle_dex]
zs_p = zs[particle_dex]
ages_p = ages[particle_dex]



