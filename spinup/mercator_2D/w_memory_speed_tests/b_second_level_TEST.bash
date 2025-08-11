#!/bin/bash

#SBATCH --job-name parcels
#SBATCH --mail-type=ALL
#SBATCH --mail-user=blaughli@ucsc.edu

logFile=$1

#mpirun -np 20 python /home/blaughli/parcels/spinup/mercator_2D/w_memory_speed_tests/mem_speed_test_mpi.py &>> "$logFile" 2>&1 &
#mpirun -np 20 python /home/blaughli/parcels/spinup/mercator_2D/w_memory_speed_tests/mem_speed_test_mpi.py


mpirun -np 20 --output-filename $logFile python /home/blaughli/parcels/spinup/mercator_2D/w_memory_speed_tests/mem_speed_test_mpi.py
