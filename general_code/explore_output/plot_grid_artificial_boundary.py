import matplotlib.pyplot as plt
import netCDF4

grid_file = "/home/blaughli/tracking_project_v2/grid_data/wcr30test1_grd.nc"
with netCDF4.Dataset(grid_file,"r") as d:
    lat_rho = d[f"lat_rho"][:].data
    lon_rho = d[f"lon_rho"][:].data
    mask_rho = d[f"mask_rho"][:].data

#buffer_size = 10
buffer_size = 5

lons_boundary = []
lats_boundary = []

lons_boundary += list(lon_rho[buffer_size,buffer_size:-buffer_size])
lons_boundary += list(lon_rho[buffer_size:-buffer_size,-buffer_size-1])
lons_boundary += list(lon_rho[-buffer_size-1,buffer_size:-buffer_size][::-1])
lons_boundary += list(lon_rho[buffer_size:-buffer_size,buffer_size][::-1])

lats_boundary += list(lat_rho[buffer_size,buffer_size:-buffer_size])
lats_boundary += list(lat_rho[buffer_size:-buffer_size,-buffer_size-1])
lats_boundary += list(lat_rho[-buffer_size-1,buffer_size:-buffer_size][::-1])
lats_boundary += list(lat_rho[buffer_size:-buffer_size,buffer_size][::-1])


domain_boundary_lon_lat = np.array([lons_boundary,lats_boundary]).T

fig,ax = plt.subplots()
ax.pcolormesh(lon_rho,lat_rho,mask_rho)
ax.plot(lons_boundary,lats_boundary,c='r')
plt.show()

