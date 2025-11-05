
# I think we'll always want these, can always revert if necessary
logSwitch = True
plotDiagonalLineSwitch = True


# <model_string> should also be variable, but I don't have it stored in my connectivity output paths...
model_string = "wcr30_ERA1_v1"

max_seed_depth = 20

dpi = 300

annualSeasonIndex = 4

tick_label_file_path = "/home/blaughli/parcels/general_code/supplementary_figures/tick_labels_single_cell_WCR30_v1_originalCells.txt"

subplot_label_fontsize = 6
title_fontsize = 8
    
#tick_label_fontsize=1.7
tick_label_fontsize=2
#tick_label_fontsize=3
#tick_label_fontsize=4.5
label_fontsize=6


# New approach: set min val to log(0.0001), so 0.0001 is our smallest colorbar tick. indicate that in colorbar tick labels
pdf_min_val = 0
#pdf_min_val_log = 0.0001
pdf_min_val_log = 0.00001

pdf_max_val = 0.01
#pdf_max_val_log = 0.1
pdf_max_val_log = 0.01

#---------------------------------------------------------------------

import matplotlib.colors as colors
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import argparse
import os
from pathlib import Path
from glob import glob
import netCDF4

'''
parser = argparse.ArgumentParser()
parser.add_argument("--connectivityfilenc", type=str)
args = parser.parse_args()

connectivity_file_nc = args.csvconnectivityfile
'''


connectivity_file_nc = "/home/blaughli/parcels/processing/n_generate_netcdf_output/z_output/connectivity_data__ROMS_WCR30_v1_originalPolygonsWithoutPeteAdditions__years_1999_2024__season_Jan-Dec.nc"


figures_dir = os.path.join(os.path.dirname(connectivity_file_nc),"z_figures")
Path(figures_dir).mkdir(parents=True, exist_ok=True)

# creating printable strings of relevant information
years_first = connectivity_file_nc.split("years_")[-1].split("_")[0]
years_last = connectivity_file_nc.split("years_")[-1].split("_")[1]
years_string = f"{years_first}-{years_last}"

figure_years_dir = os.path.join(figures_dir,years_string)
Path(figure_years_dir).mkdir(parents=True, exist_ok=True)

season_string = connectivity_file_nc.split("season_")[-1].split(".")[0]
seasonal_labels_list = ["Jan-Mar","Apr-Jun","Jul_Sep","Oct-Dec", "Jan-Dec"]
season_string_number = seasonal_labels_list.index(season_string) + 1

if season_string_number == 5:
    figure_seasons_dir = os.path.join(figure_years_dir,"annual")
else:
    figure_seasons_dir = os.path.join(figure_years_dir,"seasonal")
Path(figure_seasons_dir).mkdir(parents=True, exist_ok=True)





with netCDF4.Dataset(connectivity_file_nc, 'r') as ds:

    pld_days = np.array(ds["pld_days"][:]) 
    connectivity_data = np.array(ds["connectivity_data"][:]) 
    polygon_release_counts = np.array(ds["release_count_data"][:]) 
    settle_count_overall_per_pld = np.array(ds["settle_count_overall_per_pld"][:]) 
    settle_strength_overall_per_pld = np.array(ds["settle_strength_overall_per_pld"][:]) 


