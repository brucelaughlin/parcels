# ---------------------------------
# ---------------------------------
# Hardcoded bits...
# ---------------------------------
static_file = "/home/blaughli/tracking_project_v2/grid_data/wcr30test1_grd.nc"
polygon_seed_lon_lat_file = "/home/blaughli/tracking_project_v2/misc/z_boxes/add_Extra_Cells/z_output/combined_oldNew_points_lon_lat_WCR30_singleCellPolygons.p"
polygon_seed_ii_jj_file = "/home/blaughli/tracking_project_v2/misc/z_boxes/add_Extra_Cells/z_output/combined_oldNew_points_i_j_WCR30_singleCellPolygons.p"
dataset_folder_W = "/home/blaughli/symbolic_links_ROMS/WCR30_ERA_v1_1999_2024"

lookup_table_file = "/home/blaughli/parcels/general_code/lookup_tables/lookup_table_data_WCR30_v1.nc"

# ---------------------------------

repeatdt_days = 2

seed_spacing_days = 2

min_float_depth = 20
#depth_step = 5
depth_step = 2.5

shallow_seed_depth = 1
#shallow_seed_depth = 5
#shallow_seed_depth = 2.5

chunk_output_particle = int(1e6)
#chunk_output_time = 20
chunk_output_time = 10

#particle_lifetime_days = 180
#particle_lifetime_days = 20
#particle_lifetime_days = 10
# ---------------------------------
# ---------------------------------


import time
import os
import math
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from netCDF4 import Dataset
import pickle
from glob import glob
import argparse

import parcels_custom_util as parcels_util
import parcels



dataset_folder = "/home/blaughli/u_WCR30_forcing_files/wcr30_ERA1_v1_1999"
file_index = 0
seed_period_index = 0
current_year = 1999
dt_calc_mins = 60
dt_out_mins = 60 
particle_lifetime_days = 10
initial_seed_day_index_current_run = 0
current_seed_period_length = 10
output_dir_general = f"{os.getcwd()}/z_output_bruce"







# Copied start time algorithm from Jordana
start_of_year = datetime(current_year, 1, 1)
start_date = start_of_year + timedelta(days = initial_seed_day_index_current_run)
start_hour = 12 # all of our ROMS runs seem to save daily data at noon.  But always check
start_date = start_date.replace(hour=start_hour)


t_init = time.time()

print(f"Start time: {time.ctime()}")

dataset_folder_stem = Path(dataset_folder).stem

#output_dir_stem = f"z_output__runDir_{dataset_folder_stem}__dtCalcMins_{dt_calc_mins}_dtOutMins_{dt_out_mins}"
#output_dir = os.path.join(os.getcwd(), output_dir_stem)
#os.makedirs(output_dir, exist_ok = True)


output_file_name_stem = f"{Path(dataset_folder).stem}__fileIndex_{file_index:02d}__seedPeriodIndex_{seed_period_index:03d}"
output_file_name = os.path.join(output_dir_general,output_file_name_stem)

model_files = sorted(glob(f'{dataset_folder}/*.nc'))
model_files_W = sorted(glob(f'{dataset_folder_W}/*.nc'))

num_files = len(model_files)

# Use an input file list with a maximum length of 2 (My construction seeds for one year and then lets all floats run for their lifetime, which is assumed to be <1 year)
if file_index + 1 == num_files:
    model_files = model_files[file_index:]
    model_files_W = model_files_W[file_index:]
else:
    model_files = model_files[file_index:file_index + 2]
    model_files_W = model_files_W[file_index:file_index + 2]

variables = {
    "U":    "u_east",      
    "V":    "v_north",
    "W":    "w",
    "zeta": "zeta",
    "z_rho":"z_rho_plus_2",
    "z_w":  "z_w",
    "h_table":    "h_table",
    "landmask_table": "landmask_table",
    "degree_fraction_table": "degree_fraction_table",
}

filenames = {
    "U": model_files,
    "V": model_files,
    "W": model_files_W,
    "zeta": model_files,
    "z_rho": model_files,
    "z_w": model_files,
    "h_table":    lookup_table_file,
    "landmask_table": lookup_table_file,
    "degree_fraction_table": lookup_table_file,
}

dimensions = {
    "U":     {"lon":"lon_u",   "lat":"lat_u",   "depth":"not_yet_set", "time":"ocean_time"},
    "V":     {"lon":"lon_v",   "lat":"lat_v",   "depth":"not_yet_set", "time":"ocean_time"},
    "W":     {"lon":"lon_rho","lat":"lat_rho","depth":"not_yet_set", "time":"ocean_time"},
    "zeta":  {"lon":"lon_rho","lat":"lat_rho","time":"ocean_time"},
    "z_rho": {"lon":"lon_rho","lat":"lat_rho","depth":"not_yet_set", "time":"ocean_time"},
    "z_w":   {"lon":"lon_rho","lat":"lat_rho","depth":"not_yet_set", "time":"ocean_time"},
    "h_table":     {"lon":"lon_table","lat":"lat_table"},
    "landmask_table":     {"lon":"lon_table","lat":"lat_table"},
    "degree_fraction_table": {"lon":"dummy_dim"},
}

fieldset = parcels.FieldSet.from_netcdf(filenames, variables, dimensions)
#fieldset = parcels.FieldSet.from_netcdf(filenames, variables, dimensions, chunksize=chunksize)

# Now input the true depths:
# tell Parcels that U/V live on the z_rho field, W on z_w
fieldset.U.set_depth_from_field(fieldset.z_rho)
fieldset.V.set_depth_from_field(fieldset.z_rho)
fieldset.W.set_depth_from_field(fieldset.z_w)




