# Ask Paul which version of this makes more sense for this application


# This hacky methodology relies on the input symbolic links being named (year).nc, ie 1999.nc, 2000.nc, etc

# I tried to get fancy with the "main" function stuff, but this feels more error-prone than the argparse way with named arguments...


from datetime import datetime, timedelta
from pathlib import Path
from glob import glob
import sys


def count_days_in_model_file(dataset_folder, file_index):
    
    dataset_folder_stem = Path(dataset_folder).stem
    model_files = sorted(glob(f'{dataset_folder}/*.nc'))
    num_files = len(model_files)
    model_files = model_files[file_index:]

    year_0 = datetime(int(Path(model_files[0]).stem), 1, 1)
    year_1 = datetime(int(Path(model_files[0]).stem) + 1, 1, 1)
    year_delta = year_1 - year_0

    return(int(year_delta.total_seconds()/86400))

if __name__ == "__main__":
    if len(sys.argv) == 3:
        dataset_folder = sys.argv[1]
        file_index = int(sys.argv[2])
        
        day_count_model_file = count_days_in_model_file(dataset_folder,file_index)
        print(day_count_model_file)
    else:
        print("Usage: python get_day_count_model_file.py" "$modelFilesDir" "$fileIndex")
        sys.exit(1)


