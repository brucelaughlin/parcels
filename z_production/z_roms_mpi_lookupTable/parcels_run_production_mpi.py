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

parser = argparse.ArgumentParser()
parser.add_argument("--modelfilesdir", type=str)
parser.add_argument("--fileindex", type=int)
parser.add_argument("--seedperiodindex", type=int)
parser.add_argument("--dtcalcmins", type=int)
parser.add_argument("--dtoutmins", type=int)
parser.add_argument("--particlelifetimedays", type=int)
parser.add_argument("--currentyear", type=int)
parser.add_argument("--outputdirgeneral", type=str)
parser.add_argument("--initialseeddayindexcurrentrun", type=int)
parser.add_argument("--currentseedperiodlength", type=int)

args = parser.parse_args()

dataset_folder = args.modelfilesdir
file_index = args.fileindex
seed_period_index = args.seedperiodindex
current_year = args.currentyear
dt_calc_mins = args.dtcalcmins
dt_out_mins = args.dtoutmins
particle_lifetime_days = args.particlelifetimedays
initial_seed_day_index_current_run = args.initialseeddayindexcurrentrun
current_seed_period_length = args.currentseedperiodlength
output_dir_general = args.outputdirgeneral

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


UCSCParticle = parcels.ScipyParticle.add_variables(
    [
    parcels.Variable("age", initial=0),
    parcels.Variable("bottomDepth", initial=0),
    ]
)

with Dataset(static_file, 'r') as dset:
    h = np.array(dset['h'][:])


#--------- Get seeding lon/lat coordinates data ------------
file = open(polygon_seed_lon_lat_file,'rb')
list_of_arrays_of_points_in_polygons_lonlat = pickle.load(file)
file.close
file = open(polygon_seed_ii_jj_file,'rb')
list_of_arrays_of_points_in_polygons_iijj = pickle.load(file)
file.close

num_polygons = len(list_of_arrays_of_points_in_polygons_lonlat)

num_shallow_columns = 0


zs = []
lons = []
lats = []

for i_polygon in range(num_polygons):

    '''
    # ----------------
    # TESTING
    #if i_polygon > 10:
    #if i_polygon > 0:
    #if i_polygon != 200:
    #    continue
    #    break
    # ----------------
    '''

    for j_point in range(np.shape(list_of_arrays_of_points_in_polygons_lonlat[i_polygon])[1]):
        bottom_depth = h[list_of_arrays_of_points_in_polygons_iijj[i_polygon][0,j_point],list_of_arrays_of_points_in_polygons_iijj[i_polygon][1,j_point]]
        depth_min = np.floor(min(min_float_depth,bottom_depth))
        
        for k_depth in range(int(np.floor(depth_min / depth_step)) + 1):
            if k_depth == 0:
                zs.append(-1 * shallow_seed_depth)
            else:
                zs.append(-k_depth*depth_step)
            lons.append(list_of_arrays_of_points_in_polygons_lonlat[i_polygon][0,j_point])
            lats.append(list_of_arrays_of_points_in_polygons_lonlat[i_polygon][1,j_point])

'''
# More Testing
for ii in range(10000):
    lons.append(-127.5 + np.random.uniform(-0.5,0.5))
    lats.append(35 + np.random.uniform(-0.5,0.5))
    #zs.append(-50)
    zs.append(50)
'''



variables = {
    "U":    "u_east",      
    "V":    "v_north",
    "W":    "w",
    "zeta": "zeta",
    "z_rho":"z_rho_plus_2",
    "z_w":  "z_w",
    #"H":    "h",
    #"landmask": "mask_rho",
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
    #"H": static_file,   # Note that Clark's WCR30 files contain h as a variable
    #"landmask": static_file,
    "h_table":    "lookup_table_file",
    "landmask_table": "lookup_table_file",
    "degree_fraction_table": "lookup_table_file",
}

