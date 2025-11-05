import numpy as np
import xarray as xr
import argparse
from glob import glob

parser = argparse.ArgumentParser()
parser.add_argument("trackingdir", type=str)
args = parser.parse_args()

tracking_dir_parent = args.trackingdir

unique_starting_times_pre = []

tracking_dir_children = sorted(glob(f"{tracking_dir_parent}/*"))

for tracking_dir in tracking_dir_children:
    tracking_files = sorted(glob(f'{tracking_dir}/*.zarr'))
    for tracking_file in tracking_files:
        with xr.open_zarr(tracking_file) as ds:
            times = ds.time.values
        unique_starting_times_pre += list(np.unique(times[:,0]))
        print(tracking_file)
    #break

unique_starting_times = np.unique(unique_starting_times_pre)

print(unique_starting_times)

