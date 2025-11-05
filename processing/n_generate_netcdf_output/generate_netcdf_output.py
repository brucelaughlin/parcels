from pathlib import Path
import netCDF4
import argparse
import pandas as pd
import numpy as np
import os

# -----------------------------------------------------------------------------------------------
# Inputs
# -----------------------------------------------------------------------------------------------
'''
parser = argparse.ArgumentParser()
parser.add_argument("--csvconnectivityfile", type=str)
parser.add_argument("--polygonfilepath", type = str)
args = parser.parse_args()

csv_connectivity_file = args.csvconnectivityfile
polygon_file_path = args.polygonfilepath
'''

connectivity_data_directory="/home/blaughli/parcels/processing/p_production/z_binned_preconnectivty_data/binned_data_oldPolygonsNoPete_v1/z_connectivity_csv_files_withSeasons/"

####csv_connectivity_file = "/home/blaughli/parcels/processing/p_production/z_binned_preconnectivty_data/binned_data_oldPolygonsNoPete_v1/z_connectivity_csv_files_withSeasons/connectivity_data_years_2018_2024_PLD_150_180_season_Sep-Nov.csv"
polygon_file_path = "/home/blaughli/parcels/general_code/polygons_and_seeding/z_input_files/bounding_boxes_lonlat_WCR30_singleCoastalCells.txt"

#version = "ROMS_WCR30_v1_originalPolygonsWithoutPeteAdditions"
version = "ROMS_WCR30_v1_originalSingleCellPolygons_PeteReleaseLocations"

grid_path = "/home/blaughli/tracking_project_v2/grid_data/wcr30test1_grd.nc"
# -----------------------------------------------------------------------------------------------


output_dir = "/home/blaughli/parcels/processing/n_generate_netcdf_output/z_output"
Path(output_dir).mkdir(parents=True, exist_ok=True)


connectivity_file_prefix="connectivity_data"

csv_connectivity_files = []
for filename in os.listdir(connectivity_data_directory):
    if os.path.isfile(os.path.join(connectivity_data_directory,filename)) and connectivity_file_prefix in filename:
        csv_connectivity_files.append(os.path.join(connectivity_data_directory,filename))
       
csv_connectivity_files.sort()
num_connectivities = len(csv_connectivity_files)




years_strings = ["1999_2005", "2005_2012", "2013_2017", "2018_2024", "1999_2024"]
seasons_strings = ["Jan-Mar","Apr-Jun","Jul_Sep","Oct-Dec", "Jan-Dec"]
plds_strings = ["001_005", "005_010", "010_015", "015_030", "030_045", "045_060", "060_075", "075_090", "090_120", "120_150", "150_180"]

pld_array = np.zeros((len(plds_strings),2), dtype = int)

for i_pld in range(len(plds_strings)):
    pld_array[i_pld, 0] = int(plds_strings[i_pld].split("_")[0])
    pld_array[i_pld, 1] = int(plds_strings[i_pld].split("_")[1])




num_years_subsets = len(years_strings)
num_plds = len(plds_strings)
num_seasons = len(seasons_strings)

num_years_subsets_coord_var_array = np.arange(num_years_subsets)
num_plds_coord_var_array = np.arange(num_plds)
num_seasons_coord_var_array = np.arange(num_seasons)


# Determine constant information across all connnectivities

# Reading polygon vertex data
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

# Since we're writing to netCDF, need all polygon vertex arrays to have the same size, and then need to define dimensions which reflect this size (ie the maximum number of vertices in a polygon)
num_vertices_max = 0
for i_polygon in range(len(list_of_polygon_vertex_lonlat_lists)):
    if len(list_of_polygon_vertex_lonlat_lists[i_polygon]) > num_vertices_max:
        num_vertices_max = len(list_of_polygon_vertex_lonlat_lists[i_polygon])

data_polygon_vertices_lons = np.full((num_polygons, num_vertices_max), np.nan)
data_polygon_vertices_lats = np.full((num_polygons, num_vertices_max), np.nan)
for i_polygon in range(len(list_of_polygon_vertex_lonlat_lists)):
    data_polygon_vertices_lons[i_polygon,:len(list_of_polygon_vertex_lonlat_lists[i_polygon])] = list_of_polygon_vertex_lonlat_lists[i_polygon][:,0]
    data_polygon_vertices_lats[i_polygon,:len(list_of_polygon_vertex_lonlat_lists[i_polygon])] = list_of_polygon_vertex_lonlat_lists[i_polygon][:,1]

