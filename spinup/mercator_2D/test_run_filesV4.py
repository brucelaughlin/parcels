#!/usr/bin/env python


output_file_name_stem = f"test_output__filesV4_postCrash"
# -----------------


import time
import os
import math
from datetime import timedelta
from operator import attrgetter

import matplotlib.pyplot as plt
import numpy as np
import trajan as ta
import xarray as xr
from IPython.display import HTML
from matplotlib.animation import FuncAnimation
import netCDF4
import pickle
from glob import glob

import parcels

t_init = time.time()

particle_lifetime_days = 10
#particle_lifetime_days = 180
run_dt_minutes = 60
max_depth_meters = 20
output_dt_hours = 24
#output_dt_hours = 1
#repeatdt = timedelta(days = 2)
#repeatdt = timedelta(days = 180)

output_dir_stem = "z_output"
output_dir = os.path.join(os.getcwd(), output_dir_stem)
os.makedirs(output_dir, exist_ok = True)

dataset_folder = "/home/blaughli/u_Mercator_forcing_files/global-reanalysis-phy-001-030-daily_1993_V4"

model_files = sorted(glob(f'{dataset_folder}/*.nc'))

#'''
# -----------------
# TESTING
#model_files = model_files[:2]
model_files = model_files[:1]
# -----------------
#'''

model_sample_file = model_files[0]

#model_sample_file = "/home/blaughli/u_Mercator_forcing_files/global-reanalysis-phy-001-030-daily_1993_2024/global-reanalysis-phy-001-030-daily_1993.nc"

output_file_name = os.path.join(output_dir,output_file_name_stem)

with netCDF4.Dataset(model_sample_file, 'r') as dset:
    model_depth_level_vector = np.array(dset["depth"][:])
#    h = np.array(dset['sea_floor_depth_below_sea_level'][:])  # h will have different name in different models
    time_units = dset["time"].units

static_file = "/data04/cedwards/forcing/mercator/reanalysis12/cmems_mod_glo_phy_my_0.083deg_static_depths.nc"

with netCDF4.Dataset(static_file, 'r') as dset:
    h = np.array(dset['deptho'][:])  # h will have different name in different models



#time_reference_year = int(time_units.split("since")[-1].split('-')[0])  # 1950
time_reference_units = time_units.split("since")[0].strip()  # "hours"

#'''
max_time_offset = 0
min_time_offset = 1e10
file_dex = 0
num_files = len(model_files)
for model_file in model_files:
    file_dex += 1
    print(f"file {file_dex}/{num_files}")
    with netCDF4.Dataset(model_file, 'r') as dset:
        max_time_offset_file = int(dset["time"][:].data[-1])
        min_time_offset_file = int(dset["time"][:].data[0])
    if max_time_offset_file > max_time_offset:
        max_time_offset = max_time_offset_file
    if min_time_offset_file < min_time_offset:
        min_time_offset = min_time_offset_file
    # TESTING
    break

time_reference_units_to_run = max_time_offset - min_time_offset
#'''

seed_depths_general = model_depth_level_vector[model_depth_level_vector < max_depth_meters]
num_floats_per_column_max = len(seed_depths_general)




#######################################################################################
#######################################################################################
#######################################################################################
# NOW IS THE TIME TO FIX THIS STUPID ARRAY-TO-LIST-TO-ARRAY STUFF THAT I USED TO DO!!!!!
# CHANGE THIS CRAP!!!!

# In other words, np.shape(list_of_arrays_of_points_in_polygons_lonlat[i_polygon])  is (2,1) for polygons with single points within...

# These are the files with Monica's points, which have many ON LAND points... waiting for her to write back
polygon_seed_lon_lat_file = "/home/blaughli/tracking_project_v2/misc/z_boxes/w_Mercator/raimondi_extra_cells/z_output/combined_oldNew_points_lon_lat_Mercator_singleCellPolygons.p"
polygon_seed_ii_jj_file = "/home/blaughli/tracking_project_v2/misc/z_boxes/w_Mercator/raimondi_extra_cells/z_output/combined_oldNew_points_i_j_Mercator_singleCellPolygons.p"


#polygon_seed_lon_lat_file = "/home/blaughli/tracking_project_v2/misc/z_boxes/c_MUST_RUN_determine_points_in_polygons/z_output/points_in_boxes_lon_lat_combined_Mercator_singleCellPolygons.p"
#polygon_seed_ii_jj_file = "/home/blaughli/tracking_project_v2/misc/z_boxes/c_MUST_RUN_determine_points_in_polygons/z_output/points_in_boxes_ii_jj_combined_Mercator_singleCellPolygons.p"


#--------- Get seeding lon/lat coordinates data ------------
file = open(polygon_seed_lon_lat_file,'rb')
list_of_arrays_of_points_in_polygons_lonlat = pickle.load(file)
file.close
file = open(polygon_seed_ii_jj_file,'rb')
list_of_arrays_of_points_in_polygons_iijj = pickle.load(file)
file.close

