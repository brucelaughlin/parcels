
#output_file_name_stem = "tracking_data_problematic_particles_v1"
output_file_name_stem = "tracking_data_problematic_particles_singleParticle"


import time
import os
import math
from datetime import datetime, timedelta
#from operator import attrgetter
from pathlib import Path

#import matplotlib.pyplot as plt
import numpy as np
#import trajan as ta
#import xarray as xr
#from IPython.display import HTML
#from matplotlib.animation import FuncAnimation
from netCDF4 import Dataset
import pickle
from glob import glob
#import psutil
#from scipy import interpolate
import argparse

import parcels_custom_util as parcels_util
import parcels


'''
parser = argparse.ArgumentParser()
parser.add_argument("--modelfilesdir", type=str)
parser.add_argument("--fileindex", type=int)
#parser.add_argument("--chunksize", type=int)
args = parser.parse_args()

dataset_folder = args.modelfilesdir
file_index = args.fileindex
#chunk_output_particle = args.chunksize
'''

dataset_folder = "/home/blaughli/u_Mercator_forcing_files/global-reanalysis-phy-001-030-daily_1993_2024_V4"
file_index = 0

chunk_output_particle = int(1e6)
#chunk_output_particle = int(1e6)
#chunk_output_time = 1
chunk_output_time = 10

particle_lifetime_days = 180
run_dt_minutes = 60 # They suggest shortening this, especially when using the offshore kick
max_depth_meters = 20
#output_dt_hours = 1
output_dt_hours = 24
repeatdt_days = 2

chunksize_horizontal_int = 768 # This performed best in tests, though all manual settings were close.  "auto" was worse, and "False" was much worse.  "auto" is apparently best for "3D" runs

t_init = time.time()

print(f"Start time: {time.ctime()}")


model_files = sorted(glob(f'{dataset_folder}/*.nc'))
#model_files_all = sorted(glob(f'{dataset_folder}/*.nc'))

num_files = len(model_files)

# Keep a maximum of 2 files

if file_index + 1 == num_files:
    model_files = model_files[file_index:]
else:
    model_files = model_files[file_index:file_index + 2]

model_sample_file = model_files[0]


#AgeParticle = parcels.JITParticle.add_variable(parcels.Variable("age", initial=0))

UCSCParticle = parcels.JITParticle.add_variables(
    [
    parcels.Variable("age", initial=0),
    parcels.Variable("bottomDepth", initial=0),
    ]
)

# --------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------



chunksize = {"time": ("time", 1), "lat": ("latitude", chunksize_horizontal_int), "lon": ("longitude", chunksize_horizontal_int)}


#output_dir_stem = f"z_output__chunkOutputParticleDim_{chunk_output_particle}"
output_dir_stem = "z_output"
output_dir = os.path.join(os.getcwd(), output_dir_stem)
os.makedirs(output_dir, exist_ok = True)


year_0 = datetime(int(Path(model_files[0]).stem), 1, 1)
year_1 = datetime(int(Path(model_files[0]).stem) + 1, 1, 1)

year_delta = year_1 - year_0

seed_period_total_days = int(year_delta.total_seconds()/86400)

if file_index + 1 == num_files:
    seed_period_total_days -= (particle_lifetime_days + 1) #Need to subtract one extra, bc math


output_file_name = os.path.join(output_dir,output_file_name_stem)

with Dataset(model_sample_file, 'r') as dset:
    model_depth_level_vector = np.array(dset["depth"][:])
    #time_units = dset["time"].units

static_file = "/data04/cedwards/forcing/mercator/reanalysis12/cmems_mod_glo_phy_my_0.083deg_static_depths.nc"

with Dataset(static_file, 'r') as dset:
    h = np.array(dset['deptho'][:])  # h will have different name in different models
    #landmask = np.array(dset["mask"][:])


seed_depths_general = model_depth_level_vector[model_depth_level_vector < max_depth_meters]
num_floats_per_column_max = len(seed_depths_general)