#num_connectivities_coord_var_array = np.arange(num_connectivities)
num_polygons_coord_var_array = np.arange(num_polygons)
num_vertices_coord_var_array = np.arange(num_vertices_max)
num_plds_coord_var_array = np.arange(num_plds)
num_one_coord_var_array = np.array([1])
num_two_coord_var_array = np.arange(2)


# Initialize the arrays to be stored, and then re-initialize later...
data_connectivity_all_plds = np.zeros((num_polygons, num_polygons, num_plds))
data_release_counts = np.zeros(num_polygons)
data_settle_counts_all_plds = np.zeros(num_plds)
data_settle_strengths_all_plds = np.zeros(num_plds)
pld_counter = 0


for years_string in years_strings:
    print(years_string)
    for season_string in seasons_strings:
        print(season_string)
        output_file = f"connectivity_data__{version}__years_{years_string}__season_{season_string}.nc"
        output_file_path = os.path.join(output_dir,output_file)
        for pld_string in plds_strings:
            print(pld_string)
            for csv_connectivity_file in csv_connectivity_files:
                if years_string in csv_connectivity_file:
                    if season_string in csv_connectivity_file:
                        if pld_string in csv_connectivity_file:

                            input_filename_universal_pieces = csv_connectivity_file.split("connectivity_data")
                            csv_release_count_file = f"{input_filename_universal_pieces[0]}release_counts{input_filename_universal_pieces[-1]}"
                            txt_settle_count_file = f"{input_filename_universal_pieces[0]}settle_count{input_filename_universal_pieces[-1]}"
                            txt_settle_count_file = f"{txt_settle_count_file.split(".")[0]}.txt"
                            txt_settle_strength_file = f"{input_filename_universal_pieces[0]}settle_strength{input_filename_universal_pieces[-1]}"
                            txt_settle_strength_file = f"{txt_settle_strength_file.split(".")[0]}.txt"

                            pld_index = plds_strings.index(pld_string)
                            pld_counter += 1
                
                            # File reading >>> ----------------------------------------------------------------------
                            df_connectivity = pd.read_csv(csv_connectivity_file, header=None)
                            data_connectivity_all_plds[:,:,pld_index] = df_connectivity.values

                            if pld_index == 0:
                                df_release_count = pd.read_csv(csv_release_count_file, header=None)
                                data_release_counts[:] = df_release_count.values[:,0]

                            with open(txt_settle_count_file, "r") as file:
                                settle_count_string = file.readline()
                                data_settle_counts_all_plds[pld_index] = int(settle_count_string.strip())

                            with open(txt_settle_strength_file, "r") as file:
                                settle_strength_string = file.readline()
                                data_settle_strengths_all_plds[pld_index] = float(settle_strength_string.strip())
                            # File reading <<< ----------------------------------------------------------------------

                            if pld_counter == len(plds_strings):
                                pld_counter = 0

                                with netCDF4.Dataset(output_file_path, 'w', format='NETCDF4') as nc_file:

                                    nc_file.createDimension('polygon_index', num_polygons)
                                    nc_file.createDimension('polygon_vertex_index', num_vertices_max)
                                    nc_file.createDimension('pld_index', num_plds)
                                    nc_file.createDimension('one', 1)
                                    nc_file.createDimension('two', 2)
                                    
                                    '''
                                    # coordinate variables
                                    polygon_index_var = nc_file.createVariable('polygon_index', 'i4', ('polygon_index'))
                                    vertex_index_var = nc_file.createVariable('polygon_vertex_index', 'i4', ('polygon_vertex_index'))
                                    pld_index_var = nc_file.createVariable('pld_index', 'i4', ('pld_index'))
                                    one_var = nc_file.createVariable('one', 'f4', ('one'))
                                    two_var = nc_file.createVariable('two', 'f4', ('two'))
                                    '''

                                    # data variables
                                    polygon_vertex_lons_var = nc_file.createVariable('polygon_vertex_lons', 'f4', ('polygon_index', 'polygon_vertex_index'))
                                    polygon_vertex_lats_var = nc_file.createVariable('polygon_vertex_lats', 'f4', ('polygon_index', 'polygon_vertex_index'))
                                    pld_days_var = nc_file.createVariable('pld_days', 'i4', ('pld_index', 'two'))
                                    connectivity_var = nc_file.createVariable('connectivity', 'f4', ('polygon_index','polygon_index','pld_index'))
                                    settlement_count_var = nc_file.createVariable('settlement_counts', 'f4', ('polygon_index','polygon_index','pld_index'))
                                    release_count_var = nc_file.createVariable('release_counts', 'i4', ('polygon_index'))
                                    #settlement_count_overall_var = nc_file.createVariable('settlement_count_overall', 'i4', ('pld_index'))
                                    #settle_strength_overall__var = nc_file.createVariable('settlement_strength_overall', 'f4', ('pld_index'))

                                    # Attributes
                                    #nc_file.description = f'Connectivity and supplementary data for all PLDS, years: {years_string}, season: {season_string}.  Created: .  Note: These connectivities are slightly flawed, a new version is forthcoming'
                                    nc_file.description = f'Connectivity and supplementary data for all PLDS for a given release season within a given subset of years'
                                    nc_file.years = f'{years_string}'
                                    nc_file.season = f'{season_string}'
                                    nc_file.tracking_model = f"Tracking done using OceanParcels v3.1.4.  Kernels: <AgeAndTidalKick, DepthAdjustmentAndLandmask>.  Date of tracking run: 20251003 - 20251021"
                                    
                                    nc_file.circulation_model = "ROMS on WCR30 grid, forced by ERA5 atmospheric forcing with GLORYS lateral boundary conditions. Date of model run: February 2025"
                                    nc_file.grid_path = f"{grid_path}"
                                    nc_file.note = 'Note: These connectivities are flawed and not final, a new version is forthcoming'

                                    polygon_vertex_lons_var.long_name = 'Polygon vertex longitudes; first dimension indexes polygon number, second dimension indexes vertex number for a given polygon.'
                                    polygon_vertex_lats_var.long_name = 'Polygon vertex latitudes; first dimension indexes polygon number, second dimension indexes vertex number for a given polygon.'
                                    pld_days_var.long_name = "PLD starting and ending days; first dimension indexes PLD number, second dimension (0 or 1) indexes (starting or ending) day of a given PLD."
                                    #pld_days_var.long_name = "PLD starting and ending days; first dimension indexes PLD number, second dimension indexes starting (0) or ending (1) day of a given PLD."
                                    connectivity_var.long_name = "Matrices of connectivity probability values.  For a given PLD, the value in row i, column j is the number of particles released from polygon i which settled in polygon j, divided by the total number of particles released from polygon i.  First dimension indexes release cell, second dimension indexes settlement cell, third dimension indexes PLD."
                                    settlement_count_var.long_name = "Matrices of settlement counts.  For a given PLD, the value in row i, column j is the number of particles released from polygon i which settled in polygon j.  First dimension indexes release cell, second dimension indexes settlement cell, third dimension indexes PLD."
                                    #"Matrix of settlement counts.  First dimension indexes release cell, second dimension indexes settlement cell, third dimension indexes PLD"
                                    release_count_var.long_name = "Number of particles released from a given cell."
                                    #settlement_count_overall_var.long_name = "Overall number of settlers in a given PLD"
                                    #settlement_strength_overall_var.long_name = "Overall settlement_strength in given PLD"
                    

                                    # Write data   
                                    
                                    '''
                                    polygon_index_var[:] = num_polygons_coord_var_array
                                    vertex_index_var[:] = num_vertices_coord_var_array
                                    pld_index_var[:] = num_plds_coord_var_array
                                    one_var[:] = num_one_coord_var_array
                                    two_var[:] = num_two_coord_var_array
                                    '''

                                    polygon_vertex_lons_var[:] = data_polygon_vertices_lons
                                    polygon_vertex_lats_var[:] = data_polygon_vertices_lats
                                    pld_days_var[:] = pld_array
                                    connectivity_var[:] = data_connectivity_all_plds
                                    #connectivity_var[:] = data_connectivity_all_plds
                                    release_count_var[:] = data_release_counts
                                    #settle_count_var[:] = data_settle_counts_all_plds
                                    #settle_strength_var[:] = data_settle_strengths_all_plds

                                # Initialize the arrays to be stored, and then re-initialize later...
                                data_connectivity_all_plds = np.zeros((num_polygons, num_polygons, num_plds))
                                data_release_counts = np.zeros(num_polygons)
                                data_settle_counts_all_plds = np.zeros(num_plds)
                                data_settle_strengths_all_plds = np.zeros(num_plds)

