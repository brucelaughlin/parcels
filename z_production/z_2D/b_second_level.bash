#!/bin/bash

#SBATCH --job-name parcels
#SBATCH --mail-type=ALL
#SBATCH --mail-user=blaughli@ucsc.edu

cd "$callingDir"

fileIndexPrint=$(printf "%02d" "$fileIndex")

stdOutFilePre="stdout_production_mercator_v1__${fileIndexPrint}.log"
errOutFilePre="errout_production_mercator_v1__${fileIndexPrint}.log"

logDirGeneral="${callingDir}/v_logs/"

mkdir -p "$logDirGeneral"

stdOutFile="${logDirGeneral}${stdOutFilePre}"
errOutFile="${logDirGeneral}${errOutFilePre}"

echo "$fileIndexPrint" >> $stdOutFile


mpirun -np 24 -outfile-pattern "$stdOutFile" -errfile-pattern "$errOutFile" python /home/blaughli/parcels/z_production/z_2D/parcels_run_production_mpi_v2.py --modelfilesdir "$modelFilesDir" --fileindex "$fileIndex" 
#mpirun -np 24 -outfile-pattern "$stdOutFile" -errfile-pattern "$errOutFile" python /home/blaughli/parcels/z_production/z_2D/parcels_run_production_mpi_v1.py --modelfilesdir "$modelFilesDir" --fileindex "$fileIndex" 
#mpirun -np 22 -outfile-pattern "$stdOutFile" -errfile-pattern "$errOutFile" python /home/blaughli/parcels/z_production/z_2D/parcels_run_production_mpi_v1.py --modelfilesdir "$modelFilesDir" --fileindex "$fileIndex" 



