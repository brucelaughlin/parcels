#!/bin/bash

# Pete's years:  1993-1996, 1997-1998, 1999- 2005, 2005-2012, 2013-2017, 2018- 2024

#modelFilesDir=$1
firstYear=$1
lastYear=$2
numNodes=$3
#dtCalcMins=$3
#dtOutMins=$4

# Determine number of model files in input directory
#numFiles=$(find $modelFilesDir -name *.nc | wc -l)

# For now, we're just using the WCR30 25 year run.  So use years to distinguish different runs
numFiles=$(( lastYear - firstYear + 1 ))

# Location of THIS script (thanks SO)
callingDir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

#dirBaseName=$(basename "$modelFilesDir")
#dirStem="${dirBaseName%.*}"
#logDirGeneral="${callingDir}/v_logs__runDir_${dirStem}/"

logDirGeneral="${callingDir}/v_logs__${firstYear}_${lastYear}/"
mkdir -p "$logDirGeneral"

serialSize=$(( ($numFiles+$numNodes-1)/$numNodes ))
# Store the number of nodes that we'll use <serialSize> times (the rest we'll use <serialSize-1> times).  In the above diagram, 2/3 nodes
# get used <serialSize> (ie three) times, so <numNodesAtMaxSerial>=2 in this case.
# (I worked this math out on scratch paper and need to explain it better in future documentation)
numNodesAtMaxSerial=$(( $numNodes*(1-$serialSize)+$numFiles ))

extraArgs=""
counterRun=0
counterNode=0

for i_file in $(seq 0 $(($numFiles-1)));
do

    (( counterRun ++ ))

    currentYear=$(( firstYear + i_file ))

    # For testing, maybe use extraArgs="--afterok", which will kill the whole job if something fails.
    # For production, use "--afterany", so that if a single job fails, we can run it again using the associated config file

    #echo "$i_file"

    jobNum=$(sbatch --parsable --export="ALL,callingDir=$callingDir,currentYear=$currentYear,modelFilesDir=$modelFilesDir,logDirGeneral=$logDirGeneral" $extraArgs /home/blaughli/parcels/t_testing/cae/sbatch_parcels.bash)
    
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

done




