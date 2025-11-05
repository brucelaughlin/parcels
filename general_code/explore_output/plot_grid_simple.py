import matplotlib.pyplot as plt
import netCDF4

#grid_file = "/home/blaughli/tracking_project_v2/grid_data/grd_wcofs4_visc200_50-50-50.nc"
grid_file = "/home/blaughli/tracking_project_v2/grid_data/wcr30test1_grd.nc"
with netCDF4.Dataset(grid_file,"r") as d:
    lat_rho = d[f"lat_rho"][:].data
    lon_rho = d[f"lon_rho"][:].data
    mask_rho = d[f"mask_rho"][:].data
    h = d[f"h"][:].data

fig,ax = plt.subplots()
ax.pcolormesh(lon_rho,lat_rho,mask_rho)
plt.show()

