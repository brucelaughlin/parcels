
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
from pathlib import Path
import netCDF4

tick_label_csv_file_path = "/home/blaughli/parcels/general_code/supplementary_figures/tick_labels_single_cell_WCR30_v1_originalCells.txt"
polygon_file_path = "/home/blaughli/parcels/general_code/polygons_and_seeding/z_input_files/bounding_boxes_lonlat_WCR30_singleCoastalCells.txt"
grid_file_plot = "/home/blaughli/tracking_project_v2/grid_data/wcr30test1_grd.nc"

parser = argparse.ArgumentParser()
parser.add_argument("regionindex",type=int)
args = parser.parse_args()

region_index = args.regionindex

#plot_boxes_switch = False
plot_boxes_switch = True

# Define the tick labels and positions
tick_positions = []
tick_labels = []
with open(tick_label_csv_file_path) as tick_label_file:
   for line in tick_label_file:
        line_items = line.rstrip().split(',')
        if line_items[0].isdigit():
            tick_positions.append(int(line_items[0]))
            tick_labels.append(line_items[1])

tick_positions = np.array(tick_positions)

with netCDF4.Dataset(grid_file_plot, 'r') as dset:
    mask_rho_plot = np.array(dset["mask_rho"])
    lon_rho = np.array(dset["lon_rho"])
    lat_rho = np.array(dset["lat_rho"])

cell_number = 0
list_of_polygon_vertex_lonlat_lists = []
with open(polygon_file_path) as polygon_file:
   for line in polygon_file:
        line_items = line.rstrip().split(',')
        if line_items[0].isdigit():
            if int(line_items[0]) != cell_number:
                if cell_number > 0:
                    list_of_polygon_vertex_lonlat_lists.append(current_polygon_vertices)
                cell_number += 1
                current_polygon_vertices = np.array([float(line_items[3]), float(line_items[2])])
                continue
            current_polygon_vertices = np.vstack([current_polygon_vertices, [float(line_items[3]), float(line_items[2])]]) # Lat comes before Lon in the csv file, since that was the Patrick precedent
# Must append the last polygon
list_of_polygon_vertex_lonlat_lists.append(current_polygon_vertices)
num_polygons = len(list_of_polygon_vertex_lonlat_lists)


font_size_labels = 5

text_color = "blue"
number_color = "yellow"
arrow_color2 = "magenta" # 9
arrow_width=2
#arrow_width=4

# Copied from "https://www.geeksforgeeks.org/matplotlib-pyplot-annotate-in-python/"
bbox = dict(boxstyle ="round", fc ="0.95")

arrow_props_full_domain = dict(
    arrowstyle = "->",
    lw=arrow_width,
    color=arrow_color2)

lon_min_list = [-135, -121.8, -125, -128.5]
lon_max_list = [-116, -116.8, -121, -122.5]
lat_min_list = [31, 32.5, 35.5, 45.5]
lat_max_list = [52, 34.75, 39.5, 51.5]

#ticks_to_ignore_full_domain = [-1,91,161,194,181,392]
#ticks_to_ignore_scb = [392, tick_positions[-1]+10]
#ticks_to_ignore_central = [0,1000]
#ticks_to_ignore_north = [0,1000]

ticks_to_ignore_full_domain = [129,192,403,458,499,941,973,993,972,1010,1015,1031,1047,1062]
ticks_to_ignore_scb = []
#ticks_to_ignore_scb = [392, tick_positions[-1]+10]
ticks_to_ignore_central = []
#ticks_to_ignore_central = [0,1000]
ticks_to_ignore_north = []
#ticks_to_ignore_north = [0,1000]

ticks_to_ignore_list_of_lists = [ticks_to_ignore_full_domain, ticks_to_ignore_scb, ticks_to_ignore_central, ticks_to_ignore_north]
   

plot_title_pre = "WCR30 coastal cells v1"
title_full = f"{plot_title_pre}\nFull domain"
title_scb = f"{plot_title_pre}\nSouthern California Bight detail"
title_central = f"{plot_title_pre}\nCentral California detail"
title_northern = f"{plot_title_pre}\nnorthern west coast detail"
titles_list = [title_full, title_scb, title_central, title_northern]




offset = 100
xytext_full_domain = (-0.4 * offset, 0.0)
#xytext_full_domain = (-0.6 * offset, 0.0)
# x offset was 67.5 originally

arrow_props_full_domain = dict(
    arrowstyle = "->",
    lw=arrow_width,
    color=arrow_color2)

