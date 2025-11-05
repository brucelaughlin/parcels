import os
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import netCDF4
import argparse
from pathlib import Path
import textwrap

from parcels_analysis_util import get_timesteps_per_day

# ------------------------------------------------------------------------------------------------
#save_dir = f"{os.getcwd()}/z_figures_trajectoriesByLifetime" 
#os.makedirs(save_dir, exist_ok = True)

#lifetime_buffer = 5

max_lifetime_days = 181 


artificial_boundary_lon_min = -133.5
artificial_boundary_lat_min = 30.05
#artificial_boundary_lat_max = 47.95 # I used 47.95 in my test kernels, but I think 47.9 is also fine.  Need to settle on something
artificial_boundary_lat_max = 47.9

# ------------------------------------------------------------------------------------------------


parser = argparse.ArgumentParser()
parser.add_argument("trackingfile", type=str)
args = parser.parse_args()

tracking_file = args.trackingfile

with xr.open_zarr(tracking_file) as ds:
    ages = ds.age.values
    times = ds.time.values
    lats = ds[f"lat"][:].data
    lons = ds[f"lon"][:].data

num_particles = ages.shape[0]

days_per_timestepOut = get_timesteps_per_day(times,ages)

lifetime_timesteps_per_day = np.arange(max_lifetime_days + 1, dtype=float)
lifetime_timesteps_per_day /= days_per_timestepOut

counts_per_lifetime_day = np.zeros(max_lifetime_days)

counts_per_lifetime_running_sum = np.sum(counts_per_lifetime_day)


for i_particle in range(num_particles):
    last_living_timestep = int(np.sum(np.logical_not(np.isnan(ages[i_particle])))) - 1
    
    for lifetime_day in range(max_lifetime_days):
    #for lifetime_day in range(max_lifetime_days + 1):
    
        if ages[i_particle][last_living_timestep] >= lifetime_timesteps_per_day[lifetime_day] and ages[i_particle][last_living_timestep] < lifetime_timesteps_per_day[lifetime_day + 1]:
        #if np.max(ages[i_particle][np.logical_not(np.isnan(ages[i_particle]))]) >= lifetime_timesteps_per_day[lifetime_day] and np.max(ages[i_particle][np.logical_not(np.isnan(ages[i_particle]))]) < lifetime_timesteps_per_day[lifetime_day + 1]:
            counts_per_lifetime_day[lifetime_day] += 1 
            if lats[i_particle][-1] > artificial_boundary_lat_max or lats[i_particle][-1]  < artificial_boundary_lat_min or lons[i_particle][-1] < artificial_boundary_lon_min:
                break

    if np.sum(counts_per_lifetime_day) == counts_per_lifetime_running_sum:
        print("Premature break due to no increment in count")
        break
    else:
        counts_per_lifetime_running_sum = np.sum(counts_per_lifetime_day)

x = list(range(len(counts_per_lifetime_day))) # hacky SO code

filename_print = textwrap.fill(f"{'/'.join(tracking_file.split('/')[-2:])}", width=70) # SO code... arbitrary width?

if counts_per_lifetime_running_sum == ages.shape[0]:
    plt.plot(counts_per_lifetime_day)
    #plt.title(f"{int(counts_per_lifetime_day[-1])}/{num_particles} ({100*counts_per_lifetime_day[-1]/num_particles:.0f}%) lived to intended age ({max_lifetime_days - 1} days)\n{'/'.join(tracking_file.split('/')[-2:])}")
    plt.title(f"{int(counts_per_lifetime_day[-1])}/{num_particles} ({100*counts_per_lifetime_day[-1]/num_particles:.0f}%) lived to intended age ({max_lifetime_days - 1} days)")
    #plt.text(len(x)/2, 0, filename_print, ha='center', fontsize=10)
    #plt.text(len(x)/2, 0, filename_print, ha='center', va='top', fontsize=10)
    plt.show()
else:
    print("Something's wrong in this script; not all particles were counted")



