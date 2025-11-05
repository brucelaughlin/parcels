
# note: "time_dimension == 0" refers to pDrake tracking files.  For Opendrift files, we have "time_dimension == 1"

script_version = "production"


import pdb
import time
import datetime
import netCDF4
import pickle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as plt_path
from scipy.interpolate import interp1d
from geopy.distance import great_circle
import scipy.interpolate as spint
from os import listdir
from os.path import isfile, join
import sys
import argparse
from pathlib import Path
import os
import math
from geopy.distance import geodesic

start_script_time = time.time()

#---------------------------------------------------------------------
#---------------------------------------------------------------------
# PARAMETERS and CONSTANTS

parser = argparse.ArgumentParser()
parser.add_argument("--trackingfile", type=str)
parser.add_argument("--polygonfile", type=str)
parser.add_argument("--baseyear", type=str)
#parser.add_argument("pdrakefileswitch", type=int, nargs="?")
parser.add_argument("--pdrakefileswitch", type=int)
#parser.add_argument("--pdrakefileswitch", type=int, nargs="?")
args = parser.parse_args()

#tracking_file = "/data03/blaughli/tracking_output/Mercator_coastalCells_1993_2018_kickSTD_0p0___global-reanalysis-phy-001-030-daily_1993_2018/tracking_output_configFile_000_job_00.nc"
#pdrake_file_switch = 0
#polygon_file_path = "/home/blaughli/tracking_project_v2/misc/z_boxes/z_output/bounding_boxes_lonlat_Mercator_singleCoastalCells.txt"


tracking_file = args.trackingfile
polygon_file_path = args.polygonfile
base_year = int(args.baseyear)
pdrake_file_switch = bool(int(args.pdrakefileswitch))

tracking_dir = os.path.dirname(tracking_file)

polygon_string = Path(polygon_file_path).stem


# Opendrift swaps the particle and time dimensions relative to the tracking code that Patrick used
# For Opendrift files, the particle dimension is the first dimension (ie 0); for Patrick's files, the particle dimension is the second dimension (ie 1):
if pdrake_file_switch:
    particle_dimension = 1
    time_dimension = 0
else:
    particle_dimension = 0
    time_dimension = 1


base_datetime = datetime.datetime(base_year,1,1,0,0,0)

# Pete Raimondi's PLDs
pld_list = [[1,5],[5,10],[10,15],[15,30],[30,45],[45,60],[60,75],[75,90],[90,120],[120,150],[150,180]]

# This is for my clunky idea of first determining all polygons all floats enter
last_pld_day_global = pld_list[-1][1]

num_plds = len(pld_list)

base_path = '/home/blaughli/tracking_project_v2/'
grid_directory = 'grid_data/'
grid_file_in = 'wc15n_grd.nc'
grid_path_in = base_path + grid_directory + grid_file_in
dset = netCDF4.Dataset(grid_path_in, 'r')

lon_field = np.array(dset['lon_rho'])
lat_field = np.array(dset['lat_rho'])

dset.close

bounding_boxes_base = base_path + 'practice/bounding_boxes/create_boxes/'
bounding_boxes_continent_dir = bounding_boxes_base + 'continent/z_output/'
bounding_boxes_islands_dir = bounding_boxes_base + 'modify_islands/z_output/'


# I always do this - is it bad practice?
tracking_dir = tracking_dir + "/"

save_output_directory = tracking_dir + 'v_connHist_files_production'
    
Path(save_output_directory).mkdir(parents=True, exist_ok=True)

#---------------------------------------------------------------------
#---------------------------------------------------------------------


#---------------------------------------------------------------------
# Use a text csv file of polygon vertices to create the boxes
# These files must have a consistent format for their lines:
#   cell #, vertex #, lat, lon
#   001, 01, 30.050000, -115.816661
# Cell numbers in the file must always start at 1!!!!!

cell_number = 0
polygon_vertex_list = []
with open(polygon_file_path) as polygon_file:
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
#---------------------------------------------------------------------

print('num polygons: {}'.format(num_polygons))


extrema_lon = [np.min(lon_field),np.max(lon_field)]
extrema_lat = [np.min(lat_field),np.max(lat_field)]


