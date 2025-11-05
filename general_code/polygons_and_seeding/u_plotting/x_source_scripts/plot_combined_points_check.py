
import netCDF4
import numpy as np
import matplotlib.pyplot as plt
import pickle
import argparse
import pathlib

parser = argparse.ArgumentParser()
parser.add_argument("gridFile", type = str)
parser.add_argument("gridName", type=str)
args = parser.parse_args()

grid_file = args.gridFile
grid_name = args.gridName




plot_switch = True
#plot_switch = False

#plot_ij = True
plot_ij = False


polygon_seed_i_j_file = f"/home/blaughli/tracking_project_v2/misc/z_boxes/add_Extra_Cells/z_output/combined_oldNew_points_i_j_{grid_name}_singleCellPolygons.p"
polygon_seed_lon_lat_file = f"/home/blaughli/tracking_project_v2/misc/z_boxes/add_Extra_Cells/z_output/combined_oldNew_points_lon_lat_{grid_name}_singleCellPolygons.p"

path_object = pathlib.Path(grid_file)
extension = path_object.suffix

if extension == ".nc":
    d = netCDF4.Dataset(grid_file, 'r')
    mask_rho = np.array(d["mask_rho"])
    lon_rho = np.array(d["lon_rho"])
    lat_rho = np.array(d["lat_rho"])
    d.close()
else:
    d = np.load(grid_file)
    mask_rho = d["mask_rho"]
    lon_rho = d["lon_rho"]
    lat_rho = d["lat_rho"]

#with np.load(grid_file) as d:
#    lon_rho = d["lon_rho"]
#    lat_rho = d["lat_rho"]
#    mask_rho = d["mask_rho"]


with open(polygon_seed_lon_lat_file,'rb') as file:
    list_of_arrays_of_points_in_polygons_lonlat = pickle.load(file)
with open(polygon_seed_i_j_file,'rb') as file:
    list_of_arrays_of_points_in_polygons_ij = pickle.load(file)

points_lonlat = np.array(list_of_arrays_of_points_in_polygons_lonlat)
points_ij = np.array(list_of_arrays_of_points_in_polygons_ij)


psijf_new = f"/home/blaughli/tracking_project_v2/misc/z_boxes/add_Extra_Cells/z_output/new_points_i_j_{grid_name}_singleCellPolygons.p"
psllf_new = f"/home/blaughli/tracking_project_v2/misc/z_boxes/add_Extra_Cells/z_output/new_points_lon_lat_{grid_name}_singleCellPolygons.p"

with open(psllf_new,'rb') as file:
    loaopipll_new = pickle.load(file)
with open(psijf_new,'rb') as file:
    loaopipij_new = pickle.load(file)

points_lonlat_new = np.array(loaopipll_new)
points_ij_new = np.array(loaopipij_new)






if plot_switch:
    if plot_ij:
        plt.pcolormesh(mask_rho)
        plt.scatter(points_ij[:,1], points_ij[:,0], c='c')
    else:
        plt.pcolormesh(lon_rho, lat_rho, mask_rho)
        plt.scatter(points_lonlat[:,0], points_lonlat[:,1], c='c', s=15)
        
        plt.scatter(points_lonlat_new[:,0], points_lonlat_new[:,1], c='r', s=5)

    plt.show()