dimensions = {
    "U":     {"lon":"lon_u",   "lat":"lat_u",   "depth":"not_yet_set", "time":"ocean_time"},
    "V":     {"lon":"lon_v",   "lat":"lat_v",   "depth":"not_yet_set", "time":"ocean_time"},
    "W":     {"lon":"lon_rho","lat":"lat_rho","depth":"not_yet_set", "time":"ocean_time"},
    "zeta":  {"lon":"lon_rho","lat":"lat_rho","time":"ocean_time"},
    "z_rho": {"lon":"lon_rho","lat":"lat_rho","depth":"not_yet_set", "time":"ocean_time"},
    "z_w":   {"lon":"lon_rho","lat":"lat_rho","depth":"not_yet_set", "time":"ocean_time"},
    #"H":     {"lon":"lon_rho","lat":"lat_rho"},
    #"landmask":     {"lon":"lon_rho","lat":"lat_rho"},
    "h_table":     {"lon":"lon_table","lat":"lat_table"},
    "landmask_table":     {"lon":"lon_table","lat":"lat_table"},
    "degree_fraction_table": {},
}

fieldset = parcels.FieldSet.from_netcdf(filenames, variables, dimensions)
#fieldset = parcels.FieldSet.from_netcdf(filenames, variables, dimensions, chunksize=chunksize)

fieldset.landmask.interp_method = "nearest"

# Now input the true depths:
# tell Parcels that U/V live on the z_rho field, W on z_w
fieldset.U.set_depth_from_field(fieldset.z_rho)
fieldset.V.set_depth_from_field(fieldset.z_rho)
fieldset.W.set_depth_from_field(fieldset.z_w)


pset = parcels.ParticleSet(
    fieldset=fieldset, 
    pclass=UCSCParticle,
    lon=lons, 
    lat=lats, 
    depth=zs,
    repeatdt = timedelta(days=repeatdt_days),
    time = start_date,
)



# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# SUPER HACKY - STILL NEED TO MAKE PARTICLE LIFETIME A VARIABLE THAT CAN BE ACCESSED WITHIN THE KERNELS SOMEHOW.  
# Must add kernels dealing with "particle.state" at the END of the kernels list (see https://docs.oceanparcels.org/en/latest/examples/tutorial_kernelloop.html#Working-with-Status-Codes  last paragraph)
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
if particle_lifetime_days == 10:
    kernels = [parcels.AdvectionRK4_3D, parcels_util.KeepAboveBottom, parcels_util.KeepBelowSurface, parcels_util.AvoidLand, parcels_util.TidalKick, parcels_util.particleAgeLimit_10, parcels_util.DeleteParticle, parcels_util.DeleteOutOfBounds]
elif particle_lifetime_days == 180:
    kernels = [parcels.AdvectionRK4_3D, parcels_util.KeepAboveBottom, parcels_util.KeepBelowSurface, parcels_util.AvoidLand, parcels_util.TidalKick, parcels_util.particleAgeLimit_180, parcels_util.DeleteParticle, parcels_util.DeleteOutOfBounds]
else:
    print("Currently only supporting particle lifetime of 10 or 180... need to make this dynamic")
    sys.exit(1)
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



output_file = pset.ParticleFile(name=output_file_name, outputdt=timedelta(minutes=dt_out_mins), chunks = (chunk_output_particle, chunk_output_time))

t_setup_end = time.time()


pset.execute(
    kernels,
    dt=timedelta(minutes=dt_calc_mins),
    runtime=timedelta(days=current_seed_period_length),
    output_file=output_file,
)

pset.repeatdt = None

runtime_buffer_days = 3

pset.execute(
    kernels,
    dt=timedelta(minutes=dt_calc_mins),
    runtime=timedelta(days=(particle_lifetime_days + runtime_buffer_days)),
    output_file=output_file,
)



t_run_end = time.time()

setup_time = t_setup_end-t_init
runtime = t_run_end-t_init

total_setuptime_hours = round(setup_time/3600,3)
total_runtime_hours = round(runtime/3600,3)

print(f"Finished!")
print(f"Setup time: {total_setuptime_hours} hours")
print(f"Runtime time: {total_runtime_hours} hours")


