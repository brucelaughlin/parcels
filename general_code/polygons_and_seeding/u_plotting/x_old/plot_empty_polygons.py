import netCDF4
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.path as plt_path
import argparse
from pathlib import Path
import pickle
from scipy.interpolate import griddata
import os
import copy

empty_boxes = np.array([1159,1169,1184,1191,1204,1205,1206,1207,1208,1209,1210,1211,1212]) - 1

GENERATE_OUTPUT_SWITCH = False

polygon_preAddition_file_path = "/home/blaughli/parcels/general_code/polygons_and_seeding/z_input_files/bounding_boxes_lonlat_WCR30_singleCoastalCells.txt"

cwd = os.getcwd()
output_dir = os.path.join(str(cwd),"z_output")
Path(output_dir).mkdir(parents=True, exist_ok=True)
bounding_boxes_file_out = os.path.join(output_dir,"bounding_boxes_lonlat_WCR30_singleCoastalCells_withPeteAdditions.p")

# Use a text csv file of polygon vertices to create the boxes
# These files must have a consistent format for their lines:
#   cell #, vertex #, lat, lon
#   001, 01, 30.050000, -115.816661
# Cell numbers in the file must always start at 1!!!!!

cell_number = 0
list_of_polygon_vertex_lonlat_lists = []
with open(polygon_preAddition_file_path) as polygon_file:
   for line in polygon_file:
        line_items = line.rstrip().split(',')
        if line_items[0].isdigit():
            if int(line_items[0]) != cell_number:
                if cell_number > 0:
                    list_of_polygon_vertex_lonlat_lists.append(current_polygon_vertices)
                cell_number += 1
                current_polygon_vertices = np.array([float(line_items[3]), float(line_items[2])])
                continue
            current_polygon_vertices = np.vstack([current_polygon_vertices, [float(line_items[3]), float(line_items[2])]]) # note that Patrick stores lat first, then lon, so I switch these
# Must append the last polygon
list_of_polygon_vertex_lonlat_lists.append(current_polygon_vertices)
num_polygons = len(list_of_polygon_vertex_lonlat_lists)
#---------------------------------------------------------------------

polygon_seed_lon_lat_file = "/home/blaughli/tracking_project_v2/misc/z_boxes/add_Extra_Cells/z_output/combined_oldNew_points_lon_lat_WCR30_singleCellPolygons.p"
file = open(polygon_seed_lon_lat_file,'rb')
list_of_arrays_of_points_in_polygons_lonlat = pickle.load(file)
file.close

lons_seed = []
lats_seed = []
for i_polygon in range(len(list_of_arrays_of_points_in_polygons_lonlat)):
    lons_seed += list(list_of_arrays_of_points_in_polygons_lonlat[i_polygon][0,:])
    lats_seed += list(list_of_arrays_of_points_in_polygons_lonlat[i_polygon][1,:])

num_seed_points = len(lons_seed)

points_lon_lat = np.zeros((num_seed_points,2))
points_lon_lat[:,0] = lons_seed
points_lon_lat[:,1] = lats_seed

# vector of length (len(lons)), to keep track of which points are not in the old list of polygons
free_point_index = np.ones(num_seed_points)

for polygon_dex in range(num_polygons):
    path = plt_path.Path(list_of_polygon_vertex_lonlat_lists[polygon_dex])
    particles_inside_flags = path.contains_points(points_lon_lat)
    free_point_index[particles_inside_flags] = 0
    
free_points_pre_mask = points_lon_lat[np.bool(free_point_index),:]

grid_file = "/home/blaughli/tracking_project_v2/grid_data/wcr30test1_grd.nc"

d = netCDF4.Dataset(grid_file, 'r')
mask_rho = np.array(d["mask_rho"][:])
lon_rho = np.array(d["lon_rho"][:])
lat_rho = np.array(d["lat_rho"][:])
mask_psi = np.array(d["mask_psi"][:])
lon_psi = np.array(d["lon_psi"][:])
lat_psi = np.array(d["lat_psi"][:])
d.close()

# Ran into a big problem here... Had to use 0.5 as my filter value, since some points had an interoplated value of 0.9999, and one of those escaped
# my box-building algorithm.  Bad explanation, but I think 0.5 makes sense - if you're >=0.5, you're definitely in the ocean...
landmask_values = griddata(np.array((lon_rho.ravel(), lat_rho.ravel())).T, mask_rho.ravel(), np.array((free_points_pre_mask[:,0], free_points_pre_mask[:,1])).T)
ocean_point_index = landmask_values >= 0.5
free_points = free_points_pre_mask[ocean_point_index]

grid_i_vector = np.arange(np.shape(lon_psi)[0])
grid_j_vector = np.arange(np.shape(lon_psi)[1])
grid_i,grid_j = np.meshgrid(grid_i_vector,grid_j_vector,indexing='ij')
free_points_i = griddata(np.array((lon_psi.ravel(), lat_psi.ravel())).T, grid_i.ravel(), np.array((free_points[:,0], free_points[:,1])).T)
free_points_j = griddata(np.array((lon_psi.ravel(), lat_psi.ravel())).T, grid_j.ravel(), np.array((free_points[:,0], free_points[:,1])).T)


# The algorithm below assumes that our seed points never land directly on a "psi line".  Dangerous!?
list_of_polygon_vertex_lonlat_lists_additions = []
for point_index in range(len(free_points_i)):
    
    ii_low = int(np.floor(free_points_i[point_index]))
    ii_high = int(np.ceil(free_points_i[point_index]))
    jj_low = int(np.floor(free_points_j[point_index]))
    jj_high = int(np.ceil(free_points_j[point_index]))

    current_polygon_vertices = np.array([lon_psi[ii_low,jj_low], lat_psi[ii_low,jj_low]])
    current_polygon_vertices = np.vstack([current_polygon_vertices, np.array([lon_psi[ii_low,jj_high], lat_psi[ii_low,jj_high]])])
    current_polygon_vertices = np.vstack([current_polygon_vertices, np.array([lon_psi[ii_high,jj_high], lat_psi[ii_high,jj_high]])])
    current_polygon_vertices = np.vstack([current_polygon_vertices, np.array([lon_psi[ii_high,jj_low], lat_psi[ii_high,jj_low]])])
    current_polygon_vertices = np.vstack([current_polygon_vertices, np.array([lon_psi[ii_low,jj_low], lat_psi[ii_low,jj_low]])])
    
    list_of_polygon_vertex_lonlat_lists_additions.append(current_polygon_vertices)

list_of_polygon_vertex_lonlat_lists += list_of_polygon_vertex_lonlat_lists_additions

fig, ax = plt.subplots()
m = ax.pcolormesh(lon_rho,lat_rho,mask_rho,shading="nearest")
for ii in range(len(list_of_polygon_vertex_lonlat_lists)):
    #if ii in empty_boxes:
    ax.plot(list_of_polygon_vertex_lonlat_lists[ii][:,0],list_of_polygon_vertex_lonlat_lists[ii][:,1], c='r')
    ax.annotate(ii, xy = [np.mean(list_of_polygon_vertex_lonlat_lists[ii][:,0]), np.mean(list_of_polygon_vertex_lonlat_lists[ii][:,1])], ha="center", va="center", weight="bold",c='k')
ax.scatter(points_lon_lat[:,0], points_lon_lat[:,1], c='c', s=15)
ax.axis('image')
plt.show()