special_labels_dict = {}
special_labels_dict[129] = {}
special_labels_dict[129]["xytext"] = (-0.4 * offset, 0.0)
special_labels_dict[129]["arrowprops"] = arrow_props_full_domain
special_labels_dict[192] = {}
special_labels_dict[192]["xytext"] = (-0.4 * offset, 0.0 * offset)
special_labels_dict[192]["arrowprops"] = arrow_props_full_domain
#special_labels_dict[280] = {}
#special_labels_dict[280]["xytext"] = (-0.4 * offset, 0.1 * offset)
#special_labels_dict[280]["arrowprops"] = arrow_props_full_domain
special_labels_dict[954] = {}
special_labels_dict[954]["xytext"] = (-0.5 * offset, -0.1 * offset)
special_labels_dict[954]["arrowprops"] = arrow_props_full_domain
special_labels_dict[972] = {}
special_labels_dict[972]["xytext"] = (-0.15 * offset, -0.15 * offset)
special_labels_dict[972]["arrowprops"] = arrow_props_full_domain
special_labels_dict[993] = {}
special_labels_dict[993]["xytext"] = (-0.2 * offset, 0.1 * offset)
special_labels_dict[993]["arrowprops"] = arrow_props_full_domain
special_labels_dict[1010] = {}
special_labels_dict[1010]["xytext"] = (-0.5 * offset, 0.1 * offset)
special_labels_dict[1010]["arrowprops"] = arrow_props_full_domain
special_labels_dict[1031] = {}
special_labels_dict[1031]["xytext"] = (0.2 * offset, -0.1 * offset)
special_labels_dict[1031]["arrowprops"] = arrow_props_full_domain
special_labels_dict[1047] = {}
special_labels_dict[1047]["xytext"] = (-0.4 * offset, 0.1 * offset)
special_labels_dict[1047]["arrowprops"] = arrow_props_full_domain
special_labels_dict[1062] = {}
special_labels_dict[1062]["xytext"] = (-0.4 * offset, -0.1 * offset)
special_labels_dict[1062]["arrowprops"] = arrow_props_full_domain







#dpi = 100
dpi = 200
fig, ax = plt.subplots(dpi=dpi) #fig, ax = plt.subplots()

m = ax.pcolormesh(lon_rho,lat_rho,mask_rho_plot,shading="nearest")

for ii in range(len(list_of_polygon_vertex_lonlat_lists)):
    if plot_boxes_switch:
        if region_index != 0:
            ax.plot(list_of_polygon_vertex_lonlat_lists[ii][:,0],list_of_polygon_vertex_lonlat_lists[ii][:,1], c='c')
    if ii in tick_positions and ii not in ticks_to_ignore_list_of_lists[region_index]:
#    if ii in tick_positions:
        xy_loc = [np.mean(list_of_polygon_vertex_lonlat_lists[ii][:,0]), np.mean(list_of_polygon_vertex_lonlat_lists[ii][:,1])]
        #if ii in special_arrows_indices:
        if ii in list(special_labels_dict.keys()):
            (ax.annotate("{}".format(tick_labels[np.where(tick_positions==ii)[0][0]]), xy = xy_loc,
                xytext = special_labels_dict[ii]["xytext"], textcoords ='offset points', bbox = bbox, 
            arrowprops = special_labels_dict[ii]["arrowprops"], color=text_color, va="center", ha="center",fontsize=font_size_labels))
        else:
            (ax.annotate("{}".format(tick_labels[np.where(tick_positions==ii)[0][0]]), xy = xy_loc,
                xytext = xytext_full_domain, textcoords ='offset points', bbox = bbox, 
                #xytext = (-.9 * offset, .0), textcoords ='offset points', bbox = bbox, 
            arrowprops = arrow_props_full_domain, color=text_color, va="center", ha="center",fontsize=font_size_labels))
    

ax.axis('image')

save_file_full = "WCR30_full_domain"
save_file_scb = "WCR30_SCB_detail"
save_file_central = "WCR30_central_detail"
save_file_northern = "WCR30_northern_detail"
save_file_list = [save_file_full, save_file_scb, save_file_central, save_file_northern]

if region_index > 0:
    plt.xlim(lon_min_list[region_index], lon_max_list[region_index])
    plt.ylim(lat_min_list[region_index], lat_max_list[region_index])

plt.title(titles_list[region_index])

ticklabelsize = 6
ax.tick_params(axis='x', labelsize=ticklabelsize)
ax.tick_params(axis='y', labelsize=ticklabelsize)


cwd = os.getcwd()
output_dir = os.path.join(str(cwd),"z_output")
Path(output_dir).mkdir(exist_ok=True)

if plot_boxes_switch:
    save_file = os.path.join(output_dir,f'{save_file_list[region_index]}_withPolygons.png')
else:
    save_file = os.path.join(output_dir,f'{save_file_list[region_index]}.png')

plt.show()
#plt.savefig(save_file, bbox_inches = "tight")

