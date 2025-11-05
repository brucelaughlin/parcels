#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# NEED TO CHANGE THE OUTPUT FILENAMES LIKE CHRIS SAID, SO THAT WE CAN VERY EASILY SUBSELECT FOR YEARS AND PLDS JUST FROM THE FILENAME STEMS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import argparse
import os
from pathlib import Path
from glob import glob
import general_script_utility_functions as script_util


parser = argparse.ArgumentParser()
parser.add_argument("--settlementcountdir", type=str)
parser.add_argument("--yearfirst", type=int)
parser.add_argument("--yearlast", type=int)
parser.add_argument("--pldfirstday", type=int)
parser.add_argument("--pldlastday", type=int)
args = parser.parse_args()

settlement_count_dir = args.settlementcountdir
year_first = args.yearfirst
year_last = args.yearlast
pld_first_day = args.pldfirstday
pld_last_day = args.pldlastday


'''
# Testing with hardcoded inputs
connectivity_data_dir = "/home/blaughli/parcels/processing/p_production/z_binned_preconnectivty_data/binned_data_oldPolygonsNoPete_v1"
year_first = 1999
year_last = 1999
pld_first_day = 1
pld_last_day = 5
'''

output_csv_dir_stem = "z_connectivity_csv_files_withSeasons"
output_csv_dir = os.path.join(settlement_count_dir,output_csv_dir_stem)
Path(output_csv_dir).mkdir(parents=True, exist_ok=True)


file_list_all_years = sorted(script_util.find_files_os_walk(settlement_count_dir, ".npz"))

# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# THIS IS WHERE THINGS GET UGLY WITHOUT HAVING FULL DATES IN THE OUTPUT FILENAME STEMS
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# Select for chosen years
file_list_chosen_years = []
for filename in file_list_all_years:
    if int(filename.split("/")[-4].split("_")[-1]) >= year_first and int(filename.split("/")[-4].split("_")[-1]) <= year_last:
        file_list_chosen_years.append(filename)
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# Select for chosen PLD
file_list = []
for filename in file_list_chosen_years:
    if int(Path(filename).stem.split("_")[-2]) == pld_first_day and int(Path(filename).stem.split("_")[-1]) == pld_last_day:
        file_list.append(filename)
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------





# Prepare the lists of pre-normalization pre-pdfs (ie the arrays for the summed binned data that we're loading), and the release count array list
####################################
# FIX IN PRODUCTION
####################################
num_connectivity_pdfs = 5 # 5 total pdfs to calculate; 1-4 are the seasons (Winter - Fall), 5 is the annual/overall)
####################################
####################################
connectivity_pdf_list = []
polygon_release_counts_list = []
polygon_settlement_counts_list = []
with np.load(file_list[0]) as d:
    polygon_settlement_counts = d['polygon_settlement_counts']
    #polygon_settlement_counts = d['binned_connectivity_data']
    polygon_release_counts = d['polygon_release_counts']
    for i_season in range(num_connectivity_pdfs):
        polygon_settlement_counts_list.append(np.zeros_like(polygon_settlement_counts))
        polygon_release_counts_list.append(np.zeros_like(polygon_release_counts))
        connectivity_pdf_list.append(np.zeros_like(polygon_settlement_counts))
        
# List of lists of starting and ending month numbers for the seasons, winter-fall
seasonal_months_list = [[1, 3], [4, 6], [7, 9], [10, 12]]
#seasonal_months_list = [[12, 2], [3, 5], [6,8], [9, 11]]

file_counter = 0
for connectivity_data_file in file_list:
    
    file_counter += 1
    print(f"file {file_counter:>3}/{len(file_list)}")
    
    with np.load(connectivity_data_file) as d:
        #polygon_settlement_counts = d['binned_connectivity_data']
        polygon_settlement_counts = d['polygon_settlement_counts']
        polygon_release_counts = d['polygon_release_counts']
        
        # First, add to the "annual" pdf, which is the last (5th) element of the connectivity pdf and release counts lists
        polygon_settlement_counts_list[4] += polygon_settlement_counts
        #connectivity_pdf_list[4] += binned_connectivity_data
        polygon_release_counts_list[4] += polygon_release_counts
   
        # Now loop over the seasons, and modify the appropriate elemnts of the data lists
        for season_index in range(len(seasonal_months_list)):

            file_month = int(connectivity_data_file.split("month_")[-1].split("/")[0])
           
            if file_month >= seasonal_months_list[season_index][0] and file_month <= seasonal_months_list[season_index][1]:
                polygon_settlement_counts_list[season_index] += polygon_settlement_counts
                #connectivity_pdf_list[season_index] += binned_connectivity_data
                polygon_release_counts_list[season_index] += polygon_release_counts
                break # stop searching when season is found