#---------------------------------------------------------------------

# number of prePdfs per feild (4 seasonal and 1 annual = 5)
num_prePdfs = 5

# Store the index of the annual prePdf used in the connectivity array (original idea is seasons are indices 0-3, and annual is index 4)
annual_prePdf_index = num_prePdfs - 1


# ----------------------------------------------------------loading
dset = netCDF4.Dataset(tracking_file, 'r')

lon_all = dset.variables['lon'][:]
lat_all = dset.variables['lat'][:]

#if time_dimension == 0:
if pdrake_file_switch:
    ocean_time = dset.variables['ocean_time'][:]
    status_all = np.zeros_like(lon_all.T)
else:
    ocean_time = dset.variables['time'][:]
    status_all = dset.variables['status'][:]


dset.close()
# ----------------------------------------------------------loading


num_particles = np.shape(lon_all)[particle_dimension]


print('NUMBER OF PARTICLES: {}'.format(num_particles))


timesteps_per_day = int(1/((ocean_time[1]-ocean_time[0])/86400))

# WTF WAS THIS??????
#timesteps_full_run = len(ocean_time) * timesteps_per_day
timesteps_full_run = len(ocean_time)

# Here again assuming we'll never handle timesteps bigger than 1 day (see the "1" below)
timestep_length = 1/timesteps_per_day

# For now, exit if output is less than daily...
if timesteps_per_day < 1:
    raise RuntimeError('This code is dumb and currently breaks if the save timestep is > 1 day.  Should be an easy fix')



## NEW ALGORITHM
pld_list_timesteps = pld_list.copy()
for pld_dex in range(len(pld_list)):
    for day_dex in range(2):
        pld_list_timesteps[pld_dex][day_dex] *= timesteps_per_day



#---------------------------------------------------------------------
# Create arrays to store statistics for full run and seasonal subsets
#---------------------------------------------------------------------

# store the number of particles released from each box
release_counts_per_polygon_array = np.zeros((num_prePdfs,num_polygons), dtype=int)

# Connectivity (release box number vs settlement box number)
prePdf_arrays_connectivity = np.zeros((num_prePdfs,num_plds,num_polygons,num_polygons))
prePdf_arrays_connectivity_noStagnation = np.zeros((num_prePdfs,num_plds,num_polygons,num_polygons))

particle_distances_per_pld_settlers = np.zeros((num_particles,num_plds))
particle_distances_per_pld_settlers_noStagnation = np.zeros((num_particles,num_plds))
particle_distances_per_pld_allTimesteps = np.zeros((num_particles,num_plds))

polygons_settled_per_particle = np.zeros((num_particles,num_plds))
stagnant_settlers_per_particle_per_pld = np.zeros((num_particles,num_plds))

particle_settle_times_per_pld = np.zeros((num_particles,num_plds))
particle_settle_times_per_pld_noStagnation = np.zeros((num_particles,num_plds))


stationary_settlers_array = np.zeros((num_polygons,1))

empty_trajectory_count_array = np.zeros(1)


# Store the total number of particles
num_particles = np.shape(lon_all)[particle_dimension]
num_timesteps = np.shape(lon_all)[time_dimension]

# SEASONS - Prepare the list of possible seed months for the run.  
# Update: Subtract 1 from the output of datetime, so that January is month 0, etc.
run_seed_months_list = []
for t in ocean_time:
    run_seed_months_list.append(int(datetime.datetime.strptime(str(base_datetime+datetime.timedelta(seconds=t)), '%Y-%m-%d %H:%M:%S').month - 1))
    #run_seed_months_list.append(datetime.datetime.strptime(str(base_datetime+datetime.timedelta(seconds=t)), '%Y-%m-%d %H:%M:%S').month)

seed_months_per_particle_array = np.ones(num_particles) * -1

# Why not just make one array of all of the data, and then reference it by time index???
#if time_dimension == 0:
#    particles_lon_all=np.full((timesteps_full_run,num_particles), np.nan)
#    particles_lat_all=np.full((timesteps_full_run,num_particles), np.nan)
#else: 
particles_lon_all=np.full((num_particles,timesteps_full_run), np.nan)
particles_lat_all=np.full((num_particles,timesteps_full_run), np.nan)

