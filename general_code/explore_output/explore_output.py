import os
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import netCDF4
import argparse
from pathlib import Path

import parcels


parser = argparse.ArgumentParser()
parser.add_argument("trackingfile", type=str)
parser.add_argument("plotFlag", type=str, nargs= "?")
args = parser.parse_args()

tracking_file = args.trackingfile
plot_flag = args.plotFlag


with xr.open_zarr(tracking_file) as ds:
    lons = ds.lon.values
    lats = ds.lat.values
    ages = ds.age.values
    times = ds.time.values
    zs = ds.z.values
    #ids = ds.id.values

print(tracking_file)
print(np.unique(times[:,0]))


if plot_flag is not None:

    lons_unique_per_particle = []
    lats_unique_per_particle = []
    zs_unique_per_particle = []
    ages_unique_per_particle = []

    #nbins = 100
    nbins = 1000

    for i_float in range(lons.shape[0]):
        lons_unique_per_particle.append(len(np.unique(lons[i_float,:])))
        lats_unique_per_particle.append(len(np.unique(lats[i_float,:])))
        zs_unique_per_particle.append(len(np.unique(zs[i_float,:])))
        ages_unique_per_particle.append(len(np.unique(ages[i_float,:])))

    figsize = (16,9)
    fig,ax = plt.subplots(2,2, figsize=figsize)

    ax[0,0].hist(lons_unique_per_particle, bins=nbins)
    ax[0,0].set_title("lon")
    ax[0,1].hist(lats_unique_per_particle, bins=nbins)
    ax[0,1].set_title("lat")
    ax[1,0].hist(zs_unique_per_particle, bins=nbins)
    ax[1,0].set_title("z")
    ax[1,1].hist(ages_unique_per_particle, bins=nbins)
    ax[1,1].set_title("age")

    title = f"Histogram of unique values in trajectories\nnum particles: {lons.shape[0]}\nfile:  {tracking_file.split('/')[-2]}/{tracking_file.split('/')[-1]}"
    #title = f"Histogram of unique values in trajectories\n{tracking_file.split('/')[-2]}\nnum particles: {lons.shape[0]}"

    fig.suptitle(title)

    plt.show()

