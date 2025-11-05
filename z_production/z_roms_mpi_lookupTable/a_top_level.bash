#!/bin/bash

modelFilesDir=$1
numNodes=$2
dtCalcMins=$3
dtOutMins=$4
particleLifetimeDays=$5
seedPeriodDays=$6

# ---------------------------------------------------------------------
# Make ouput file directories

# Location of THIS script (thanks SO)
callingDir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

dtCalcMinsPrint=$(printf "%03d" "$dtCalcMins")
dtOutMinsPrint=$(printf "%03d" "$dtOutMins")
particleLifetimeDaysPrint=$(printf "%03d" "$particleLifetimeDays")
seedPeriodDaysPrint=$(printf "%03d" "$seedPeriodDays")
dir_base_name=$(basename "$modelFilesDir")
dir_stem="${dir_base_name%.*}"

logDirGeneral="${callingDir}/v_logs__modelDir_${dir_stem}__dtCalcMins_${dtCalcMinsPrint}__dtOutMins_${dtOutMinsPrint}__particleLifetimeDays_${particleLifetimeDaysPrint}__seedPeriodDays_${seedPeriodDaysPrint}/"
outputDirGeneral="${callingDir}/z_output__modelDir_${dir_stem}__dtCalcMins_${dtCalcMinsPrint}__dtOutMins_${dtOutMinsPrint}__particleLifetimeDays_${particleLifetimeDaysPrint}__seedPeriodDays_${seedPeriodDaysPrint}/"


mkdir -p "$logDirGeneral"
mkdir -p "$outputDirGeneral"
# ---------------------------------------------------------------------



#chunkSize=$3

# Determine number of model files in input directory
numFiles=$(find $modelFilesDir -name *.nc | wc -l)

# This might be too loose...
maxDaysPerFile=366
maxNumSeedPeriodsPerFile=$(( (maxDaysPerFile + (seedPeriodDays - 1))/seedPeriodDays ))

# Store the number of nodes that we'll use <serialSize> times (the rest we'll use <serialSize-1> times).
serialSize=$(((numFiles * maxNumSeedPeriodsPerFile + (numNodes - 1))/numNodes))
#numFilesPerNode=$(((numFiles + (numNodes - 1))/numNodes))


#echo $numFiles
#echo $numNodes
#echo $numFilesPerNode
#echo ""

###serialSize=$(( ($numFiles+$numNodes-1)/$numNodes )) # ceiling division



# (I worked this math out on scratch paper and need to explain it better in future documentation)
numNodesAtMaxSerial=$(( $numNodes*(1-$serialSize)+$numFiles ))


extraArgs=""
counterRun=0
counterNode=0



for fileIndex in $(seq 0 $(($numFiles-1)));
do

    #(( counterRun ++ ))

    # For testing, maybe use extraArgs="--afterok", which will kill the whole job if something fails.
    # For production, use "--afterany", so that if a single job fails, we can run it again using the associated config file

    #echo "$fileIndex"

    #numDaysToSeedCurrentYearFile=$(python /home/blaughli/parcels/general_code/run_utility/get_day_count_model_file.py --modelfilesdir "$modelFilesDir" --fileindex "$fileIndex")
    #numDaysToSeedCurrentYearFile=$(python /home/blaughli/parcels/general_code/run_utility/get_day_count_model_file_proMainFancyCool.py "$modelFilesDir" "$fileIndex")

    fileDateInfoString=$(python /home/blaughli/parcels/general_code/run_utility/get_day_count_model_file.py --modelfilesdir "$modelFilesDir" --fileindex "$fileIndex")


    read -r currentYear numDaysToSeedCurrentYearFile <<< "$fileDateInfoString"



    if [[ $fileIndex == $(($numFiles-1)) ]];
    then
        (( numDaysToSeedCurrentYearFile -= (particleLifetimeDays + 1) ))
    fi


    numSeedPeriodsCurrentFile=$(( numDaysToSeedCurrentYearFile/seedPeriodDays ))
    #extraDaysInLastSeedPeriod=$(( numDaysToSeedCurrentYearFile - numSeedPeriodsCurrentFile * seedPeriodDays ))
    daysInLastSeedPeriod=$(( numDaysToSeedCurrentYearFile - numSeedPeriodsCurrentFile * seedPeriodDays ))
   
#    echo "" 
#    echo "" 
#    echo "File Index: ${fileIndex}"
#    echo "$numDaysToSeedCurrentYearFile"
#    echo "$currentYear"
#    echo "$numSeedPeriodsCurrentFile"
#    echo "$extraDaysInLastSeedPeriod"
#    echo "Entering seed loop for current file"

    initialSeedDayIndexCurrentRun=$((0 - seedPeriodDays))


    for seedPeriodIndex in $(seq 0 $(($numSeedPeriodsCurrentFile)));
    #for seedPeriodIndex in $(seq 0 $(($numSeedPeriodsCurrentFile-1)));
    do
        
        (( counterRun ++ ))
        
        (( initialSeedDayIndexCurrentRun += seedPeriodDays ))
        
        currentSeedPeriodLength=$seedPeriodDays
        if [[ $seedPeriodIndex == $(($numSeedPeriodsCurrentFile)) ]];
        #if [[ $seedPeriodIndex == $(($numSeedPeriodsCurrentFile-1)) ]];
        then
            (( currentSeedPeriodLength = extraDaysInLastSeedPeriod ))
            #(( currentSeedPeriodLength += extraDaysInLastSeedPeriod ))
            #echo "Last seed day index: $numDaysToSeedCurrentYearFile"
        fi

#        echo "Seed Period Index: ${seedPeriodIndex}"
#        echo "$initialSeedDayIndexCurrentRun"
#        echo "$currentSeedPeriodLength"
#        echo


        if (( currentSeedPeriodLength > 0  ));
        then
            # How do I split this statement into multiple lines?????
            jobNum=$(sbatch --parsable --export="ALL,callingDir=$callingDir,fileIndex=$fileIndex,modelFilesDir=$modelFilesDir,dtCalcMins=$dtCalcMins,dtOutMins=$dtOutMins,currentYear=$currentYear,seedPeriodIndex=$seedPeriodIndex,initialSeedDayIndexCurrentRun=$initialSeedDayIndexCurrentRun,currentSeedPeriodLength=$currentSeedPeriodLength,logDirGeneral=$logDirGeneral,outputDirGeneral=$outputDirGeneral,particleLifetimeDays=$particleLifetimeDays" $extraArgs /home/blaughli/parcels/z_production/z_roms_mpi/b_second_level.bash)

            #extraArgs="-d afterany:$jobNum"
            extraArgs="-d afterok:$jobNum"

            if [[ $counterRun == $serialSize ]]; then
                counterRun=0
                extraArgs=""
                (( counterNode ++ ))
                if [[ $counterNode == $numNodesAtMaxSerial ]]; then
                    (( serialSize -- ))
                fi
            fi
        fi

    done
done




