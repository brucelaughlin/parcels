#!/bin/bash

#SBATCH --job-name conn
#SBATCH --mail-type=ALL
#SBATCH --mail-user=blaughli@ucsc.edu

cd "$callingDir"

# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# SHOULD NOT BE HARDCODED, FIX IMMEDIATELY
# ------------------------------------------------------------------------------------------------------------------------------------
polygonFile="/home/blaughli/parcels/general_code/polygons_and_seeding/z_input_files/bounding_boxes_lonlat_WCR30_singleCoastalCells.txt"
version="oldPolygonsNoPete_v1"
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# Should be able to pass PLD list as a variable.  But, for now, hardcode
pldStartDays=(1 5 10 15 30 45 60 75 90 120 150)
pldEndDays=(5 10 15 30 45 60 75 90 120 150 180)
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------


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
            python /home/blaughli/parcels/processing/p_production/connectivity_single_file.py --polygonfile "$polygonFile" --version "$version" --trackingfile "$trackingFile" --pldstartday "${pldStartDays[$pldIndex]}" --pldendday "${pldEndDays[$pldIndex]}" >> stdout.txt 2>> errout.txt &
        fi

    done
    wait

done
