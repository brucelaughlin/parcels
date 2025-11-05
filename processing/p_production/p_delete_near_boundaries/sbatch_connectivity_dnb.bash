#!/bin/bash

#SBATCH --job-name dnbconn
#SBATCH --mail-type=ALL
#SBATCH --mail-user=blaughli@ucsc.edu

# ------------------------------------------------------------------------------------------------------------------------------------
# SHOULD NOT BE HARDCODED!!!! 
# ------------------------------------------------------------------------------------------------------------------------------------
#version="oldPolygonsNoPete_deleteNearBoundaries_v1"
version="polygons_ROMS_ParentCellsOnly_WGS84_deleteNearBoundaries_v1"
#version="polygons_singleCellsIncludingPeteSeeds_deleteNearBoundaries_v2"
# ------------------------------------------------------------------------------------------------------------------------------------
#polygonFile="/home/blaughli/parcels/general_code/polygons_and_seeding/z_input_files/bounding_boxes_lonlat_WCR30_singleCoastalCells.txt"
polygonFile="/home/blaughli/parcels/general_code/polygons_and_seeding/z_output/ROMS_ParentCellsOnly_WGS84.txt"
#polygonFile="/home/blaughli/parcels/general_code/polygons_and_seeding/z_output/bounding_boxes_lonlat_WCR30_withPeteAdditions_romsGridCellCentroidsOnly.txt"
# ------------------------------------------------------------------------------------------------------------------------------------
gridFile="/home/blaughli/tracking_project_v2/grid_data/wcr30test1_grd.nc"
# ------------------------------------------------------------------------------------------------------------------------------------


# ------------------------------------------------------------------------------------------------------------------------------------
# Should be able to pass PLD list as a variable.  But, for now, hardcode
pldStartDays=(1 5 10 15 30 45 60 75 90 120 150)
pldEndDays=(5 10 15 30 45 60 75 90 120 150 180)
# ------------------------------------------------------------------------------------------------------------------------------------

cd "$callingDir"

# Using "wait" after each inner loop iteration, to try to make sure we don't add more jobs to current node than there are cores
for coreIndex in $(seq 0 $((numCores - 1)));
do

    for pldIndex in "${!pldStartDays[@]}"
    do

        lineNumber=$(( firstLineNumberBatch + coreIndex ))
        trackingFile=$(sed -n "${lineNumber}p" "$jobFile")
        fileNameLength=${#trackingFile}

        # Hack to avoid passing empty strings to python script... Not supremely confident this will alway work, since I think I saw a strange low number at some point when I was expecting 0...
        if [[ $fileNameLength -gt 0 ]]
        then
            python /home/blaughli/parcels/processing/p_production/p_delete_near_boundaries/connectivity_single_file_deleteNearBoundaries.py --gridfile "$gridFile" --polygonfile "$polygonFile" --version "$version" --trackingfile "$trackingFile" --pldstartday "${pldStartDays[$pldIndex]}" --pldendday "${pldEndDays[$pldIndex]}" >> stdout.txt 2>> errout.txt &
        fi

    done
    wait

done
