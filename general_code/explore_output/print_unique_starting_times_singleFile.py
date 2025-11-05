import numpy as np
import xarray as xr
import argparse
from glob import glob

parser = argparse.ArgumentParser()
parser.add_argument("trackingfile", type=str)
args = parser.parse_args()

tracking_file = args.trackingfile

with xr.open_zarr(tracking_file) as ds:
    times = ds.time.values
    lons = ds.lon.values
    lats = ds.lat.values
    zs = ds.z.values
    ages = ds.age.values


ust= list(np.unique(times[:,0]))

print(ust)

