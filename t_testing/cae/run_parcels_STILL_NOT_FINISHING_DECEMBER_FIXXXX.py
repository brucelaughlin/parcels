
import time
import os
import math
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from netCDF4 import Dataset
import pickle
from glob import glob
import argparse
from scipy.interpolate import griddata

import parcels_custom_util as parcels_util
import parcels_one_release as parcels_one_release

# Pete's years:  1993-1996, 1997-1998, 1999- 2005, 2005-2012, 2013-2017, 2018- 2024

parser = argparse.ArgumentParser()
parser.add_argument("--currentyear", type=int)
parser.add_argument("--numcores", type=int)
parser.add_argument("--coreindex", type=int)

args = parser.parse_args()

currentyear = args.currentyear
num_cores = args.numcores
core_index = args.coreindex


# Hardwired seed day interval
seed_day_interval = 2

# Get number of days in current year
day_1 = datetime(current_year,1,1)
day_1_nextYear = datetime(current_year+1,1,1)
n_days_in_year = int((day_1_nextYear - day_1).days)

# Want to use all nodes; using "ceil" doesn't always accomplish this.  
# So, use "floor", and then add 1 extra seed day for each core until all "remainder days" are accounted for
n_days_per_core_base = int(np.floor(n_days_in_year/num_cores))

# Calculate the number of "extra" seed days that the "floor" division above does not account for in the current year
n_days_remainder = n_days_in_year - (num_cores * n_days_per_core_base)

# Start a tally of covered days, for use in determining start/end day of current seed window
day_tally = 0

n_days_per_core = n_days_per_core_base

# If <core_index> is less than <n_days_remainder>, add 1 to <n_days_per_core> and modify <day_tally> correspondingly.  Else, subtract 1 from <n_days_per_core> (these increments
# ensure that we have one extra seed time for the "remainder days", AND that we don't incur a 1-off error after those days (I wrestled with this for a little while in testing))
if core_index <= n_days_remainder:
    day_tally += (n_days_per_core_base + 1) * (core_index - 1)
    n_days_per_core += 1 
else:
    n_days_per_core -= 1
    day_tally += (n_days_per_core_base + 1) * (n_days_remainder) + (n_days_per_core_base -1 ) * ((core_index - 1) - n_days_remainder)

# Determine seeding start and end day of the year for this core
start_day = day_tally + 1
end_day = min(day_tally + n_days_per_core, n_days_in_year)

day_tally += n_days_per_core

# Loop over year days of interest for this year
for year_day in range(start_day, end_day, seed_day_interval):
    seed_date = datetime(current_year,1,1) + timedelta(days = year_day - 1)
    parcels_one_release(seed_date)