num_polygons = len(list_of_arrays_of_points_in_polygons_lonlat)

num_shallow_columns = 0

start_times = [0, 86400]

times = []
zs = []
lons = []
lats = []
#for k_time in start_times:
for i_polygon in range(num_polygons):

    '''
    # ----------------
    # TESTING
    if i_polygon > 0:
        break
    # ----------------
    '''

    for j_point in range(np.shape(list_of_arrays_of_points_in_polygons_lonlat[i_polygon])[1]):
        bottom_depth = h[list_of_arrays_of_points_in_polygons_iijj[i_polygon][0,j_point],list_of_arrays_of_points_in_polygons_iijj[i_polygon][1,j_point]]
        seed_depths_column = seed_depths_general[seed_depths_general < bottom_depth]
        if len(seed_depths_column) < num_floats_per_column_max:
#            print(f"polygon: {i_polygon}, seeded in column: {len(seed_depths_column)}/{num_floats_per_column_max}")
            num_shallow_columns += 1
        '''
        for seed_depth in seed_depths_column:
            zs.append(seed_depth)
            lons.append(list_of_arrays_of_points_in_polygons_lonlat[i_polygon][0,j_point])
            lats.append(list_of_arrays_of_points_in_polygons_lonlat[i_polygon][1,j_point])
            #times.append(k_time)
        '''
        zs.append(seed_depths_column[0])
        lons.append(list_of_arrays_of_points_in_polygons_lonlat[i_polygon][0,j_point])
        lats.append(list_of_arrays_of_points_in_polygons_lonlat[i_polygon][1,j_point])
        #times.append(0)




#print()
#print(f"Number of shallow columns: {num_shallow_columns}/{num_polygons}")

num_seeds_single_time = len(lons) # 8998
num_timesteps_single_particle_max = int((particle_lifetime_days * 24)/output_dt_hours)   # 180

chunks = (num_seeds_single_time * 10, num_timesteps_single_particle_max)
#chunks = (num_seeds_single_time * 10, 1)


#######################################################################################
#######################################################################################
#######################################################################################

filenames = {
    "U": model_files,
    "V": model_files,
}

variables = {
    "U": "u_all",
    "V": "v_all",
}

dimensions = {
    "U": {"lon":"lon_all", "lat":"lat_all", "depth":"depth", "time":"time"},
    "V": {"lon":"lon_all", "lat":"lat_all", "depth":"depth", "time":"time"}, 
    }



fieldset = parcels.FieldSet.from_netcdf(filenames, variables, dimensions, chunksize="auto")
#fieldset = parcels.FieldSet.from_netcdf(filenames, variables, dimensions)
#fieldset = parcels.FieldSet.from_netcdf(filenames, variables, dimensions, mesh="spherical")
#fieldset = parcels.FieldSet.from_netcdf(filenames, variables, dimensions, mesh="spherical", interp_method="cgrid_velocity")


pset = parcels.ParticleSet(
    fieldset=fieldset, pclass=parcels.JITParticle, lon=lons, lat=lats, depth=zs
    #fieldset=fieldset, pclass=parcels.JITParticle, lon=lons, lat=lats, depth=zs, time = times
    #fieldset=fieldset, pclass=parcels.JITParticle, lon=lons, lat=lats, depth=zs, repeatdt=repeatdt
)

outputdt = timedelta(hours=output_dt_hours)
output_file = pset.ParticleFile(
        name=output_file_name, 
        outputdt=outputdt,
        chunks=chunks,
        #chunks=(),
)


def CheckOutOfBounds(particle, fieldset, time):
    if particle.state == StatusCode.ErrorOutOfBounds:
        particle.delete()

t_setup_end = time.time()

'''
# For MPI testing, just run for 180 days
pset.execute(
    [parcels.AdvectionRK4, CheckOutOfBounds],
    runtime=timedelta(days=particle_lifetime_days),
    dt=timedelta(minutes=run_dt_minutes),
    output_file=output_file,
)
'''

#'''
if time_reference_units == "minutes":
    pset.execute(
        [parcels.AdvectionRK4, CheckOutOfBounds],
        dt=timedelta(minutes=run_dt_minutes),
#        endtime=timedelta(minutes=time_reference_units_to_run),
        output_file=output_file,
        runtime=timedelta(days=particle_lifetime_days)
    )
elif time_reference_units == "hours":
    pset.execute(
        [parcels.AdvectionRK4, CheckOutOfBounds],
        dt=timedelta(minutes=run_dt_minutes),
#        endtime=timedelta(hours=time_reference_units_to_run),
        output_file=output_file,
        runtime=timedelta(days=particle_lifetime_days)
    )
#'''

t_run_end = time.time()

setup_time = t_setup_end-t_init
runtime = t_run_end-t_init

total_setuptime_hours = round(setup_time/3600,3)
total_runtime_hours = round(runtime/3600,3)

print(f"Setup time: {total_setuptime_hours} hours")
print(f"Runtime time: {total_runtime_hours} hours")

