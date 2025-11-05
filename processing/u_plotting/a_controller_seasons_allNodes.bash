#!/bin/bash

#connectivityDataDir=$1
connectivityDataDir="/home/blaughli/parcels/processing/p_production/z_binned_preconnectivty_data/binned_data_oldPolygonsNoPete_v1/z_connectivity_csv_files_withSeasons/"

extensionCSV="csv"
#connectivityFiles=( "$connectivityDataDir"/*."$extension" )

connectivityFilePrefix="connectivity_data"
connectivityFiles=( "$connectivityDataDir$connectivityFilePrefix"*."$extensionCSV" )

#releaseCountFilePrefix="release_counts"
#releaseCountFiles=( "$connectivityDataDir$releaseCountFilePrefix"*."$extensionCSV" )

#for fileIndex in "${!connectivityFiles[@]}"

numFiles=${#connectivityFiles[@]}

numNodes=20
counter=0
overallCounter=0

for connectivityFile in "${connectivityFiles[@]}"
do

    ((counter ++))
    ((overallCounter ++))

    echo "$overallCounter / $numFiles"

    #connectivityFile="${connectivityFiles[$fileIndex]}"
    #releaseCountFile="${releaseCountFiles[$fileIndex]}"

    #echo "$connectivityFile"

    python /home/blaughli/parcels/processing/u_plotting/plot_connectivity_from_csv.py --csvconnectivityfile "$connectivityFile" &
    #python /home/blaughli/parcels/processing/u_plotting/plot_connectivity_from_csv.py --csvconnectivityfile "$connectivityFile"

    if [[ $counter == $numNodes ]]; then
        counter=0
        wait
    fi
done


