
import numpy as np
import matplotlib.pyplot as plt
import netCDF4

polygon_file_path = "/home/blaughli/parcels/general_code/polygons_and_seeding/z_output/bounding_boxes_lonlat_WCR30_singleCoastalCells_withPeteAdditions.txt"
grid_file_plot = "/home/blaughli/tracking_project_v2/grid_data/wcr30test1_grd.nc"
roms_grid_switch = True
plot_numbers_switch = True


empty_boxes = np.array([1159,1169,1184,1191,1204,1205,1206,1207,1208,1209,1210,1211,1212]) - 1

if roms_grid_switch:
    d = netCDF4.Dataset(grid_file_plot, 'r')
    mask_rho_plot = np.array(d["mask_rho"])
    lon_rho = np.array(d["lon_rho"])
    lat_rho = np.array(d["lat_rho"])
    d.close()
else:
    d = np.load(grid_file_plot)
    mask_rho_plot = d["mask_rho"]
    lon_rho = d["lon_rho"]
    lat_rho = d["lat_rho"]

polygon_number = 0
list_of_polygon_vertex_lonlat_lists = []
list_of_polygon_numbers = []
with open(polygon_file_path) as polygon_file:
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
m = ax.pcolormesh(lon_rho,lat_rho,mask_rho_plot,shading="nearest")

for ii in range(len(list_of_polygon_vertex_lonlat_lists)):
    if ii in empty_boxes:
        ax.plot(list_of_polygon_vertex_lonlat_lists[ii][:,0],list_of_polygon_vertex_lonlat_lists[ii][:,1], c='r')
        if plot_numbers_switch:
            ax.annotate(ii, xy = [np.mean(list_of_polygon_vertex_lonlat_lists[ii][:,0]), np.mean(list_of_polygon_vertex_lonlat_lists[ii][:,1])], ha="center", va="center", weight="bold",c='k')

ax.axis('image')

plt.show()

