import netCDF4
import numpy as np
import math
from scipy.interpolate import griddata

input_file_path = "/home/blaughli/tracking_project_v2/grid_data/wcr30test1_grd.nc"

output_file_path = "lookup_table_data_WCR30_v1.nc"
#output_file_path = "/home/blaughli/parcels/general_code/lookup_tables/lookup_table_data_WCR30_v1.nc"
#output_file_path = 'lookup_table_data_WCR30.nc'


#degree_fraction_table = 100 
#degree_fraction_table_base = 10

degree_fraction_table = 50
num_decimal_places_correct = 2 # now just hardcoding, since I know that 1/50 = 0.02, so any higher precision in arange output is a floating point error
#degree_fraction_table = 25
#degree_fraction_table_base = 5

#num_decimal_places_correct = int(np.log10(degree_fraction_table))
#num_decimal_places_correct = int(math.log(degree_fraction_table,degree_fraction_table_base))


with netCDF4.Dataset(input_file_path, 'r') as dset:
    h = np.array(dset['h'][:])
    lon_rho = np.array(dset['lon_rho'][:])
    lat_rho = np.array(dset['lat_rho'][:])
    mask_rho = np.array(dset['mask_rho'][:])
   
lon_max = np.ceil(np.max(lon_rho) * degree_fraction_table) / degree_fraction_table
lon_min = np.floor(np.min(lon_rho) * degree_fraction_table) / degree_fraction_table
lat_max = np.ceil(np.max(lat_rho) * degree_fraction_table) / degree_fraction_table
lat_min = np.floor(np.min(lat_rho) * degree_fraction_table) / degree_fraction_table

lon_table_vector = np.round(np.arange(lon_min,lon_max + 1/degree_fraction_table, 1/degree_fraction_table), num_decimal_places_correct)
lat_table_vector = np.round(np.arange(lat_min,lat_max + 1/degree_fraction_table, 1/degree_fraction_table), num_decimal_places_correct)

lon_table, lat_table = np.meshgrid(lon_table_vector,lat_table_vector)

table_h_vector = griddata(np.array((lon_rho.ravel(), lat_rho.ravel())).T, h.ravel(), np.array((lon_table.ravel(), lat_table.ravel())).T)
table_h = np.reshape(table_h_vector, lon_table.shape)

table_landmask_vector = griddata(np.array((lon_rho.ravel(), lat_rho.ravel())).T, mask_rho.ravel(), np.array((lon_table.ravel(), lat_table.ravel())).T)
table_landmask = np.reshape(table_landmask_vector, lon_table.shape)



with netCDF4.Dataset(output_file_path, 'w', format='NETCDF4') as nc_file:

    nc_file.createDimension('lat', len(lat_table_vector))
    nc_file.createDimension('lon', len(lon_table_vector))
    nc_file.createDimension('dummy', 1)

    # coordinate variables
    lat_var = nc_file.createVariable('lat_table', 'f4', ('lat'))
    lon_var = nc_file.createVariable('lon_table', 'f4', ('lon'))
    dummy_var = nc_file.createVariable('dummy_dim', 'f4', ('dummy'))

    # data variables
    h_var = nc_file.createVariable('h_table', 'f4', ('lat', 'lon'))
    landmask_var = nc_file.createVariable('landmask_table', 'f4', ('lat', 'lon'))
    degree_fraction_var = nc_file.createVariable('degree_fraction_table', 'f4', ('dummy'))
    

    # Attributes
    nc_file.description = 'Lookup table data for h (bathymetry) and landmask'
    lat_var.units = 'degrees_north, at regular intervals of degree_fraction_table'
    lon_var.units = 'degrees_east, at regular intervals of degree_fraction_table'
    degree_fraction_var.long_name = 'Resolution of lookup table, as denominator of fraction of a degree' 
    landmask_var.long_name = "Lookup table data for landmask"
    h_var.long_name = "Lookup table data for h"

    # Write data    
    lon_var[:] = lon_table_vector
    lat_var[:] = lat_table_vector
    dummy_var[:] = 1

    h_var[:] = table_h
    landmask_var[:] = table_landmask
    degree_fraction_var[:] = degree_fraction_table








