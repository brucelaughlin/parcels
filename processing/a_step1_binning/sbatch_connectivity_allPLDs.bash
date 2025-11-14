#!/bin/bash

#SBATCH --job-name conn
#SBATCH --mail-type=ALL
#SBATCH --mail-user=blaughli@ucsc.edu

cd "$callingDir"

#numFilesPerNode=$(python /home/blaughli/parcels/processing/g_utility/print_numFilesPerNode_fromConfig.py "$configFile")

# Using "wait" after each inner loop iteration, to try to make sure we don't add more jobs to current node than there are cores
for fileIndex in $(seq 0 $((numFilesPerNode - 1)));
do
    lineNumber=$(( firstLineNumberBatch + fileIndex ))
    trackingFile=$(sed -n "${lineNumber}p" "$trackingOutputListFile")
    fileNameLength=${#trackingFile}

    trackingFileNumTimesteps=$(python /home/blaughli/parcels/processing/g_utility/print_trackingFileNumTimesteps_fromTrackingFile.py "$trackingFile")

    # Hack to avoid passing empty strings to python script... Not supremely confident this will alway work, since I think I saw a strange low number at some point when I was expecting 0...
    if [[ $fileNameLength -gt 0 ]]; then
    
        # Make sure we don't process unfinished files (This check added since Chris is doing some file juggling and we're not totally confident everything is good)
        if [[ $trackingFileNumTimesteps == $trackingFileNumTimestepsExpected ]]; then

            python /home/blaughli/parcels/processing/a_step1_binning/settlement_binning_single_file_allPLDs.py --configfile "$configFile" --trackingfile "$trackingFile" >> stdout.txt 2>> errout.txt &
            
        fi
    fi
done
wait
