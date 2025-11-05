#!/bin/bash

jobFile=$1
numNodes=$2

# Just hardcoded for now... would we ever want to use fewer than the total number of cores on a compute node?
#numCores=12
numCores=24

# Location of THIS script (thanks SO)
callingDir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )


# Determine number of connectivity jobs to process
# Note: The first time I tried this, $(cat $jobFile | wc -l) was one less than the number of lines in the file.  So, I manually added an extra line.  Now, that isn't happening.  So I feel a bit nervous
#numLines=$({ cat $jobFile; echo ''; } | wc -l)  
numLines=$(cat $jobFile | wc -l)

# Number of batch jobs that will be submitted
numJobs=$(( ($numLines+$numCores-1)/$numCores ))

serialSize=$(( ($numJobs+$numNodes-1)/$numNodes ))

# Store the number of nodes that we'll use <serialSize> times (the rest we'll use <serialSize-1> times).  In the above diagram, 2/3 nodes
# get used <serialSize> (ie three) times, so <numNodesAtMaxSerial>=2 in this case.
# (I worked this math out on scratch paper and need to explain it better in future documentation)
numNodesAtMaxSerial=$(( $numNodes*(1-$serialSize)+$numJobs ))

extraArgs=""
counterRun=0
counterNode=0

for firstLineNumberBatch in $(seq 1 $numCores $(($numLines)));
do

    (( counterRun ++ ))

    jobNum=$(sbatch --parsable --export="ALL,callingDir=$callingDir,numCores=$numCores,jobFile=$jobFile,firstLineNumberBatch=$firstLineNumberBatch" $extraArgs /home/blaughli/parcels/processing/p_production/p_delete_near_boundaries/sbatch_connectivity_dnb.bash)

    
    # For testing, maybe use extraArgs="--afterok", which will kill the whole job if something fails.
    # For production, use "--afterany", so that if a single job fails, we can run it again using the associated config file

    extraArgs="-d afterany:$jobNum"
    #extraArgs="-d afterok:$jobNum"

    if [[ $counterRun == $serialSize ]]; then
        counterRun=0
        extraArgs=""
        (( counterNode ++ ))
        if [[ $counterNode == $numNodesAtMaxSerial ]]; then
            (( serialSize -- ))
        fi
    fi

done


