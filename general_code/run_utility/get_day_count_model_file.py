from datetime import datetime, timedelta
from pathlib import Path
from glob import glob
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--modelfilesdir", type=str)
parser.add_argument("--fileindex", type=int)
#parser.add_argument("modelfilesdir", type=str)
#parser.add_argument("fileindex", type=int)
args = parser.parse_args()

dataset_folder = args.modelfilesdir
file_index = args.fileindex

dataset_folder_stem = Path(dataset_folder).stem

model_files = sorted(glob(f'{dataset_folder}/*.nc'))

num_files = len(model_files)

model_files = model_files[file_index:]

# This hacky methodology relies on the input symbolic links being named (year).nc, ie 1999.nc, 2000.nc, etc
year_0 = datetime(int(Path(model_files[0]).stem), 1, 1)
year_1 = datetime(int(Path(model_files[0]).stem) + 1, 1, 1)
year_delta = year_1 - year_0

day_count_model_file = int(year_delta.total_seconds()/86400)

#print(day_count_model_file)
#print(year_0.year)

print(f"{year_0.year} {day_count_model_file}")
