#!/usr/bin/env python

# V2: Removing the offshore kick; their implementation example was too crude.  Given the simplicity requirements for functions, still not sure how to add randomness in a function

import time
import os
import math
from datetime import datetime, timedelta
from operator import attrgetter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import trajan as ta
import xarray as xr
from IPython.display import HTML
from matplotlib.animation import FuncAnimation
from netCDF4 import Dataset
import pickle
from glob import glob
import psutil
from scipy import interpolate
import argparse

import parcels_custom_util as parcels_util
import parcels



parser = argparse.ArgumentParser()
parser.add_argument("--modelfilesdir", type=str)
parser.add_argument("--fileindex", type=int)
#parser.add_argument("--model-files-dir", type=str)
#parser.add_argument("--file-index", type=int)
args = parser.parse_args()

dataset_folder = args.modelfilesdir
file_index = args.fileindex

#print(f"File index: {file_index}")

t_init = time.time()



output_file_name_stem = f"{Path(dataset_folder).stem}__fileNumber_{file_index:02d}"


model_files = sorted(glob(f'{dataset_folder}/*.nc'))
#model_files_all = sorted(glob(f'{dataset_folder}/*.nc'))

num_files = len(model_files)

# Keep a maximum of 2 files

if file_index + 1 == num_files:
    model_files = model_files[file_index:]
else:
    model_files = model_files[file_index:file_index + 2]

model_sample_file = model_files[0]


AgeParticle = parcels.JITParticle.add_variable(parcels.Variable("age", initial=0))

# --------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------



chunksize_int = 768 # This performed best in tests, though all manual settings were close.  "auto" was worse, and "False" was much worse
chunksize = {"time": ("time", 1), "lat": ("latitude", chunksize_int), "lon": ("longitude", chunksize_int)}


chunk_output_particle = int(1e4) # Just a suggestion from the tutorial
chunk_output_time = 1

particle_lifetime_days = 180
run_dt_minutes = 60 # They suggest shortening this, especially when using the offshore kick
max_depth_meters = 20
#output_dt_hours = 1
output_dt_hours = 24

repeatdt_days = 2
#seed_period_total_days = 15

output_dir_stem = "z_output"
output_dir = os.path.join(os.getcwd(), output_dir_stem)
os.makedirs(output_dir, exist_ok = True)


year_0 = datetime(int(Path(model_files[0]).stem), 1, 1)
year_1 = datetime(int(Path(model_files[0]).stem) + 1, 1, 1)

year_delta = year_1 - year_0

seed_period_total_days = int(year_delta.total_seconds()/86400)

if file_index + 1 == num_files:
    seed_period_total_days -= particle_lifetime_days




output_file_name = os.path.join(output_dir,output_file_name_stem)

with Dataset(model_sample_file, 'r') as dset:
    model_depth_level_vector = np.array(dset["depth"][:])
#    h = np.array(dset['sea_floor_depth_below_sea_level'][:])  # h will have different name in different models
    time_units = dset["time"].units

static_file = "/data04/cedwards/forcing/mercator/reanalysis12/cmems_mod_glo_phy_my_0.083deg_static_depths.nc"

with Dataset(static_file, 'r') as dset:
    h = np.array(dset['deptho'][:])  # h will have different name in different models


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


times = []
zs = []
lons = []
lats = []
#for k_time in start_times:
for i_polygon in range(num_polygons):

    '''
    # ----------------
    # TESTING
    #if i_polygon > 0:
    if i_polygon != 200:
        continue
        #break
    # ----------------
    '''

    for j_point in range(np.shape(list_of_arrays_of_points_in_polygons_lonlat[i_polygon])[1]):
        bottom_depth = h[list_of_arrays_of_points_in_polygons_iijj[i_polygon][0,j_point],list_of_arrays_of_points_in_polygons_iijj[i_polygon][1,j_point]]
        seed_depths_column = seed_depths_general[seed_depths_general < bottom_depth]

        if len(seed_depths_column) < num_floats_per_column_max:
#            print(f"polygon: {i_polygon}, seeded in column: {len(seed_depths_column)}/{num_floats_per_column_max}")
            num_shallow_columns += 1
        for seed_depth in seed_depths_column:
            zs.append(seed_depth)
            lons.append(list_of_arrays_of_points_in_polygons_lonlat[i_polygon][0,j_point])
            lats.append(list_of_arrays_of_points_in_polygons_lonlat[i_polygon][1,j_point])
        



num_seeds_single_time = len(lons) # 8998
num_timesteps_single_particle_max = int((particle_lifetime_days * 24)/output_dt_hours)   # 180

#chunks = (num_seeds_single_time * 10, num_timesteps_single_particle_max)
#chunks = (num_seeds_single_time * 10, 1)


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


fieldset = parcels.FieldSet.from_netcdf(filenames, variables, dimensions, chunksize=chunksize)


pset = parcels.ParticleSet(
    fieldset=fieldset, 
    pclass=AgeParticle,
    lon=lons, 
    lat=lats, 
    depth=zs, 
    repeatdt = timedelta(days = repeatdt_days),
)

kernels = [parcels.AdvectionRK4, parcels_util.CheckOutOfBounds, parcels_util.particleAgeLimit_180]

output_file = pset.ParticleFile(name=output_file_name, outputdt=timedelta(hours=output_dt_hours), chunks = (chunk_output_particle, chunk_output_time))


t_setup_end = time.time()


pset.execute(
    kernels, 
    dt=timedelta(minutes=run_dt_minutes),
    runtime=timedelta(days=seed_period_total_days),
    output_file=output_file
)

pset.repeatdt = None

pset.execute(
    kernels,
    dt=timedelta(minutes=run_dt_minutes),
    runtime=timedelta(days=particle_lifetime_days),
    output_file=output_file
)





t_run_end = time.time()

setup_time = t_setup_end-t_init
runtime = t_run_end-t_init

total_setuptime_hours = round(setup_time/3600,3)
total_runtime_hours = round(runtime/3600,3)

print(f"Finished!")
print(f"Setup time: {total_setuptime_hours} hours")
print(f"Runtime time: {total_runtime_hours} hours")


