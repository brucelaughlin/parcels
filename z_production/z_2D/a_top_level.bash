#!/bin/bash

modelFilesDir=$1
numNodes=$2

# Determine number of model files in input directory
numFiles=$(find $modelFilesDir -name *.nc | wc -l)

# Determine number of files in which TO SEED per node
numFilesPerNode=$(((numFiles + (numNodes - 1))/numNodes))


# Location of THIS script (thanks SO)
callingDir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

#echo $numFiles
#echo $numNodes
#echo $numFilesPerNode
#echo ""

serialSize=$(( ($numFiles+$numNodes-1)/$numNodes ))
# Store the number of nodes that we'll use <serialSize> times (the rest we'll use <serialSize-1> times).  In the above diagram, 2/3 nodes
# get used <serialSize> (ie three) times, so <numNodesAtMaxSerial>=2 in this case.
# (I worked this math out on scratch paper and need to explain it better in future documentation)
numNodesAtMaxSerial=$(( $numNodes*(1-$serialSize)+$numFiles ))


extraArgs=""
counterRun=0
counterNode=0



for i_file in $(seq 0 $(($numFiles-1)));
#for i_node in $(seq 0 $(($numNodes-1)));
do

    (( counterRun ++ ))

    #firstFileIndex=$(($i_node * $numFilesPerNode))


    # For testing, maybe use extraArgs="--afterok", which will kill the whole job if something fails.
    # For production, use "--afterany", so that if a single job fails, we can run it again using the associated config file

    #echo "$i_file"

    jobNum=$(sbatch --parsable --export="ALL,callingDir=$callingDir,fileIndex=$i_file,modelFilesDir=$modelFilesDir" $extraArgs /home/blaughli/parcels/z_production/z_2D/b_second_level.bash)
    
    
    
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




