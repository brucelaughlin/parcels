#!/bin/bash

#SBATCH --job-name connCalc
#SBATCH --mail-type=ALL
#SBATCH --mail-user=blaughli@ucsc.edu

# NOTE:  REMOVE THE 95GB SLURM NODE COMMAND ABOVE WHEN IN PRODUCTION

#pdrakefileswitch=1
#pdrakefileswitch=0

loggerLevel="DEBUG"

#connJobFile=$1
#callingDir=$2
#logDir=$3

cd "$callingDir"

connJobFileTrim1="${connJobFile##*/}"
connJobFilePrefix="jobFile_"
connJobFileTrim2=${connJobFileTrim1#"$connJobFilePrefix"}
connJobFileNum="${connJobFileTrim2/.txt/}"

connDataDir="$(dirname "$connJobFile")"
logDir="$connDataDir/l_logs"

#mkdir -p "$logDir"
#
#if [ -d "$logDir" ]; then
#    if ! [ -z "$( ls -A $logDir )" ]; then
#        rm "$logDir"/*
#    fi
#fi

#echo "$logDir"
#echo "hi"

# --------
# temporary, for testing
#logFilePath="/home/blaughli/aa_log.txt"
# --------

IFS=

while read -r line; do
    #echo "$line"
   
    trackingFileTrim1="${line##*/}"
    trackingFileTrim2="${trackingFileTrim1/.nc/}"

    logFilePre="${trackingFileTrim2}.log"
    logFilePath="$logDir/$logFilePre"
    #echo "$logFile"
    
    #echo "File: $line" >> "$logFilePath"
   
    echo "pdrakefileswitch = $pdrakeFileSwitch" >> "$logFilePath"

    python /home/blaughli/tracking_project_v2/processing/settlement/y_parallel/y_production_simple/connectivity_calc_production.py --trackingfile "$line" --pdrakefileswitch "$pdrakeFileSwitch" --polygonfile "$polygonFile" --baseyear "$baseYear"  &>> "$logFilePath" &
    
    #python /home/blaughli/tracking_project_v2/processing/settlement/y_parallel/z_test/connectivity_histogram_calc_plds_seasons_recordDistance_test5.py --trackingfile $line --pdrakefileswitch $pdrakefileswitch --polygonfile $polygonFile  &>> "$logFilePath" &
    
    #python /home/blaughli/tracking_project_v2/processing/settlement/y_parallel/z_test/connectivity_histogram_calc_plds_seasons_nowAddPDrakeOption_test4.py --trackingfile $line --pdrakefileswitch $pdrakefileswitch --polygonfile $polygonFile  &>> "$logFilePath" &


done < "$connJobFile"

    

wait # I don't know why I was using "wait" here.  I think the "&" above is required to make the python calls run in parallel

