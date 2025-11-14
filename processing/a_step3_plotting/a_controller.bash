#!/bin/bash

connectivityDataDir=$1
#connectivityDataDir="/home/blaughli/parcels/processing/p_production/z_binned_preconnectivty_data/binned_data_oldPolygonsNoPete_v1/z_connectivity_csv_files_withSeasons/"

extensionCSV="csv"

connectivityFilePrefix="connectivity_data"
connectivityFiles=( "$connectivityDataDir$connectivityFilePrefix"*."$extensionCSV" )

numFiles=${#connectivityFiles[@]}

numCores=24

counter=0
overallCounter=0

for connectivityFile in "${connectivityFiles[@]}"
do

    ((counter ++))
    ((overallCounter ++))

    echo "$overallCounter / $numFiles"

    python /home/blaughli/parcels/processing/u_plotting/plot_connectivity_from_csv.py --csvconnectivityfile "$connectivityFile" &

    if [[ $counter == $numCores ]]; then
        counter=0
        wait
    fi
done


