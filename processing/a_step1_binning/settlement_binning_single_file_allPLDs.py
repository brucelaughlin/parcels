# note: REMOVING distance calculation; see Parcels docs for example kernel to calculate that and store it as a variable

import netCDF4
import xarray as xr
import pdb
import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as plt_path
from os import listdir
from os.path import isfile, join
import argparse
from pathlib import Path
import os
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


import parcels_analysis_util as parcels_analysis_util

start_script_time = time.time()

# This should never change

parser = argparse.ArgumentParser()
parser.add_argument('--configfile', type=str)
parser.add_argument("--trackingfile", type=str)
args = parser.parse_args()
config_file = args.configfile
tracking_file = args.trackingfile

with open(config_file,'r') as stream:
    config_dict = yaml.safe_load(stream)

grid_file = config_dict['gridFile']
polygon_file = config_dict['polygonFile']
connectivity_common_grandparent_dir = config_dict['connectivityCommonGrandparentDir']
version_detail = config_dict['versionDetail']
connectivity_local_dir_preamble = config_dict['connectivityLocalDirPreamble']
border_buffer = config_dict['DomainGridCellBorderBuffer']
pld_start_days = config_dict['pldStartDays']
pld_end_days = config_dict['pldEndDays']
tracking_file_num_timesteps_expected = config_dict['trackingFileNumTimestepsExpected']

polygon_metadata = Path(polygon_file).stem
config_file_name = Path(config_file).stem
version_string = f"polygons_{polygon_metadata}__version_{version_detail}__config_{config_file_name}"

connectivity_parent_dir_local_name = f"{connectivity_local_dir_preamble}{version_string}"

#cwd = os.getcwd()
#parent_dir = os.path.join(str(cwd), common_grandparent_dir, settlement_count_parent_dir_local_name)

input_date_data_pre1 = tracking_file.split("/")[-2]
input_date_data_pre2 = input_date_data_pre1.split("_")[-1]

input_year_str = input_date_data_pre2[:4]
input_month_str = input_date_data_pre2[4:6]
input_day_str = input_date_data_pre2[6:]

sub_dir_year = f"bd_year_{input_year_str}"
sub_dir_month = f"bd_month_{input_month_str}"
sub_dir_day = f"bd_day_{input_day_str}"

#output_dir = os.path.join(parent_dir,sub_dir_year,sub_dir_month,sub_dir_day)
output_dir = os.path.join(connectivity_common_grandparent_dir,connectivity_parent_dir_local_name,sub_dir_year,sub_dir_month,sub_dir_day)
Path(output_dir).mkdir(parents=True, exist_ok=True)




# ----------------------------------------------------------------------------------------------------
# Create the domain boundary polygon
# ----------------------------------------------------------------------------------------------------
with netCDF4.Dataset(grid_file) as ds:
    lon_rho = ds["lon_rho"][:].data
    lat_rho = ds["lat_rho"][:].data

lons_boundary = []
lats_boundary = []

lons_boundary += list(lon_rho[border_buffer,border_buffer:-border_buffer])
lons_boundary += list(lon_rho[border_buffer:-border_buffer,-border_buffer-1])
lons_boundary += list(lon_rho[-border_buffer-1,border_buffer:-border_buffer][::-1])
lons_boundary += list(lon_rho[border_buffer:-border_buffer,border_buffer][::-1])

lats_boundary += list(lat_rho[border_buffer,border_buffer:-border_buffer])
lats_boundary += list(lat_rho[border_buffer:-border_buffer,-border_buffer-1])
lats_boundary += list(lat_rho[-border_buffer-1,border_buffer:-border_buffer][::-1])
lats_boundary += list(lat_rho[border_buffer:-border_buffer,border_buffer][::-1])

domain_boundary_vertices = np.array([lons_boundary,lats_boundary]).T
path_domain = plt_path.Path(domain_boundary_vertices)
# ----------------------------------------------------------------------------------------------------



#---------------------------------------------------------------------
# Use a text csv file of polygon vertices to create the polygones
# These files must have a consistent format for their lines:
#   cell #, vertex #, lat, lon
#   001, 01, 30.050000, -115.816661
# Cell numbers in the file must always start at 1!!!!!