num_invalid_status = 0


for particle_num in range(num_particles):

    # Need trajectory status (active vs inactive) for determining month of release of particles
    trajectory_status = status_all[particle_num,:]

    # NOTE: Had cases where a particle had inactive status (1) for its whole life... not sure why, but I had clearly assumed this wouldn't
    # happen (it seems sketchy now to be using a list, appending a value for each particle.  why not just start with a fixed array, and
    # for problematic particles, leave their value as the default, ie nan?

    if np.shape(np.where(trajectory_status == 0))[1] == 0:
        num_invalid_status += 1
        continue
    seed_months_per_particle_array[particle_num] = run_seed_months_list[np.where(trajectory_status == 0)[0][0]]

    #if time_dimension == 0:
    if pdrake_file_switch:
        particle_lon = lon_all[:,particle_num]
        particle_lon = particle_lon[np.logical_not(particle_lon.mask)].data
        # ADDING A STEP WHICH IS NECESSARY WHEN THERE IS NO MASKED DATA (CALLING FOR THE DATA ABOVE ADDS A DIMENSION, WHICH MESSES UP INDEXING)
        if np.shape(np.shape(particle_lon))[0] == 2:
            particle_lon = particle_lon[0,:]
        particle_lat = lat_all[:,particle_num]
        particle_lat = particle_lat[np.logical_not(particle_lat.mask)].data
        if np.shape(np.shape(particle_lat))[0] == 2:
            particle_lat = particle_lat[0,:]
    else:
        particle_lon = lon_all[particle_num,:]
        particle_lon = particle_lon[np.logical_not(particle_lon.mask)].data
        if np.shape(np.shape(particle_lon))[0] == 2:
            particle_lon = particle_lon[0,:]
        particle_lat = lat_all[particle_num,:]
        particle_lat = particle_lat[np.logical_not(particle_lat.mask)].data
        if np.shape(np.shape(particle_lat))[0] == 2:
            particle_lat = particle_lat[0,:]
    
    
#    if time_dimension == 0:
#        particles_lon_all[0:len(particle_lon),particle_num] = particle_lon
#        particles_lat_all[0:len(particle_lat),particle_num] = particle_lat
#    else:
    particles_lon_all[particle_num,0:len(particle_lon)] = particle_lon
    particles_lat_all[particle_num,0:len(particle_lat)] = particle_lat


# We need to track a particle's current polygon location at all times, to remove particles which never leave their seeding polygon
# New idea: just have a single boolean vector of length <num_particles> which starts as true (ie assumes particle has not left seed polygon),
# and switches to false when the particle leaves the seed polygon, and never changes value again.  So, we start by assuming they're all stagnant
stagnant_particle_boolean_vector = np.ones(num_particles, dtype=bool)

# prepare lists to hold the starting/ending polygon numbers for each particle
release_polygons_per_particle = np.zeros(num_particles, dtype=int)

settlement_polygons = np.zeros((num_particles,num_plds), dtype=int)
settlement_polygons_noStagnation = np.zeros((num_particles,num_plds), dtype=int)
settlement_times = np.zeros((num_particles,num_plds), dtype=int)
settlement_times_noStagnation = np.zeros((num_particles,num_plds), dtype=int)


#---------------------------------------------------------------------
# FIRST MUST DETERMINE STARTING LOCATIONS
#---------------------------------------------------------------------
unsettled_particle_mask = np.ones(num_particles, dtype=bool)

# <points_lon_lat> is used here and in settlement; for starting locations, its value is fixed

points_lon_lat = np.zeros((num_particles,2))
#if time_dimension == 0:
#    points_lon_lat[:,0] = particles_lon_all[0,:]
#    points_lon_lat[:,1] = particles_lat_all[0,:]
#else:
points_lon_lat[:,0] = particles_lon_all[:,0]
points_lon_lat[:,1] = particles_lat_all[:,0]