bad_lon_list = [np.float32(-120.25), np.float32(-120.333336), np.float32(-120.333336), np.float32(-120.5), np.float32(-120.25), np.float32(-120.583336), np.float32(-120.5), np.float32(-120.42646), np.float32(-120.64089), np.float32(-120.5), np.float32(-120.5), np.float32(-120.44381), np.float32(-120.5), np.float32(-120.5), np.float32(-120.416664)]

bad_lat_list = [np.float32(33.833332), np.float32(34.416668), np.float32(34.416668), np.float32(34.5), np.float32(34.083332), np.float32(34.5), np.float32(34.416668), np.float32(34.024353), np.float32(34.5196), np.float32(34.5), np.float32(34.5), np.float32(34.038773), np.float32(34.5), np.float32(34.5), np.float32(34.416668)]


bad_time_list = [np.datetime64('1993-01-17T12:00:00.000000000'), np.datetime64('1993-12-27T12:00:00.000000000'), np.datetime64('1993-09-16T12:00:00.000000000'), np.datetime64('1993-09-08T12:00:00.000000000'), np.datetime64('1993-08-07T12:00:00.000000000'), np.datetime64('1993-12-01T12:00:00.000000000'), np.datetime64('1993-05-15T12:00:00.000000000'), np.datetime64('1993-07-12T12:00:00.000000000'), np.datetime64('1993-05-19T12:00:00.000000000'), np.datetime64('1993-08-19T12:00:00.000000000'), np.datetime64('1993-09-08T12:00:00.000000000'), np.datetime64('1993-07-12T12:00:00.000000000'), np.datetime64('1993-10-28T12:00:00.000000000'), np.datetime64('1993-08-23T12:00:00.000000000'), np.datetime64('1993-01-15T12:00:00.000000000')]


zs = []
lons = []
lats = []
times = []

for seed_depth in seed_depths_general:
    zs.append(seed_depth)
    lons.append(bad_lon_list[0])
    lats.append(bad_lat_list[0])
    times.append(bad_time_list[0])




num_seeds_single_time = len(lons) # 8998
num_timesteps_single_particle_max = int((particle_lifetime_days * 24)/output_dt_hours)   # 180

variables = {
    "U": "u_all",
    "V": "v_all",
    "H": "deptho",
    "landmask": "mask",
}

filenames = {
    "U": model_files,
    "V": model_files,
    "H": static_file,
    "landmask": static_file,
}

dimensions = {
    "U": {"lon":"lon_all", "lat":"lat_all", "depth":"depth", "time":"time"},
    "V": {"lon":"lon_all", "lat":"lat_all", "depth":"depth", "time":"time"},
    "H": {"lon":"longitude", "lat":"latitude"},
    "landmask": {"lon":"longitude", "lat":"latitude"},
}

fieldset = parcels.FieldSet.from_netcdf(filenames, variables, dimensions, chunksize=chunksize)

fieldset.landmask.interp_method = "nearest"

pset = parcels.ParticleSet(
    fieldset=fieldset, 
    pclass=UCSCParticle,
    lon=lons, 
    lat=lats, 
    depth=zs, 
    time=times
)

# Must add kernels dealing with "particle.state" at the END of the kernels list (see https://docs.oceanparcels.org/en/latest/examples/tutorial_kernelloop.html#Working-with-Status-Codes  last paragraph)

kernels = [parcels.AdvectionRK4, parcels_util.particleAgeLimit_180, parcels_util.TidalKick, parcels_util.DeleteOutOfBounds]
#kernels = [parcels.AdvectionRK4, parcels_util.CheckOutOfBounds, parcels_util.particleAgeLimit_180, parcels_util.TidalKick]

output_file = pset.ParticleFile(name=output_file_name, outputdt=timedelta(hours=output_dt_hours), chunks = (chunk_output_particle, chunk_output_time))


t_setup_end = time.time()


pset.execute(
    kernels, 
    dt=timedelta(minutes=run_dt_minutes),
#    runtime=timedelta(days=(particle_lifetime_days + runtime_buffer)),
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


