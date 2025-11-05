#!/bin/bash

#SBATCH --job-name carpels
#SBATCH --mail-type=ALL
#SBATCH --mail-user=blaughli@ucsc.edu

numCores=24

cd "$callingDir"

for coreIndex in $(seq 1 $((numCores)));
do
    coreIndexPrint=$(printf "%02d" "$coreIndex")
    stdOutFilePre="stdout__year_${currentYear}__coreIndex_${coreIndexPrint}.log"
    errOutFilePre="errout__year_${currentYear}__coreIndex_${coreIndexPrint}.log"
    stdOutFile="${logDirGeneral}${stdOutFilePre}"
    errOutFile="${logDirGeneral}${errOutFilePre}"

    echo "Model currentYear: ${currentYear}" >> $stdOutFile

    python /home/blaughli/parcels/t_testing/cae/run_parcels.py --currentyear "$currentYear" --numcores "$numCores" --coreindex "$coreIndex" > "$stdOutFile" 2> "$errOutFile" & 

done
wait


