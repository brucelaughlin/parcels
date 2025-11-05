#!/bin/bash

# DID PETE ALSO WANT INDIVIDUAL YEARS?  SEE HIS EMAIL... I WAS A BIT CONFUSED BY THE WORDING

#connectivityDataDir=$1
connectivityDataDir="/home/blaughli/parcels/processing/p_production/z_binned_preconnectivty_data/binned_data_oldPolygonsNoPete_v1"

yearsStart=(1999 1999 2005 2013 2018)
yearsEnd=(2024 2005 2012 2017 2024)
#yearsStart=(1999)
#yearsEnd=(2000)

pldStartDays=(1 5 10 15 30 45 60 75 90 120 150)
pldEndDays=(5 10 15 30 45 60 75 90 120 150 180)

numCores=20
counter=0

for yearIndex in "${!yearsStart[@]}"
do
    for pldIndex in "${!pldStartDays[@]}"
        do
            ((counter ++))

            python /home/blaughli/parcels/processing/c_produce_conn_csvs/calculate_connectivity_single_pld_select_years_seasons_save_csv.py --connectivydatadir "$connectivityDataDir" --yearfirst "${yearsStart[$yearIndex]}" --yearlast "${yearsEnd[$yearIndex]}" --pldfirstday "${pldStartDays[$pldIndex]}" --pldlastday "${pldEndDays[$pldIndex]}" &

            if [[ $counter == $numCores ]]; then
                counter=0
                wait
            fi

    done
done

