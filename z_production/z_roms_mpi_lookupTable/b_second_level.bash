#!/bin/bash

#SBATCH --job-name parcels
#SBATCH --mail-type=ALL
#SBATCH --mail-user=blaughli@ucsc.edu

numCores=24

cd "$callingDir"

fileIndexPrint=$(printf "%02d" "$fileIndex")
dtCalcMinsPrint=$(printf "%02d" "$dtCalcMins")
dtOutMinsPrint=$(printf "%02d" "$dtOutMins")

seedPeriodIndexPrint=$(printf "%02d" "$seedPeriodIndex")

#initialSeedDayIndexCurrentRun
#currentSeedPeriodLength

stdOutFilePre="stdout__fileIndex_${fileIndexPrint}__seedIndex_${seedPeriodIndexPrint}.log"
errOutFilePre="errout__fileIndex_${fileIndexPrint}__seedIndex_${seedPeriodIndexPrint}.log"
stdOutFile="${logDirGeneral}${stdOutFilePre}"
errOutFile="${logDirGeneral}${errOutFilePre}"

#argumentString='--modelfilesdir "$modelFilesDir" --fileindex "$fileIndex" --dtcalcmins "$dtCalcMins" --dtoutmins "$dtOutMins" --particlelifetimedays "$particleLifetimeDays" --seedperiodindex "$seedPeriodIndex"\ 
#--currentyear "$currentYear" --initialseeddayindexcurrentrun "$initialSeedDayIndexCurrentRun" --currentseedperiodlength "$currentSeedPeriodLength" --outputdirgeneral "$outputDirGeneral"'
##mpirun -np 24 -outfile-pattern "$stdOutFile" -errfile-pattern "$errOutFile" python /home/blaughli/parcels/z_production/z_roms_mpi_shorterSeedPeriod/parcels_run_production_mpi_v2.py "$argumentString"



mpirun -np 24 -outfile-pattern "$stdOutFile" -errfile-pattern "$errOutFile" python /home/blaughli/parcels/z_production/z_roms_mpi/parcels_run_production_mpi.py --modelfilesdir "$modelFilesDir" --fileindex "$fileIndex" --dtcalcmins "$dtCalcMins" --dtoutmins "$dtOutMins" --particlelifetimedays "$particleLifetimeDays" --seedperiodindex "$seedPeriodIndex" --currentyear "$currentYear" --initialseeddayindexcurrentrun "$initialSeedDayIndexCurrentRun" --currentseedperiodlength "$currentSeedPeriodLength" --outputdirgeneral "$outputDirGeneral"