# Actually, beyond the counts of releases per polygon for use in making pdfs later, I now also want a vector with the starting polygon (with my +1 convention,
# so the first is number 1 (not 0)) for each particle.  I'll try to use this for determining when particles stop being stagnant
particle_seed_polygon_vector = np.zeros(np.shape(points_lon_lat)[0])


for polygon_dex in range(num_polygons):
    path = plt_path.Path(polygon_vertex_list[polygon_dex])
    particles_inside_flags = path.contains_points(points_lon_lat)

    particle_seed_polygon_vector[particles_inside_flags] = polygon_dex + 1

    release_polygons_per_particle[np.logical_and(particles_inside_flags,unsettled_particle_mask)] = polygon_dex + 1
    unsettled_particle_mask[particles_inside_flags] = False


# Need a mask to prevent processing of particles with no release location (I have no idea how that happens, by the way..???!)
empty_release_cells = np.setdiff1d(np.arange(num_polygons)+1,release_polygons_per_particle)

print("--------------------------------------------")
print(f"{len(empty_release_cells)} Empty release cells:")
for ii in range(len(empty_release_cells)):
    print(f"cell {empty_release_cells[ii]}")
print("--------------------------------------------")



#---------------------------------------------------------------------
# NOW DETERMINE SETTLEMENT LOCATIONS!
# NOTE: Release locations could probably be easily calculated as part of the main loop (ie timestep 0), but for now I don't
# want to mess anything up so I'm leaving that as a separate calculation above. 
#---------------------------------------------------------------------

points_lon_lat = np.zeros((num_particles,2))
points_lon_lat_previous = np.zeros((num_particles,2))

# We're now gonna determine the pld dex dynamically, as we loop over ALL output timesteps
pld_dex = 0
first_time_dex = 0
currently_within_pld_switch = False
first_timestep_of_run_switch = True

# Create the "safety mask" that I'll use to make sure I only store the first polygon entered during the settlement window
# (not used if current timestep is not within a pld)
unsettled_particle_mask = np.ones(num_particles, dtype=bool)

for time_dex in range(first_time_dex,pld_list_timesteps[-1][-1]):

    print('timestep {}/{}'.format(time_dex,pld_list_timesteps[-1][-1] - 1))

    last_timestep_of_pld_switch = False
    
    if time_dex >= pld_list_timesteps[pld_dex][0] and time_dex < pld_list_timesteps[pld_dex][1]:
        currently_within_pld_switch = True
        # Need switch for indicating last timestep of pld, for storing connectivity
        if time_dex == pld_list_timesteps[pld_dex][1] - 1:
            last_timestep_of_pld_switch = True

    elif time_dex >= pld_list_timesteps[pld_dex][1]:
        unsettled_particle_mask = np.ones(num_particles, dtype=bool) 
        pld_dex += 1
        if pld_dex == num_plds:
            break
        elif time_dex >= pld_list_timesteps[pld_dex][0]:
            currently_within_pld_switch = True
        else:
            currently_within_pld_switch = False

    
    active_current_polygon_occupation = np.zeros(num_particles)


    if time_dex > first_time_dex:
        points_lon_lat_previous = points_lon_lat.copy()

