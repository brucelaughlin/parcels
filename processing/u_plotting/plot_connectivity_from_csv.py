
# <model_string> should also be variable, but I don't have it stored in my connectivity output paths...
model_string = "wcr30_ERA1_v1"

max_seed_depth = 20

dpi = 300

annualSeasonIndex = 4

tick_label_file_path = "/home/blaughli/parcels/general_code/supplementary_figures/tick_labels_single_cell_WCR30_v1_originalCells.txt"

subplot_label_fontsize = 6
title_fontsize = 8
    
#tick_label_fontsize=1.7
#tick_label_fontsize=2
tick_label_fontsize=3
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
import pandas as pd

#'''
parser = argparse.ArgumentParser()
parser.add_argument("--csvconnectivityfile", type=str)
#parser.add_argument("csvreleasecountfile", type=str)
#parser.add_argument("txtsettlestrengthfile", type=str)
#parser.add_argument("txtsettlecountfile", type=str)

args = parser.parse_args()

csv_connectivity_file = args.csvconnectivityfile
#csv_release_count_file = args.csvreleasecountfile
#txt_settle_strength_file = args.txtsettlestrengthfile
#txt_settle_count_file = args.txtsettlecountfile

input_filename_universal_pieces = csv_connectivity_file.split("connectivity_data")

csv_release_count_file = f"{input_filename_universal_pieces[0]}release_counts{input_filename_universal_pieces[-1]}"
txt_settle_count_file = f"{input_filename_universal_pieces[0]}settle_count{input_filename_universal_pieces[-1]}"
txt_settle_strength_file = f"{input_filename_universal_pieces[0]}settle_strength{input_filename_universal_pieces[-1]}"

txt_settle_count_file = f"{txt_settle_count_file.split(".")[0]}.txt"
txt_settle_strength_file = f"{txt_settle_strength_file.split(".")[0]}.txt"
#'''

'''
csv_connectivity_file = "/home/blaughli/parcels/processing/p_production/z_binned_preconnectivty_data/binned_data_oldPolygonsNoPete_v1/z_connectivity_csv_files_withSeasons/connectivity_data_years_1999_2005_PLD_001_005_season_Jan-Dec.csv"
csv_release_count_file = "/home/blaughli/parcels/processing/p_production/z_binned_preconnectivty_data/binned_data_oldPolygonsNoPete_v1/z_connectivity_csv_files_withSeasons/release_counts_years_1999_2005_PLD_001_005_season_Jan-Dec.csv"
txt_settle_strength_file = "/home/blaughli/parcels/processing/p_production/z_binned_preconnectivty_data/binned_data_oldPolygonsNoPete_v1/z_connectivity_csv_files_withSeasons/settle_strength_years_1999_2005_PLD_001_005_season_Jan-Dec.txt"
txt_settle_count_file = "/home/blaughli/parcels/processing/p_production/z_binned_preconnectivty_data/binned_data_oldPolygonsNoPete_v1/z_connectivity_csv_files_withSeasons/settle_count_years_1999_2005_PLD_001_005_season_Jan-Dec.txt"
'''

'''
csv_connectivity_file = "/home/blaughli/parcels/processing/p_production/z_binned_preconnectivty_data/binned_data_oldPolygonsNoPete_v1/z_connectivity_csv_files_withSeasons/connectivity_data_years_1999_2005_PLD_045_060_season_Jan-Dec.csv"
csv_release_count_file = "/home/blaughli/parcels/processing/p_production/z_binned_preconnectivty_data/binned_data_oldPolygonsNoPete_v1/z_connectivity_csv_files_withSeasons/release_counts_years_1999_2005_PLD_045_060_season_Jan-Dec.csv"
txt_settle_strength_file = "/home/blaughli/parcels/processing/p_production/z_binned_preconnectivty_data/binned_data_oldPolygonsNoPete_v1/z_connectivity_csv_files_withSeasons/settle_strength_years_1999_2005_PLD_045_060_season_Jan-Dec.txt"
txt_settle_count_file = "/home/blaughli/parcels/processing/p_production/z_binned_preconnectivty_data/binned_data_oldPolygonsNoPete_v1/z_connectivity_csv_files_withSeasons/settle_count_years_1999_2005_PLD_045_060_season_Jan-Dec.txt"
'''

figures_dir = os.path.join(os.path.dirname(csv_connectivity_file),"z_figures")
Path(figures_dir).mkdir(parents=True, exist_ok=True)

# creating printable strings of relevant information
years_first = csv_connectivity_file.split("years_")[-1].split("_")[0]
years_last = csv_connectivity_file.split("years_")[-1].split("_")[1]
years_string = f"{years_first}-{years_last}"

figure_years_dir = os.path.join(figures_dir,years_string)
Path(figure_years_dir).mkdir(parents=True, exist_ok=True)

season_string = csv_connectivity_file.split("season_")[-1].split(".")[0]
seasonal_labels_list = ["Jan-Mar","Apr-Jun","Jul_Sep","Oct-Dec", "Jan-Dec"]
season_string_number = seasonal_labels_list.index(season_string) + 1

if season_string_number == 5:
    figure_seasons_dir = os.path.join(figure_years_dir,"annual")
else:
    figure_seasons_dir = os.path.join(figure_years_dir,"seasonal")
Path(figure_seasons_dir).mkdir(parents=True, exist_ok=True)

