#!/bin/bash

# DID PETE ALSO WANT INDIVIDUAL YEARS?  SEE HIS EMAIL... I WAS A BIT CONFUSED BY THE WORDING

configFile=$1

yearsStartFromPython=$(python /home/blaughli/parcels/processing/g_utility/print_yearsStart_fromConfig.py "$configFile")
yearsEndFromPython=$(python /home/blaughli/parcels/processing/g_utility/print_yearsEnd_fromConfig.py "$configFile")
pldStartDaysFromPython=$(python /home/blaughli/parcels/processing/g_utility/print_pldStartDays_fromConfig.py "$configFile")
pldEndDaysFromPython=$(python /home/blaughli/parcels/processing/g_utility/print_pldEndDays_fromConfig.py "$configFile")
numCores=$(python /home/blaughli/parcels/processing/g_utility/print_numCoresStep2_fromConfig.py "$configFile")

IFS=' ' read -r -a yearsStart <<< "$yearsStartFromPython"
IFS=' ' read -r -a yearsEnd <<< "$yearsEndFromPython"
IFS=' ' read -r -a pldStartDays <<< "$pldStartDaysFromPython"
IFS=' ' read -r -a pldEndDays <<< "$pldEndDaysFromPython"

counter=0

for yearIndex in "${!yearsStart[@]}"
do
    for pldIndex in "${!pldStartDays[@]}"
        do
            ((counter ++))

            python /home/blaughli/parcels/processing/a_step2_produce_connectivity_csv/calculate_connectivity_single_pld_select_years_seasons_save_csv.py --configfile "$configFile" --yearfirst "${yearsStart[$yearIndex]}" --yearlast "${yearsEnd[$yearIndex]}" --pldfirstday "${pldStartDays[$pldIndex]}" --pldlastday "${pldEndDays[$pldIndex]}" &

            if [[ $counter == $numCores ]]; then
                counter=0
                wait
            fi

    done
done