#    if time_dimension == 0:
#        points_lon_lat[:,0] = particles_lon_all[time_dex,:]
#        points_lon_lat[:,1] = particles_lat_all[time_dex,:]
#    else:
    points_lon_lat[:,0] = particles_lon_all[:,time_dex]
    points_lon_lat[:,1] = particles_lat_all[:,time_dex]

    start_1 = time.time()

    # must reverse coordinates, since lat/lon is standard but I've been using lon/lat
    if time_dex > first_time_dex:
        for particle_dex in range(num_particles):

            if unsettled_particle_mask[particle_dex]:

                point1 = list(points_lon_lat_previous[particle_dex])
                point1.reverse()
                point2 = list(points_lon_lat[particle_dex])
                point2.reverse()
               
                if np.sum(np.isnan(point1)) > 0 or np.sum(np.isnan(point2)) > 0:
                    continue

                distance = geodesic(point1, point2).km  # Returns distance in kilometers
                particle_distances_per_pld_allTimesteps[particle_dex,pld_dex:] += distance

    
    for polygon_dex in range(num_polygons):

        path = plt_path.Path(polygon_vertex_list[polygon_dex])
        
        particles_inside_flags = path.contains_points(points_lon_lat)
  
        stagnant_particle_boolean_vector[particles_inside_flags] = np.logical_and(particle_seed_polygon_vector[particles_inside_flags] == polygon_dex + 1, stagnant_particle_boolean_vector[particles_inside_flags])

        active_current_polygon_occupation_indices = np.logical_and(particles_inside_flags, unsettled_particle_mask)  
        active_current_polygon_occupation_indices_noStagnation = np.logical_and(active_current_polygon_occupation_indices, np.logical_not(stagnant_particle_boolean_vector))  

        active_current_polygon_occupation[active_current_polygon_occupation_indices] = polygon_dex + 1

        if currently_within_pld_switch:

            particle_distances_per_pld_settlers[active_current_polygon_occupation_indices,pld_dex] = particle_distances_per_pld_allTimesteps[active_current_polygon_occupation_indices,pld_dex]
            particle_distances_per_pld_settlers_noStagnation[active_current_polygon_occupation_indices_noStagnation,pld_dex] = (
                    particle_distances_per_pld_allTimesteps[active_current_polygon_occupation_indices_noStagnation,pld_dex])
            
            polygons_settled_per_particle[active_current_polygon_occupation_indices,pld_dex] = polygon_dex + 1

            stagnant_settlers_per_particle_per_pld[active_current_polygon_occupation_indices,pld_dex] += stagnant_particle_boolean_vector[active_current_polygon_occupation_indices].astype(int)

            particle_settle_times_per_pld[active_current_polygon_occupation_indices, pld_dex] = time_dex * timestep_length 
            particle_settle_times_per_pld_noStagnation[active_current_polygon_occupation_indices_noStagnation, pld_dex] = time_dex * timestep_length 

            settlement_polygons[active_current_polygon_occupation_indices,pld_dex] = polygon_dex + 1
            settlement_polygons_noStagnation[active_current_polygon_occupation_indices_noStagnation,pld_dex] = polygon_dex + 1
            
            # Update the safety mask, so that settlement prevents further modifications to the stored settlement location
            unsettled_particle_mask[particles_inside_flags] = False

    end_1 = time.time()
    

# DEBUG
#print(f"Debug: Max season for a particle: {np.max(seed_months_per_particle_array)}")
print(f"Number of completely inactive particles: {np.sum(seed_months_per_particle_array == -1)}/{num_particles}")
    

firstPldSwitch = True
for pld_dex in range(num_plds):

    # modify the prePdf data structure
    for particle_num in range(num_particles):
    
        # --------------------------------------------------
        # Error handling
        # --------------------------------------------------
        # --------------------------------------------------
        # Added this, after seeing that I was getting "-1" values in <seed_months_per_particle_array[particle_num]>, meaning this condition was met above and the particle was inactive for its whole life and not processed
        if np.shape(np.where(trajectory_status == 0))[1] == 0:
            num_invalid_status += 1
            continue

        # --------------------------------------------------
        if release_polygons_per_particle[particle_num] < 0:
            raise RuntimeError('particle {} has release cell dex: {}'.format(particle_num,release_polygons_per_particle[particle_num]))
        # --------------------------------------------------
        # --------------------------------------------------
        # --------------------------------------------------



        # -------------------------------------------------------------------------------------
        # Seasons
        # We always add to the "annual" array; and we also add to the seasonal array
        # -------------------------------------------------------------------------------------
        if seed_months_per_particle_array[particle_num] == 11 or (seed_months_per_particle_array[particle_num] >=0 and seed_months_per_particle_array[particle_num] <2):
            season_dex = 0 #DJF
        elif seed_months_per_particle_array[particle_num] >=2 and seed_months_per_particle_array[particle_num] <5:
            season_dex = 1 #MAM
        elif seed_months_per_particle_array[particle_num] >=5 and seed_months_per_particle_array[particle_num] <8:
            season_dex = 2 #JJA
        elif seed_months_per_particle_array[particle_num] >=8 and seed_months_per_particle_array[particle_num] <11:
            season_dex = 3 #SON

        # DEBUG
        #else:
        #    print(f"Error: For particle {particle_num}, seed_months_per_particle_array[particle_num] = {seed_months_per_particle_array[particle_num]}")


