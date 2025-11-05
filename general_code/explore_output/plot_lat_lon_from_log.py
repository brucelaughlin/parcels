import os
import matplotlib.pyplot as plt
import numpy as np
import re
import netCDF4
import argparse

match_pattern = r"\((?P<longitude>[+-]?\d+(\.\d+)?)\s*,\s*(?P<latitude>[+-]?\d+(\.\d+)?)\)"

dpi = 300

num_floats_seeded = 12248

output_dir_general = f"{os.getcwd()}/y_figures"
os.makedirs(output_dir_general, exist_ok = True)

parser = argparse.ArgumentParser()
parser.add_argument("filename", type=str)
parser.add_argument("regiondex", type=int)
args = parser.parse_args()

filename = args.filename
region_index = args.regiondex

if region_index == 1:
    label = "north"
    x_low = -127
    x_high = -122
    y_low = 41.5
    y_high = 47.5
elif region_index == 2:
    label = "central"
    x_low = -125.25
    x_high = -123.5
    y_low = 39.25
    y_high = 41.25
elif region_index == 3:
    label = "south"
    x_low = -122.5
    x_high = -117
    y_low = 32
    y_high = 37

lats = []
lons = []

num_floats_bad = 0
with open(filename) as f:
    for line in f:
        latlon_group = re.search(match_pattern, line)
        if latlon_group is not None:
            group_dict = latlon_group.groupdict() 
            lats.append(float(group_dict["latitude"]))
            lons.append(float(group_dict["longitude"]))
            num_floats_bad += 1


if region_index > 0:
    num_floats_figure = 0
    for i_float in range(len(lons)):
        if lons[i_float] > x_low and lons[i_float] < x_high and lats[i_float] > y_low and lats[i_float] < y_high:
            num_floats_figure += 1
    

grid_file = "/home/blaughli/tracking_project_v2/grid_data/wcr30test1_grd.nc"
with netCDF4.Dataset(grid_file,"r") as d:
    lat_rho = d[f"lat_rho"][:].data
    lon_rho = d[f"lon_rho"][:].data
    mask_rho = d[f"mask_rho"][:].data
    h = d[f"h"][:].data

#h[h <= 10] = np.nan
h[mask_rho == 0] = np.nan

#h[h > 500] = np.nan

fig,ax = plt.subplots()
ax.pcolormesh(lon_rho,lat_rho,h)
#cs = ax.contour(lon_rho, lat_rho, h, 20)
ax.scatter(lons,lats, c= 'r', s=20)#, zorder=0)

#ax.clabel(cs, inline=True, fontsize=10, fmt="%d")

#plt.colorbar(cs, ax=ax)

if region_index > 0:
    plt.xlim(x_low,x_high)
    plt.ylim(y_low,y_high)


save_file_pre = filename.split("/")[-2]


#label = "blah"
if region_index > 0:
    title = f"({label})\ndeleted/total: {num_floats_bad}/{num_floats_seeded}\nwithin image: {num_floats_figure}/{num_floats_bad}"
    #title = f"target depth above bottom: {filename.split("/")[-2].split("_")[-1]}m   ({label})\ndeleted/total: {num_floats_bad}/{num_floats_seeded}\nwithin image: {num_floats_figure}/{num_floats_bad}"
else:
    title = f"deleted/total: {num_floats_bad}/{num_floats_seeded}"


plt.title(title)

plt.show()

#plt.savefig(os.path.join(output_dir_general,f"{save_file_pre}__{label}.png"))