cell_number = 0
polygon_vertex_list = []
with open(polygon_file) as polygon_file:
   for line in polygon_file:
        line_items = line.rstrip().split(',')
        if line_items[0].isdigit():
            if int(line_items[0]) != cell_number:
                if cell_number > 0:
                    polygon_vertex_list.append(current_polygon_vertices)
                cell_number += 1
                current_polygon_vertices = np.array([float(line_items[3]), float(line_items[2])])
                continue
            current_polygon_vertices = np.vstack([current_polygon_vertices, [float(line_items[3]), float(line_items[2])]]) # note that Patrick stores lat first, then lon, so I switch these
# Must append the last polygon
polygon_vertex_list.append(current_polygon_vertices)
num_polygons = len(polygon_vertex_list)

print('num polygons: {}'.format(num_polygons))
#---------------------------------------------------------------------


with xr.open_zarr(tracking_file) as ds:
    particles_lon_all = ds.lon.values
    particles_lat_all = ds.lat.values
    particles_age_all = ds.age.values
    particles_time_all = ds.time.values


# This is a vestige of when I was reproducing Patrick's work; his output had time as the first dimension
particle_dimension = 0
time_dimension = 1

num_particles = np.shape(particles_lon_all)[particle_dimension]
num_timesteps = np.shape(particles_lon_all)[time_dimension]
print('NUMBER OF PARTICLES: {}'.format(num_particles))

days_per_output_timestep = parcels_analysis_util.get_days_per_output_timestep(particles_time_all, particles_age_all)
seconds_per_timestep_out = 86400 * days_per_output_timestep





# ---------------------------------------------------------------------------------
# Release locations
# ---------------------------------------------------------------------------------
polygon_release_counts = np.zeros(num_polygons, dtype=int)
particle_release_polygons = np.zeros(num_particles, dtype=int)
unprocessed_particle_mask = np.ones(num_particles, dtype=bool)

points_lon_lat_timestep_zero = np.column_stack([particles_lon_all[:,0],particles_lat_all[:,0]])

# <unprocessed_particle_mask> should not be necessary here, but it can't hurt (it's copied logic from the settlement loop)
for polygon_dex in range(num_polygons):
    path = plt_path.Path(polygon_vertex_list[polygon_dex])
    polygon_inside_flags = path.contains_points(points_lon_lat_timestep_zero)
    
    path = plt_path.Path(domain_boundary_vertices)
    domain_inside_flags = path.contains_points(points_lon_lat_timestep_zero)
    
    #particle_release_polygons[np.logical_and(polygon_inside_flags,unprocessed_particle_mask)] = polygon_dex + 1
    particle_release_polygons[np.logical_and(domain_inside_flags, np.logical_and(polygon_inside_flags,unprocessed_particle_mask))] = polygon_dex + 1
    #unprocessed_particle_mask[polygon_inside_flags] = False
    unprocessed_particle_mask[np.logical_and(domain_inside_flags, polygon_inside_flags)] = False


# WHY ARE THERE ELEMENTS OF <particle_release_polygons> whose value is still 0???  They were not counted as being in any polygon??? Check to see if these are releases on land... hopefully that explains EVERYthing

# Diagnostic info - Typically we shouldn't have empty release cells, so if <empty_release_cells> is non-empty, look into this (why did some polygons have no particles recorded as being seeded in them?)
# This was, of course, a piece of Paul cleverness
empty_release_cells = np.setdiff1d(np.arange(num_polygons)+1,particle_release_polygons)
print("--------------------------------------------")
print(f"{len(empty_release_cells)} Empty release cells:")
for ii in range(len(empty_release_cells)):
    print(f"cell {empty_release_cells[ii]}")
print("--------------------------------------------")

# modify the prePdf data structure
for particle_num in range(num_particles):

    # If a particle isn't found to have a release location, my logic requires we skip it
    # (I store a particle's release/settlement polygon index with base-1 numbering, and then I increment the release/settlement polygon array indices with said index minus 1.  So, if a particle
    # has "0" as its release/settlement polygon number, that means it was never found to be in a polygon.  And subtracting 1 will produce an indexing error.  This was all done to avoid over-counting
    # the first/zeroth polygon statistics...

    if particle_release_polygons[particle_num] == 0:
        continue
    else:
        polygon_release_counts[int(particle_release_polygons[particle_num])-1] += 1