#        if seed_months_per_particle_array[particle_num] >=0 and seed_months_per_particle_array[particle_num] <=2 :
#            season_dex = 0 #DJF
#        elif seed_months_per_particle_array[particle_num] >=3 and seed_months_per_particle_array[particle_num] <=5 :
#            season_dex = 1 #MAM
#        elif seed_months_per_particle_array[particle_num] >=6 and seed_months_per_particle_array[particle_num] <=8 :
#            season_dex = 2 #JJA
#        elif seed_months_per_particle_array[particle_num] >=9 and seed_months_per_particle_array[particle_num] <=11 :
#            season_dex = 3 #SON

        array_dex_list = [season_dex,annual_prePdf_index]
        # -------------------------------------------------------------------------------------

        # wait we have 0's in here, so my logic requires we skip in this case
        if release_polygons_per_particle[particle_num] == 0:
            continue
        else:
            for array_dex in array_dex_list:
                if firstPldSwitch:
                    release_counts_per_polygon_array[array_dex,int(release_polygons_per_particle[particle_num])-1] += 1
                if settlement_polygons[particle_num,pld_dex] > 0:
                    prePdf_arrays_connectivity[array_dex,pld_dex,int(release_polygons_per_particle[particle_num])-1,int(settlement_polygons[particle_num,pld_dex])-1] += 1   
                if settlement_polygons_noStagnation[particle_num,pld_dex] > 0:
                    prePdf_arrays_connectivity_noStagnation[array_dex,pld_dex,int(release_polygons_per_particle[particle_num])-1,int(settlement_polygons[particle_num,pld_dex])-1] += 1   
                
                
    firstPldSwitch = False


d = {}
d['particle_distances_per_pld_settlers'] = particle_distances_per_pld_settlers
d['particle_distances_per_pld_settlers_noStagnation'] = particle_distances_per_pld_settlers_noStagnation
d['particle_distances_per_pld_allTimesteps'] = particle_distances_per_pld_allTimesteps
d['particle_release_polygons_per_particle'] = release_polygons_per_particle
d['polygons_settled_per_particle'] = polygons_settled_per_particle


d["stagnant_settlers_per_particle_per_pld"] = stagnant_settlers_per_particle_per_pld
d["particle_settle_times_per_pld"] = particle_settle_times_per_pld
d["particle_settle_times_per_pld_noStagnation"] = particle_settle_times_per_pld_noStagnation


d['release_counts_per_polygon_array'] = release_counts_per_polygon_array
d['prePdf_arrays_connectivity'] = prePdf_arrays_connectivity
d['prePdf_arrays_connectivity_noStagnation'] = prePdf_arrays_connectivity_noStagnation

d['pld_list'] = pld_list
d['pld_list_timesteps'] = pld_list_timesteps

save_output_file_name_pre = "conn_hist_data_"
save_output_file_name = save_output_file_name_pre + tracking_file.split('.')[0].split('/')[-1]
save_output_full_path = os.path.join(save_output_directory, save_output_file_name + f"_version_{script_version}_{polygon_string}")
#save_output_full_path = os.path.join(save_output_directory, save_output_file_name + f"_allPLDs_version_{script_version}_{polygon_string}")


np.savez(save_output_full_path, **d)

print("Finished!")

#sample_start = 1000
#sample_end = 1010

#print("polygons_settled_per_particle")
#print(polygons_settled_per_particle[sample_start:sample_end,:])
#print("particle_settle_times_per_pld")
#print(particle_settle_times_per_pld[sample_start:sample_end,:])
#print("stagnant_settlers_per_particle_per_pld")
#print(stagnant_settlers_per_particle_per_pld[sample_start:sample_end,:])
#print("particle_distances_per_pld_settlers")
#print(particle_distances_per_pld_settlers[sample_start:sample_end,:].astype(int))
###print("polygons_settled_per_particle")
##print(polygons_settled_per_particle[sample_start:sample_end,:])




