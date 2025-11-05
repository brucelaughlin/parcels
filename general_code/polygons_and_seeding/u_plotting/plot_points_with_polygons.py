
import netCDF4
import numpy as np
import matplotlib.pyplot as plt
import pickle
import argparse
import pathlib

#polygon_file_path = "/home/blaughli/parcels/general_code/polygons_and_seeding/z_output/ROMS_ParentCellsOnly_WGS84.txt"
#polygon_file_path = "/home/blaughli/parcels/general_code/polygons_and_seeding/z_input_files/bounding_boxes_lonlat_WCR30_singleCoastalCells.txt"
polygon_file_path = "/home/blaughli/parcels/general_code/polygons_and_seeding/z_output/bounding_boxes_lonlat_WCR30_withPeteAdditions_romsGridCellCentroidsOnly.txt"
#polygon_seed_lon_lat_file = "/home/blaughli/tracking_project_v2/misc/z_boxes/add_Extra_Cells/z_output/combined_oldNew_points_lon_lat_WCR30_singleCellPolygons.p"
polygon_seed_lon_lat_file = "/home/blaughli/parcels/general_code/polygons_and_seeding/z_output/seeding_latlon_WCR30_withPeteAdditions_romsGridCellCentroidsOnly.p"
grid_file = "/home/blaughli/tracking_project_v2/grid_data/wcr30test1_grd.nc"

d = netCDF4.Dataset(grid_file, 'r')
mask_rho = np.array(d["mask_rho"])
lon_rho = np.array(d["lon_rho"])
lat_rho = np.array(d["lat_rho"])
d.close()


with open(polygon_seed_lon_lat_file,'rb') as file:
    list_of_arrays_of_points_in_polygons_lonlat = pickle.load(file)
#with open(polygon_seed_i_j_file,'rb') as file:
#    list_of_arrays_of_points_in_polygons_ij = pickle.load(file)

points_lonlat = np.array(list_of_arrays_of_points_in_polygons_lonlat)
#points_ij = np.array(list_of_arrays_of_points_in_polygons_ij)

'''
psijf_new = f"/home/blaughli/tracking_project_v2/misc/z_boxes/add_Extra_Cells/z_output/new_points_i_j_{grid_name}_singleCellPolygons.p"
psllf_new = f"/home/blaughli/tracking_project_v2/misc/z_boxes/add_Extra_Cells/z_output/new_points_lon_lat_{grid_name}_singleCellPolygons.p"

with open(psllf_new,'rb') as file:
    loaopipll_new = pickle.load(file)
with open(psijf_new,'rb') as file:
    loaopipij_new = pickle.load(file)

points_lonlat_new = np.array(loaopipll_new)
points_ij_new = np.array(loaopipij_new)
'''

polygon_number = 0
list_of_polygon_vertex_lonlat_lists = []
list_of_polygon_numbers = []
with open(polygon_file_path) as polygon_file:
#with open(polygon_file_path) as polygon_file:
   for line in polygon_file:
        line_items = line.rstrip().split(',')
        if line_items[0].isdigit():
            if int(line_items[0]) != polygon_number:
                if polygon_number > 0:
                    list_of_polygon_vertex_lonlat_lists.append(current_polygon_vertices)
                #list_of_polygon_numbers.append(int(line_items[0]))
                polygon_number = int(line_items[0])
                current_polygon_vertices = np.array([float(line_items[3]), float(line_items[2])])
                continue
            current_polygon_vertices = np.vstack([current_polygon_vertices, [float(line_items[3]), float(line_items[2])]]) # Lat comes before Lon in the csv file, since that was the Patrick precedent
# Must append the last polygon
list_of_polygon_vertex_lonlat_lists.append(current_polygon_vertices)
num_polygons = len(list_of_polygon_vertex_lonlat_lists)


fig, ax = plt.subplots()
m = ax.pcolormesh(lon_rho,lat_rho,mask_rho,shading="nearest")

for ii in range(len(list_of_polygon_vertex_lonlat_lists)):
    ax.plot(list_of_polygon_vertex_lonlat_lists[ii][:,0],list_of_polygon_vertex_lonlat_lists[ii][:,1], c='r')
#    if plot_numbers_switch:
#        ax.annotate(ii, xy = [np.mean(list_of_polygon_vertex_lonlat_lists[ii][:,0]), np.mean(list_of_polygon_vertex_lonlat_lists[ii][:,1])], ha="center", va="center", weight="bold",c='k')

ax.axis('image')



#plt.pcolormesh(mask_rho)
#plt.scatter(points_ij[:,1], points_ij[:,0], c='c')

ax.scatter(points_lonlat[:,0], points_lonlat[:,1], c='c', s=15)

#plt.scatter(points_lonlat_new[:,0], points_lonlat_new[:,1], c='r', s=5)

plt.show()
