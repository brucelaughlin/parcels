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



