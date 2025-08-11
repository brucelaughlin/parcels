import os

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from datetime import timedelta

import parcels

# Open dataset lazily
ds = xr.open_dataset("/home/jsevigny/opendrift/working_data/test_wcofs/wcofs_20000101_roms_avg_wcofs.nc", chunks={'ocean_time': 1})

# Interpolate U to rho-points (eta-direction)
u_rho = 0.5 * (ds['u'].isel(eta_u=slice(0, -1)) + ds['u'].isel(eta_u=slice(1, None)))

# Interpolate V to rho-points (xi-direction)
v_rho = 0.5 * (ds['v'].isel(xi_v=slice(0, -1)) + ds['v'].isel(xi_v=slice(1, None)))

# After interpolation, get shapes:
eta_rho_size = u_rho.sizes['eta_u']
xi_rho_size = u_rho.sizes['xi_u']

# Subset lat_rho and lon_rho to match interpolated velocity grid:
lat_rho_subset = ds['lat_rho'].isel(
    eta_rho=slice(0, eta_rho_size),
    xi_rho=slice(0, xi_rho_size)
)
lon_rho_subset = ds['lon_rho'].isel(
    eta_rho=slice(0, eta_rho_size),
    xi_rho=slice(0, xi_rho_size)
)

# Create output dataset
ds_out = xr.Dataset(
    {
        'u_rho': (('ocean_time', 's_rho', 'eta_rho', 'xi_rho'), u_rho.data),
        'v_rho': (('ocean_time', 's_rho', 'eta_rho', 'xi_rho'), v_rho.data),
        'lat_rho': (('eta_rho', 'xi_rho'), lat_rho_subset.data),
        'lon_rho': (('eta_rho', 'xi_rho'), lon_rho_subset.data),
        'ocean_time': (('ocean_time',), ds['ocean_time'].values),
        's_rho': (('s_rho',), ds['s_rho'].values)
    }
)

# Save both together as a single NetCDF file
ds_out.to_netcdf('/home/jsevigny/opendrift/working_data/test_wcofs/interpolated_uv_rho.nc')


filenames = {
    "U": "/home/jsevigny/opendrift/working_data/test_wcofs/interpolated_uv_rho.nc",
    "V": "/home/jsevigny/opendrift/working_data/test_wcofs/interpolated_uv_rho.nc",
    "W": "/home/jsevigny/opendrift/working_data/test_wcofs/wcofs_20000101_roms_avg_wcofs.nc",
    "Zeta": "/home/jsevigny/opendrift/working_data/test_wcofs/wcofs_20000101_roms_avg_wcofs.nc",
    "Cs_w": "/home/jsevigny/opendrift/working_data/test_wcofs/wcofs_20000101_roms_avg_wcofs.nc",
    "H": "/data04/cpennell/data/wcofs_era5_temp_salt_calcofi/grd_wcofs4_visc200_50-50-50.nc"

}

variables = {"U": "u_rho", "V": "v_rho", "W": "w", "Zeta": "zeta", "Cs_w": "Cs_w", "H": "h"}


dimensions = {
    "U": {"time": "ocean_time", "depth": "s_rho", "lat": "lat_rho", "lon": "lon_rho"},
    "V": {"time": "ocean_time", "depth": "s_rho", "lat": "lat_rho", "lon": "lon_rho"},
    "W": {"time": "ocean_time", "depth": "s_w", "lat": "lat_rho", "lon": "lon_rho"},
    "H": {"lat": "lat_rho", "lon": "lon_rho"},
    "Zeta": {"time": "ocean_time", "lat": "lat_rho", "lon": "lon_rho"},
    "Cs_w": {"depth": "s_w"},
}

# FieldSet
fieldset = parcels.FieldSet.from_croco(
    filenames,
    variables,
    dimensions,
    hc=xr.open_dataset(
    "/home/jsevigny/opendrift/working_data/test_wcofs/wcofs_20000101_roms_avg_wcofs.nc"
    ).hc.values,
    allow_time_extrapolation=True)
