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
    #lons = ds.lon.values
    #lats = ds.lat.values
    #ages = ds.age.values
    #times = ds.time.values
    zs = ds.z.values
    #ids = ds.id.values

#print(tracking_file)
#print(np.unique(times[:,0]))

#print(f"Total: ")
print(f"Positive: {np.sum(zs > 0)}")
print(f"Negative: {np.sum(zs < 0)}")

print(f"Ratio: {np.sum(zs > 0)/np.sum(zs <= 0)}")

