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
args = parser.parse_args()

tracking_file = args.trackingfile


with xr.open_zarr(tracking_file) as ds:
    lons = ds.lon.values
    lats = ds.lat.values
    ages = ds.age.values
    times = ds.time.values
    zs = ds.z.values

print(tracking_file)
print(np.unique(times[:,0]))



lons_unique_per_particle = []
lats_unique_per_particle = []
zs_unique_per_particle = []
ages_unique_per_particle = []

nbins = 100

#ages_per_particle = np.zeros(ages.shape[0])
ages_per_particle = []

for i_float in range(lons.shape[0]):
#    lons_unique_per_particle.append(len(np.unique(lons[i_float,:])))
#    lats_unique_per_particle.append(len(np.unique(lats[i_float,:])))
#    zs_unique_per_particle.append(len(np.unique(zs[i_float,:])))
#    ages_unique_per_particle.append(len(np.unique(ages[i_float,:])))
    n_unique = len(np.unique(ages[i_float,:])) # Remember that NaN counts as unique.  So subtract 1 if this number is less than the max
    #ages_per_particle[i_float] += n_unique
    ages_per_particle.append(n_unique)

plt.plot(ages_per_particle)
plt.show()
