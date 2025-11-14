import xarray as xr
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("trackingfile", type=str)
args = parser.parse_args()

tracking_file = args.trackingfile

with xr.open_zarr(tracking_file) as ds:
    lons = ds.lon.values

print(lons.shape[1])