# ---------------------------------------------------------------------------------




# ---------------------------------------------------------------------------------
# Settlement locations
# ---------------------------------------------------------------------------------

particle_settlement_polygons = np.zeros(num_particles, dtype=int)
particle_settle_times = np.zeros(num_particles)
unsettled_particle_mask = np.ones(num_particles, dtype=bool)
outofbounds_particle_mask = np.ones(num_particles, dtype=bool)

pld_index = 0

pld_start_day_timestep = int(pld_start_days[pld_index] / days_per_output_timestep)
pld_end_day_timestep = int(pld_end_days[pld_index] / days_per_output_timestep)

finished_switch = False

print(f"NEW PLD: timesteps {pld_start_day_timestep:04d}:{pld_end_day_timestep:04d}")

# Now we process EVERY timestep from 0 through the end of the current PLD, in order to "kill" particles which come within <border_buffer> of the grid domain boundary
for time_dex in range(tracking_file_num_timesteps_expected):
#for time_dex in range(pld_end_day_timestep):

    print(f"Time index: {time_dex + 1}/{tracking_file_num_timesteps_expected}")

    points_lon_lat_current_timestep = np.column_stack([particles_lon_all[:,time_dex],particles_lat_all[:,time_dex]])
    domain_inside_flags = path_domain.contains_points(points_lon_lat_current_timestep)

    # "Delete" particles if they cross into the "buffer" region near the lateral boundaries
    #unsettled_particle_mask[np.logical_not(domain_inside_flags)] = False
    outofbounds_particle_mask[np.logical_not(domain_inside_flags)] = False

    #if time_dex >= pld_start_day_timestep:
    if time_dex >= pld_start_day_timestep and time_dex < pld_end_day_timestep:

        for polygon_dex in range(num_polygons):
            path = plt_path.Path(polygon_vertex_list[polygon_dex])
            polygon_inside_flags = path.contains_points(points_lon_lat_current_timestep)
            #unsettled_particles_in_current_polygon_mask = np.logical_and(polygon_inside_flags, unsettled_particle_mask)
            unsettled_particles_in_current_polygon_mask = np.logical_and(outofbounds_particle_mask, np.logical_and(polygon_inside_flags, unsettled_particle_mask))
            particle_settlement_polygons[unsettled_particles_in_current_polygon_mask] = polygon_dex + 1
            particle_settle_times[unsettled_particles_in_current_polygon_mask] = time_dex * seconds_per_timestep_out 
            unsettled_particle_mask[unsettled_particles_in_current_polygon_mask] = False
    
        
        if time_dex == pld_end_day_timestep - 1:

            polygon_settlement_counts = np.zeros((num_polygons,num_polygons))

            for particle_num in range(num_particles):
                if particle_release_polygons[particle_num] == 0 or particle_settlement_polygons[particle_num] == 0:
                    continue
                else:
                    polygon_settlement_counts[int(particle_release_polygons[particle_num])-1,int(particle_settlement_polygons[particle_num])-1] += 1   

            
            output_file_name = f"{input_year_str}{input_month_str}{input_day_str}_PLD_{pld_start_days[pld_index]:03d}_{pld_end_days[pld_index]:03d}"
            output_full_path = os.path.join(output_dir, output_file_name)

            d = {}
            d["particle_settle_times"] = particle_settle_times
            d['polygon_release_counts'] = polygon_release_counts
            d['polygon_settlement_counts'] = polygon_settlement_counts
            np.savez(output_full_path, **d)

            
            # ----------------------------------------------------------------------------------------
            # Reset the PLD arrays

            pld_index += 1
            
            if pld_index == len(pld_start_days):
                finished_switch = True
                break
            
            pld_start_day_timestep = int(pld_start_days[pld_index] / days_per_output_timestep)
            pld_end_day_timestep = int(pld_end_days[pld_index] / days_per_output_timestep)
            print(f"NEW PLD: timesteps {pld_start_day_timestep:04d}:{pld_end_day_timestep:04d}")

            particle_settlement_polygons = np.zeros(num_particles, dtype=int)
            particle_settle_times = np.zeros(num_particles)
            unsettled_particle_mask = np.ones(num_particles, dtype=bool)

    
    if finished_switch:
        break

print("Finished!")