for pld_index in range(len(pld_days)):

    pld_first_day = pld_days[pld_index][0]
    pld_last_day = pld_days[pld_index][1]
    pld_string_print = f"{pld_first_day}-{pld_last_day}"
    pld_string_save = f"{pld_first_day:03d}-{pld_last_day:03d}"
    
    connectivity_pdf = connectivity_data[:,:,pld_index]
    settle_count = settle_count_overall_per_pld[pld_index]
    settle_strength = settle_strength_overall_per_pld[pld_index]
    

    if logSwitch:
        figure_output_file = f"connectivity_plot_years_{years_string}_PLD_{pld_string_save}_season_{season_string_number}_{season_string}_logScale.png"
    else:
        figure_output_file = f"connectivity_plot_years_{years_string}_PLD_{pld_string_save}_season_{season_string_number}_{season_string}.png"
    #figure_output_path = os.path.join(figure_seasons_dir,figure_output_file)

    temp_output_dir = os.path.join(os.getcwd(), "z_output")
    Path(temp_output_dir).mkdir(parents=True, exist_ok=True)

    figure_output_path = os.path.join(temp_output_dir,figure_output_file)


    # Define the tick labels and positions
    # Hacky - after looking at plots, need to ignore some tick labels to avoid cluttering
    #ticks_positions_to_ignore = [1010]
    ticks_positions_to_ignore = [993, 1010]

    tick_positions = []
    tick_labels = []
    with open(tick_label_file_path) as tick_label_file:
       for line in tick_label_file:
            line_items = line.rstrip().split(',')
            if line_items[0].isdigit():
                if int(line_items[0]) not in ticks_positions_to_ignore:
                    tick_positions.append(int(line_items[0]))
                    tick_labels.append(line_items[1])





    #if annualOnlySwitch:
    nrows = 1
    ncols = 1
    #else:
    #    nrows = 2
    #    ncols = 2

    #if annualOnlySwitch:
    figsize = (6*ncols+2,6*nrows+1)
    #else:
    #    figsize = (6*ncols+2,6*nrows)

    fig,axs = plt.subplots(nrows=nrows,ncols=ncols, squeeze=False, figsize=figsize, gridspec_kw={'hspace':0.0001, 'wspace':0.15}, dpi=dpi)

    num_dummy_lines = 1

    #boundary_index = 27
    #island_index = 489

    pdf_plot = connectivity_pdf

    #subplot_label = f"num floats: {num_released_per_season[season_index]}, n settlers: {num_settled_per_pld_per_season[pld_index,season_index]}, settle strength: {settle_strength_array[season_index]:.3f}"

    n_boxes_seeded = int(np.shape(pdf_plot)[1])
    n_boxes_settled = int(np.shape(pdf_plot)[0])
    X = np.arange(-0.5, n_boxes_settled, 1)
    Y = np.arange(-0.5, n_boxes_seeded, 1)

    if logSwitch:
        mesh1 = axs[0,0].pcolormesh(X,Y,pdf_plot.T,cmap='jet',norm=colors.LogNorm(vmin=pdf_min_val_log,vmax=pdf_max_val_log),shading='auto')
    else:
        mesh1 = axs[0,0].pcolormesh(X,Y,pdf_plot.T,cmap='jet',vmin=pdf_min_val,vmax=pdf_max_val,shading='auto')
    if plotDiagonalLineSwitch:
        axs[0,0].plot([0,np.shape(pdf_plot.T)[1]-1],[0,np.shape(pdf_plot.T)[0]-1],color="white",linewidth=0.2)
        #axs[0,0].plot([0,np.shape(pdf_plot.T)[1]-1],[0,np.shape(pdf_plot.T)[0]-1],color="white",linewidth=0.5)
    axs[0,0].set_aspect('equal')

    axs[0,0].set_xticks(tick_positions)
    axs[0,0].set_xticklabels(tick_labels,fontsize=tick_label_fontsize, rotation ='vertical')
    axs[0,0].set_yticks(tick_positions)
    axs[0,0].set_yticklabels(tick_labels,fontsize=tick_label_fontsize)
    axs[0,0].set_xlabel("release cell",fontsize=label_fontsize)
    axs[0,0].set_ylabel("settling cell",fontsize=label_fontsize)

    axs[0,0].xaxis.set_major_locator(plt.FixedLocator(tick_positions))
    axs[0,0].yaxis.set_major_locator(plt.FixedLocator(tick_positions))

    axs[0,0].grid(True, which='major', linestyle='-', linewidth=0.2, color='gray')
    axs[0,0].set_axisbelow(True)

    overall_plot_title = ""
    overall_plot_title += f"{model_string}"
    overall_plot_title += f"\nPLD: {pld_string_print} days"
    overall_plot_title += f"\nReleased {years_string}, {season_string}, 0-{max_seed_depth}m"
    overall_plot_title += f"\nnum floats: {int(np.sum(polygon_release_counts))}, n settlers: {settle_count}, settle strength: {settle_strength:.3f}"

    cbar_label = "probability"

    cbar = plt.colorbar(mesh1, ax=axs.ravel(), shrink=0.6)
    fig.suptitle(overall_plot_title, fontsize=title_fontsize, y=0.95, x=0.435)

    plt.savefig(figure_output_path, bbox_inches = "tight")

    #plt.show()