# Now, compute settlement statistics
settle_strength_by_season_list = []
settle_count_by_season_list = []

for pdf_index in range(len(connectivity_pdf_list)):
    # First, calculate settle counts and strengths (before normalizing the pdf arrays!!!)
    settle_strength_by_season_list.append(np.sum(connectivity_pdf_list[pdf_index])/np.sum(polygon_release_counts_list[pdf_index]))
    settle_count_by_season_list.append(int(np.sum(connectivity_pdf_list[pdf_index])))
    # Normalize by number of releases (ie convert to pdfs)
    connectivity_pdf_list[pdf_index] = polygon_settlement_counts_list[pdf_index] / polygon_release_counts_list[pdf_index][:, np.newaxis] 
    #connectivity_pdf_list[pdf_index] = connectivity_pdf_list[pdf_index] / polygon_release_counts_list[pdf_index][:, np.newaxis] 




# Save the connectivity data to a csv file
####################################
# FIX IN PRODUCTION
####################################
seasonal_output_filename_labels = ["Jan-Mar","Apr-Jun","Jul_Sep","Oct-Dec", "Jan-Dec"]
#seasonal_output_filename_labels = ["Dec-Feb","Mar-May","Jun-Aug","Sep-Nov", "Jan-Dec"]

for pdf_index in range(num_connectivity_pdfs):
    csv_filename_conn = f"connectivity_values_years_{year_first}_{year_last}_PLD_{pld_first_day:03d}_{pld_last_day:03d}_season_{seasonal_output_filename_labels[pdf_index]}.csv"
    csv_conn_path = os.path.join(output_csv_dir,csv_filename_conn)
    np.savetxt(csv_conn_path,connectivity_pdf_list[pdf_index],delimiter=',',fmt='%1.8e')
    
    csv_filename_settlement_counts = f"settlement_counts_years_{year_first}_{year_last}_PLD_{pld_first_day:03d}_{pld_last_day:03d}_season_{seasonal_output_filename_labels[pdf_index]}.csv"
    csv_settlement_path = os.path.join(output_csv_dir,csv_filename_settlement_counts)
    np.savetxt(csv_settlement_path,polygon_settlement_counts_list[pdf_index],delimiter=',',fmt='%1.8e')
    
    csv_filename_release_counts = f"release_counts_years_{year_first}_{year_last}_PLD_{pld_first_day:03d}_{pld_last_day:03d}_season_{seasonal_output_filename_labels[pdf_index]}.csv"
    csv_release_count_path = os.path.join(output_csv_dir,csv_filename_release_counts)
    np.savetxt(csv_release_count_path,polygon_release_counts_list[pdf_index],delimiter=',',fmt='%1.8e')

    txt_filename_settle_count = f"settle_count_years_{year_first}_{year_last}_PLD_{pld_first_day:03d}_{pld_last_day:03d}_season_{seasonal_output_filename_labels[pdf_index]}.txt"
    txt_settle_count_path = os.path.join(output_csv_dir,txt_filename_settle_count)
    with open(txt_settle_count_path, "w") as file:
        file.write(f"{settle_count_by_season_list[pdf_index]}")

    txt_filename_settle_strength = f"settle_strength_years_{year_first}_{year_last}_PLD_{pld_first_day:03d}_{pld_last_day:03d}_season_{seasonal_output_filename_labels[pdf_index]}.txt"
    txt_settle_strength_path = os.path.join(output_csv_dir,txt_filename_settle_strength)
    with open(txt_settle_strength_path, "w") as file:
        file.write(f"{settle_strength_by_season_list[pdf_index]}")




