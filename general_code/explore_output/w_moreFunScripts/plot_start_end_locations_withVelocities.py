import xarray as xr
import netCDF4
import numpy as np
import matplotlib.pyplot as plt

'''
parser = argparse.ArgumentParser()
parser.add_argument("--trackingfile", type=str)
args = parser.parse_args()

tracking_file = args.trackingfile

'''
#polygon_file_path = "/home/blaughli/tracking_project_v2/misc/z_boxes/z_output/bounding_boxes_lonlat_Mercator_singleCoastalCells.txt"

#tracking_file = "/home/blaughli/parcels/z_production/z_2D/z_output/global-reanalysis-phy-001-030-daily_1993_2024_V4__fileNumber_00/proc23.zarr"
#tracking_file = "/home/blaughli/parcels/z_production/z_2D/z_output/global-reanalysis-phy-001-030-daily_1993_2024_V4__fileNumber_00/proc00.zarr"
tracking_file = "/home/blaughli/parcels/processing/w_explore/z_output/tracking_data_problematic_particles_v1.zarr"

particle_dimension = 0
time_dimension = 1

# Pete Raimondi's PLDs
pld_list = [[1,5],[5,10],[10,15],[15,30],[30,45],[45,60],[60,75],[75,90],[90,120],[120,150],[150,180]]

num_plds = len(pld_list)

with xr.open_zarr(tracking_file) as ds:

    lon_all = ds.lon.values
    lat_all = ds.lat.values
    age_all = ds.age.values
    time_all = ds.time.values

num_particles = np.shape(lon_all)[particle_dimension]
num_timesteps = np.shape(lon_all)[time_dimension]

time_units_between_output_timesteps = int(age_all[0,1] - age_all[0,0])

# Haven't thought about how to make this dynamic yet.
if time_units_between_output_timesteps == 24:
    timesteps_per_day = 1
else:
    raise RuntimeError('Just testing now, and expected output dt of 24 hours')

## NEW ALGORITHM
pld_list_timesteps = pld_list.copy()
for pld_dex in range(len(pld_list)):
    for day_dex in range(2):
        pld_list_timesteps[pld_dex][day_dex] *= timesteps_per_day


lons_start = lon_all[:,0]
lats_start = lat_all[:,0]

lons_end = []
lats_end = []
end_indices = []

#'''
for i_particle in range(lon_all.shape[0]):
    lon_particle = lon_all[i_particle,:]
    lat_particle = lat_all[i_particle,:]
    mask = np.logical_not(np.isnan(lon_particle))
    lons_end.append(lon_particle[mask][-1])
    lats_end.append(lat_particle[mask][-1])
    end_indices.append(sum(mask)-1)
#'''

#'''
model_file = "/data04/cedwards/forcing/mercator/reanalysis12/global-reanalysis-phy-001-030-daily_1993_parcels_v4.nc"
with netCDF4.Dataset(model_file) as ds:
    mask_v4 = np.array(ds["mask_all"][:])[0]
    lon_v4 = np.array(ds["lon_all"][:])
    lat_v4 = np.array(ds["lat_all"][:])
    u_v4 = np.array(ds["u_all"][0,0,:,:])
    v_v4 = np.array(ds["v_all"][0,0,:,:])

#plt.pcolormesh(lon_rho,lat_rho,u_rho)
#'''

static_file = "/data04/cedwards/forcing/mercator/reanalysis12/cmems_mod_glo_phy_my_0.083deg_static_depths.nc"
with netCDF4.Dataset(static_file) as ds:
    mask_rho = np.array(ds["mask"][:])[0]
    lon_rho = np.array(ds["longitude"][:])
    lat_rho = np.array(ds["latitude"][:])


fig,ax = plt.subplots(1,3)

ax[0].pcolormesh(lon_rho,lat_rho,mask_rho)
ax[0].set_title("mask_v4")
#ax[0].set_title("mask_rho")
ax[1].pcolormesh(lon_v4,lat_v4,u_v4)
ax[1].set_title("u_v4")
ax[2].pcolormesh(lon_v4,lat_v4,v_v4)
ax[2].set_title("v_v4")

for ii in range(3):
    ax[ii].scatter(lons_end, lats_end, c='r', s=1) #, zorder=3)
    ax[ii].scatter(lons_start, lats_start, c='g', s=1) #, zorder=3)


plt.show()






