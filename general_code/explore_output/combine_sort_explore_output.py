import os
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import netCDF4
import argparse
from glob import glob
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("trackingdir", type=str)
parser.add_argument("mpiflag", type=str, nargs="?")
args = parser.parse_args()

tracking_dir = args.trackingdir
mpi_flag = args.mpiflag

tracking_files = sorted(glob(f'{tracking_dir}/*.zarr'))
num_files = len(tracking_files)

#tracking_file = tracking_files[1]
tracking_file = tracking_files[0]
with xr.open_zarr(tracking_file) as ds:
    lons = ds.lon.values
    lats = ds.lat.values
    zs = ds.z.values
    ages = ds.age.values
    times = ds.time.values

print(lons.shape)

for tracking_file in tracking_files[1:]:

    with xr.open_zarr(tracking_file) as ds:
        lons = np.concatenate((lons, ds.lon.values), axis=0)
        lats = np.concatenate((lats, ds.lat.values), axis=0)
        zs = np.concatenate((zs, ds.z.values), axis=0)
        ages = np.concatenate((ages, ds.age.values), axis=0)
        times = np.concatenate((times, ds.time.values), axis=0)

    print(lons.shape)

sorting_key = lons[:,0].argsort().astype(int)

lons = lons[sorting_key]
lats = lats[sorting_key]
zs = zs[sorting_key]
ages = ages[sorting_key]
times = times[sorting_key]

if mpi_flag is not None:
    lons_mpi = lons.copy()
    lats_mpi = lats.copy()
    zs_mpi = zs.copy()
    ages_mpi = ages.copy()
    times_mpi = times.copy()
else:
    lons_nmpi = lons.copy()
    lats_nmpi = lats.copy()
    zs_nmpi = zs.copy()
    ages_nmpi = ages.copy()
    times_nmpi = times.copy()












