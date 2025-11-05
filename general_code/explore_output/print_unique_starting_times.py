import numpy as np
import xarray as xr
import argparse
from glob import glob

parser = argparse.ArgumentParser()
parser.add_argument("trackingdir", type=str)
parser.add_argument("filedex", type=int, nargs="?")
args = parser.parse_args()

tracking_dir = args.trackingdir
file_index = args.filedex

tracking_files = sorted(glob(f'{tracking_dir}/*.zarr'))

#unique_starting_times_pre = []
ust_p = []

for tracking_file in tracking_files:

    if file_index is not None:
        tracking_file = tracking_files[file_index]

    with xr.open_zarr(tracking_file) as ds:
        times = ds.time.values

    #unique_starting_times_pre += list(np.unique(times[:,0]))
    ust_p += list(np.unique(times[:,0]))
    

    if file_index is not None:
        break


#unique_starting_times = np.unique(unique_starting_times_pre)
ust = np.unique(ust_p)


#print(unique_starting_times)
print(ust)