pld_first_day = csv_connectivity_file.split("PLD_")[-1].split("_")[0]
pld_last_day = csv_connectivity_file.split("PLD_")[-1].split("_")[1]
pld_string_print = f"{int(pld_first_day)}-{int(pld_last_day)}"
pld_string_save = f"{pld_first_day}-{pld_last_day}"


# I think we'll always want these, can always revert if necessary
logSwitch = True
plotDiagonalLineSwitch = True

if logSwitch:
    figure_output_file = f"connectivity_plot_years_{years_string}_PLD_{pld_string_save}_season_{season_string_number}_{season_string}_logScale.png"
else:
    figure_output_file = f"connectivity_plot_years_{years_string}_PLD_{pld_string_save}_season_{season_string_number}_{season_string}.png"






figure_output_path = os.path.join(figure_seasons_dir,figure_output_file)
#figure_output_path = os.path.join(figure_dir,figure_output_file)



'''
output_figures_dir = os.path.join(connectivity_data_dir,output_figures_dir_stem)
Path(output_figures_dir).mkdir(parents=True, exist_ok=True)

output_csv_dir = os.path.join(connectivity_data_dir,output_csv_dir_stem)
Path(output_csv_dir).mkdir(parents=True, exist_ok=True)

figure_title_base = Path(tracking_dir).stem
'''



release_months_list_pre = np.array(["Dec-Feb", "March-May","June-Aug","Sep-Nov","Jan-Dec"])

#file_list = sorted(glob(os.path.join(connectivity_data_dir,"*.npz")))

#d = np.load(file_list[0])


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


df_connectivity = pd.read_csv(csv_connectivity_file, header=None)
connectivity_pdf = df_connectivity.values

df_release_count = pd.read_csv(csv_release_count_file, header=None)
polygon_release_counts = df_release_count.values

with open(txt_settle_count_file, "r") as file:
    settle_count_string = file.readline()
    settle_count = int(settle_count_string.strip())

with open(txt_settle_strength_file, "r") as file:
    settle_strength_string = file.readline()
    settle_strength = float(settle_strength_string.strip())



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

#pcolormesh_plot_list = []

num_dummy_lines = 1

# Wait, there are 5 pdfs in the list - the first (index 0) is the overall pdf (non-seasonal).  So, do I have a 1-off error here?



#boundary_index = 27
#island_index = 489

'''
print(f"Number of pdfs: {len(connectivity_pdf_list[pld_index])}")

for season_index in pdfs_to_plot_indices:

if annualOnlySwitch:
    csv_file_leaf_pre = f"settlement_{output_file_general_leaf_pre}"
    csv_file_leaf = f"{csv_file_leaf_pre}.csv"
    season_index = 0
else:
    release_months_string = release_months_list_pre[pdfs_to_plot_indices[season_index]]  
    csv_file_leaf_pre = f"settlement_{output_file_general_leaf_pre}_months_{release_months_string}"
    csv_file_leaf = f"{csv_file_leaf_pre}.csv"

csv_file_out = os.path.join(output_figures_dir,csv_file_leaf)

pdf_plot = connectivity_pdf_list[pld_index][season_index]

# Save the connectivity data to a csv file
np.savetxt(csv_file_out,pdf_plot,delimiter=',',fmt='%1.8e')
'''
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
#axs[0,0].set_xlabel("release cell")
#axs[0,0].set_ylabel("settling cell")
axs[0,0].set_xlabel("release cell",fontsize=label_fontsize)
axs[0,0].set_ylabel("settling cell",fontsize=label_fontsize)

axs[0,0].xaxis.set_major_locator(plt.FixedLocator(tick_positions))
axs[0,0].yaxis.set_major_locator(plt.FixedLocator(tick_positions))

axs[0,0].grid(True, which='major', linestyle='-', linewidth=0.2, color='gray')
axs[0,0].set_axisbelow(True)

overall_plot_title = ""
overall_plot_title += f"{model_string}"
overall_plot_title += f"\nPLD: {pld_string_print} days"
#if annualOnlySwitch:
#overall_plot_title += f"\nReleased {release_months_list_pre[-1]}, 0-{max_seed_depth}m"
overall_plot_title += f"\nReleased {years_string}, {season_string}, 0-{max_seed_depth}m"
overall_plot_title += f"\nnum floats: {int(np.sum(polygon_release_counts))}, n settlers: {settle_count}, settle strength: {settle_strength:.3f}"
#overall_plot_title += f"\nnum floats: {np.sum(num_released_per_season)}, n settlers: {np.sum(num_settled_per_pld_per_season[pld_index])}, settle strength: {settle_strength_full_run:.3f}"
#else:
#    overall_plot_title += f"\nReleased seasonally, 0-{max_seed_depth}m"
#    overall_plot_title += f"\nOverall: num floats: {np.sum(num_released_per_season)}, n settlers: {np.sum(num_settled_per_pld_per_season[pld_index])}, settle strength: {settle_strength_full_run:.3f}"
#if ignoreStagnantSwitch:
#    overall_plot_title += "\nhomebodies removed"
#else:
#    overall_plot_title += "\nhomebodies included"


cbar_label = "probability"

cbar = plt.colorbar(mesh1, ax=axs.ravel(), shrink=0.6)

#figure_title = figure_title_base + "\n" + overall_plot_title

fig.suptitle(overall_plot_title, fontsize=title_fontsize, y=0.95, x=0.435)

plt.savefig(figure_output_path, bbox_inches = "tight")

#plt.show()



