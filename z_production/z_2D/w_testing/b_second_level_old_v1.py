#!/bin/bash

#SBATCH --job-name parcels
#SBATCH --mail-type=ALL
#SBATCH --mail-user=blaughli@ucsc.edu

cd "$callingDir"

logFilePrefix=$(basename $modelFilesDir)

logDir="v_logs/logs_${logFilePrefix}"
mkdir -p $logDir

fileNameListPre=($modelFilesDir/*)

fileNameList=( $(printf "%s\n" "${fileNameListPre[@]}" | sort ) )

for i_file in $(seq $(($firstFileIndex)) $(($firstFileIndex + $numFilesPerNode - 1)));
do

    logFile="${logDir}/$(basename ${fileNameList[$i_file]%.*}).log"

    # make sure that the output file made by python script uses "i_file" in its name creation, to avoid overwriting

    echo "b_level" >> $logFile
    echo $(basename ${fileNameList[$i_file]%.*}) >> $logFile
    echo $callingDir >> $logFile

    python u_test_python.py --modelfilesdir $modelFilesDir --fileindex $i_file &>> "$logFile" 2>&1 &
    #python u_test_python_simple.py --modelFilesDir $ModelFilesDir --fileIndex $i_file &>> "$logFile" 2>&1 &
    
    
done
