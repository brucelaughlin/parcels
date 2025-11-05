import os
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import netCDF4
import argparse
from pathlib import Path

from parcels_analysis_util import get_timesteps_per_day

artificial_boundary_lon_min = -133.5
artificial_boundary_lat_min = 30.05
#artificial_boundary_lat_max = 47.95 # I used 47.95 in my test kernels, but I think 47.9 is also fine.  Need to settle on something
artificial_boundary_lat_max = 47.9


#if trajectories_to_plot_lats[i_traj][-1] > 47.95 or trajectories_to_plot_lats[i_traj][-1]  < 30.05 or trajectories_to_plot_lons[i_traj][-1] < -133.5:





# ------------------------------------------------------------------------------------------------
#save_dir = f"{os.getcwd()}/z_figures_trajectoriesByLifetime" 
#os.makedirs(save_dir, exist_ok = True)

#lifetime_buffer = 5
# ------------------------------------------------------------------------------------------------


parser = argparse.ArgumentParser()
parser.add_argument("trackingfile", type=str)
#parser.add_argument("lifetimedays", type=float)
#parser.add_argument("lifetimedaysbuffer", type=float)
parser.add_argument("lifetimedays", type=int)
parser.add_argument("lifetimedaysbuffer", type=int)
args = parser.parse_args()

tracking_file = args.trackingfile
lifetime_days = args.lifetimedays
lifetime_days_buffer = args.lifetimedaysbuffer

with xr.open_zarr(tracking_file) as ds:
    lons = ds.lon.values
    lats = ds.lat.values
    ages = ds.age.values
    times = ds.time.values
    zs = ds.z.values

grid_file = "/home/blaughli/tracking_project_v2/grid_data/wcr30test1_grd.nc"
with netCDF4.Dataset(grid_file,"r") as d:
    lat_rho = d[f"lat_rho"][:].data
    lon_rho = d[f"lon_rho"][:].data
    mask_rho = d[f"mask_rho"][:].data
#    h = d[f"h"][:].data

num_particles = lons.shape[0]

days_per_timestepOut = get_timesteps_per_day(times,ages)

lifetime_timesteps = lifetime_days / days_per_timestepOut
lifetime_timesteps_buffer = lifetime_days_buffer / days_per_timestepOut

lifetime_timesteps_min = max(0,lifetime_timesteps - lifetime_timesteps_buffer)
if lifetime_days_buffer == 0:
    lifetime_timesteps_max = lifetime_timesteps + 1
    #lifetime_timesteps_max = lifetime_timesteps + 1/days_per_timestepOut
else:
    lifetime_timesteps_max = lifetime_timesteps + lifetime_timesteps_buffer

lifetime_days_min = lifetime_timesteps_min * days_per_timestepOut
lifetime_days_max = lifetime_timesteps_max * days_per_timestepOut


trajectories_to_plot_lons = []
trajectories_to_plot_lats = []


for i_particle in range(num_particles):
    last_living_timestep = int(np.sum(np.logical_not(np.isnan(ages[i_particle])))) - 1 # this assumes that particles never get reactivated/"un-nanned" after being deactivated/"nanned"
    if ages[i_particle][last_living_timestep] >= lifetime_timesteps_min and ages[i_particle][last_living_timestep] < lifetime_timesteps_max:
    #if np.max(ages[i_particle][np.logical_not(np.isnan(ages[i_particle]))]) >= lifetime_timesteps_min and np.max(ages[i_particle][np.logical_not(np.isnan(ages[i_particle]))]) < lifetime_timesteps_max:
    
    #if np.max(ages[i_particle]) >= lifetime_timesteps_min and np.max(ages[i_particle]) < lifetime_timesteps_max:
    ###if len(np.unique(ages[i_particle])) >= lifetime_timesteps_min and len(np.unique(ages[i_particle])) < lifetime_timesteps_max:
        
        trajectories_to_plot_lons.append(lons[i_particle][:last_living_timestep])
        trajectories_to_plot_lats.append(lats[i_particle][:last_living_timestep])
        
        #trajectories_to_plot_lons.append(lons[i_particle])
        #trajectories_to_plot_lats.append(lats[i_particle])

num_trajectories_plot = len(trajectories_to_plot_lons)

oob_indices = np.zeros(num_trajectories_plot)
for i_traj in range(num_trajectories_plot):
    if trajectories_to_plot_lats[i_traj][-1] > artificial_boundary_lat_max or trajectories_to_plot_lats[i_traj][-1]  < artificial_boundary_lat_min or trajectories_to_plot_lons[i_traj][-1] < artificial_boundary_lon_min:
    #if trajectories_to_plot_lats[i_traj][-1] > 47.95 or trajectories_to_plot_lats[i_traj][-1]  < 30.05 or trajectories_to_plot_lons[i_traj][-1] < -133.5:
        oob_indices[i_traj] = 1

oob_count = int(np.sum(oob_indices))

fig,ax = plt.subplots()
if lifetime_days_buffer == 0:
    ax.set_title(f"Age: {lifetime_days_min} days\nnumber of particles shown: {num_trajectories_plot}/{num_particles}\nnumber leaving domain horizontally: {oob_count}/{num_trajectories_plot}")
else:
    ax.set_title(f"Ages in range {lifetime_days_min} - {lifetime_days_max} days\nnumber of particles shown: {num_trajectories_plot}/{num_particles}\nnumber leaving domain horizontally: {oob_count}/{num_trajectories_plot}")
ax.pcolormesh(lon_rho,lat_rho,mask_rho)

for i_particle in range(num_trajectories_plot):
    ax.plot(trajectories_to_plot_lons[i_particle],trajectories_to_plot_lats[i_particle])

    ax.scatter(trajectories_to_plot_lons[i_particle][0], trajectories_to_plot_lats[i_particle][0], c='k', marker='D', s=50, zorder=10)
    if oob_indices[i_particle]:
        ax.scatter(trajectories_to_plot_lons[i_particle][-1], trajectories_to_plot_lats[i_particle][-1], c='k', s=50, zorder=10)
    else:
        ax.scatter(trajectories_to_plot_lons[i_particle][-1], trajectories_to_plot_lats[i_particle][-1], c='r', s=500, zorder=10)
    
    #ax.scatter(trajectories_to_plot_lons[i_particle][np.logical_not(np.isnan(trajectories_to_plot_lons[i_particle]))][0], trajectories_to_plot_lats[i_particle][np.logical_not(np.isnan(trajectories_to_plot_lats[i_particle]))][0], c='c', s=50)
    #ax.scatter(trajectories_to_plot_lons[i_particle][np.logical_not(np.isnan(trajectories_to_plot_lons[i_particle]))][-1], trajectories_to_plot_lats[i_particle][np.logical_not(np.isnan(trajectories_to_plot_lats[i_particle]))][-1], c='r', s=50)
    


plt.show()

#plt.savefig(f"{save_dir}/figure_{i_frame:02d}")
#plt.close(fig)





