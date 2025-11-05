import xarray as xr
import netCDF4
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator as RGI


model_timestep_check = int(np.random.uniform(0,364))


# Center coordinates of phantom corner cell of interest
lon_phantom = -120.5832
lat_phantom = 34.586


model_year = 1994

model_file_v4 = f"/data04/cedwards/forcing/mercator/reanalysis12/global-reanalysis-phy-001-030-daily_{model_year}_parcels_v4.nc"
model_file_OG = f"/data04/cedwards/forcing/mercator/reanalysis12/global-reanalysis-phy-001-030-daily_{model_year}.nc"

#model_file_v4 = "/data04/cedwards/forcing/mercator/reanalysis12/global-reanalysis-phy-001-030-daily_1993_parcels_v4.nc"
#model_file_OG = "/data04/cedwards/forcing/mercator/reanalysis12/global-reanalysis-phy-001-030-daily_1993.nc"



with netCDF4.Dataset(model_file_v4) as ds:
    mask_v4 = np.array(ds["mask_all"][:])[0]
    lon_v4 = np.array(ds["lon_all"][:])
    lat_v4 = np.array(ds["lat_all"][:])
    u_v4 = np.array(ds["u_all"][model_timestep_check,0,:,:])
    v_v4 = np.array(ds["v_all"][model_timestep_check,0,:,:])

u_v4[np.abs(u_v4) > 10] = np.nan
v_v4[np.abs(v_v4) > 10] = np.nan


with netCDF4.Dataset(model_file_OG) as ds:
    #mask_OG = np.array(ds["mask_all"][:])[0]
    #lon_OG = np.array(ds["longitude"][:])
    #lat_OG = np.array(ds["latitude"][:])
    u_OG = np.array(ds["uo"][model_timestep_check,0,:,:])
    v_OG = np.array(ds["vo"][model_timestep_check,0,:,:])

u_OG[np.abs(u_OG) > 10] = np.nan
v_OG[np.abs(v_OG) > 10] = np.nan


static_file = "/data04/cedwards/forcing/mercator/reanalysis12/cmems_mod_glo_phy_my_0.083deg_static_depths.nc"
with netCDF4.Dataset(static_file) as ds:
    mask_OG = np.array(ds["mask"][:])[0]
    lon_OG = np.array(ds["longitude"][:])
    lat_OG = np.array(ds["latitude"][:])






fig,ax = plt.subplots(2,3)

im1 = ax[0,0].pcolormesh(lon_OG,lat_OG,mask_OG)
ax[0,0].set_title("mask_OG")

im2 = ax[0,1].pcolormesh(lon_OG,lat_OG,u_OG)
ax[0,1].set_title("u_OG")
plt.colorbar(im2, ax=ax[0,1])

im2 = ax[0,2].pcolormesh(lon_OG,lat_OG,v_OG)
ax[0,2].set_title("v_OG")
plt.colorbar(im2, ax=ax[0,2])

im3 = ax[1,0].pcolormesh(lon_v4,lat_v4,mask_v4)
ax[1,0].set_title("mask_v4")

im4 = ax[1,1].pcolormesh(lon_v4,lat_v4,u_v4)
ax[1,1].set_title("u_v4")
plt.colorbar(im4, ax=ax[1,1])

im2 = ax[1,2].pcolormesh(lon_v4,lat_v4,v_v4)
ax[1,2].set_title("v_v4")
plt.colorbar(im2, ax=ax[1,2])


lon_min = -120.64
lon_max = -120.54

lat_min = 34.53
lat_max = 34.64

axis_lim_pad = 0.1

for ii in range(2):
    for jj in range(3):
        #ax[ii,jj].set_xlim(lon_min, lon_max)
        #ax[ii,jj].set_ylim(lat_min, lat_max)
        
        ax[ii,jj].set_xlim(lon_min - axis_lim_pad, lon_max + axis_lim_pad)
        ax[ii,jj].set_ylim(lat_min - axis_lim_pad, lat_max + axis_lim_pad)
        ax[ii,jj].scatter(lon_phantom, lat_phantom, c='r')

        ax[ii,jj].set_aspect(1.0)

figure_title = f"{model_year}, timestep: {model_timestep_check}/365ish"
#figure_title = f"Red dot indicates center of 'phantom corner' cell;  timestep: {model_timestep_check}/365ish"
title_fontsize = 8

#fig.suptitle(figure_title, fontsize=title_fontsize, y=0.95, x=0.435)
fig.suptitle(figure_title)

plt.show()






