
import os


# --------------------------------
# --------------------------------
# SHOULD NOT BE CONSTANT
# --------------------------------
# --------------------------------
connectivity_version = "oldPolygonsNoPete_v1"
# --------------------------------
connectivity_dir_parent = "/home/blaughli/parcels/processing/p_production/z_binned_preconnectivty_data"
# --------------------------------
parcels_output_parent_dir = "/data04/cedwards/wcr30_parcels/wcr30_ERA1_v1/output_20251003"
parcels_log_parent_dir = "/home/cedwards/projects/parcels/batch_jobs/logs"
# --------------------------------
# --------------------------------
# --------------------------------
# --------------------------------


# --------------------------------
# Maybe ok constant?
# --------------------------------
job_list_file_out_stem = "files_to_process.txt"
cwd = os.getcwd()
job_list_file_out = os.path.join(str(cwd), job_list_file_out_stem)


tracking_file_ext = ".zarr"
connectivity_dir_stem = f"binned_data_{connectivity_version}"

conn_year_str = "bd_year_"
conn_month_str = "bd_month_"
conn_day_str = "bd_day_"
# ----------------------i----------



# Function definitions
# --------------------------------------------------------------------------------------------------------------------------------
def find_lines_with_string(filename, search_string):
    found_lines = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                if search_string in line:
                    found_lines.append(line.strip())
    except FileNotFoundError:
        print(f"Error: file '{filename}' not found.")
    return found_lines
# --------------------------------------------------------------------------------------------------------------------------------



processed_dates_list = []

connectivity_dir = os.path.join(connectivity_dir_parent, connectivity_dir_stem)

if os.path.exists(connectivity_dir):
    processed_year_dirs = os.listdir(connectivity_dir)
    processed_year_dirs.sort()
    for directory_year in processed_year_dirs:
        processed_year_dir = os.path.join(connectivity_dir,directory_year)
        if os.path.isdir(processed_year_dir):
            processed_year = processed_year_dir.split(conn_year_str)[-1]
            processed_month_dirs = os.listdir(processed_year_dir)
            processed_month_dirs.sort()
            for directory_month in processed_month_dirs:
                processed_month_dir = os.path.join(processed_year_dir,directory_month)
                if os.path.isdir(processed_month_dir):
                    processed_month = processed_month_dir.split(conn_month_str)[-1]
                    processed_day_dirs = os.listdir(processed_month_dir)
                    processed_day_dirs.sort()
                    for directory_day in processed_day_dirs:
                        processed_day_dir = os.path.join(processed_month_dir,directory_day)
                        if os.path.isdir(processed_day_dir):
                            processed_day = processed_day_dir.split(conn_day_str)[-1]
                            processed_dates_list.append(f"{processed_year}{processed_month}{processed_day}")







log_filename_string = "stdout"
started_tracking_jobs_string = "year_day"
finished_tracking_jobs_string = "Finished"

files_to_process_list = []

log_year_dirs = os.listdir(parcels_log_parent_dir)
log_year_dirs.sort()
for directory in log_year_dirs:
    log_year_dir = os.path.join(parcels_log_parent_dir,directory)
    if os.path.isdir(log_year_dir):
        log_files = os.listdir(log_year_dir)
        log_files.sort()
        for filename in log_files:
            if log_filename_string in filename:

                log_filename = os.path.join(log_year_dir, filename)

                started_tracking_jobs_lines = find_lines_with_string(log_filename,started_tracking_jobs_string)
                finished_tracking_jobs_lines = find_lines_with_string(log_filename,finished_tracking_jobs_string)


                # Only processed finished lines.  ALSO NEED TO CHECK IF WE'VE ALREADY PROCESSED RUNS!!!!!  NEED TO IMPLEMENT THAT!!!
                for i_line in range(len(finished_tracking_jobs_lines)):
                    date_pre = started_tracking_jobs_lines[i_line].split()[0]
                    date_string_no_spaces = date_pre.replace("-","")

                    if date_string_no_spaces not in processed_dates_list:

                        tracking_year = date_pre.split("-")[0]
                        tracking_dir = os.path.join(parcels_output_parent_dir,f"output_{tracking_year}",f"z_output_{date_string_no_spaces}")

                        # -------------------------------------------------------------------------------------------------------------------------------------------------
                        # THERE SHOULD ONLY EVER BE ONE zarr_file HERE, UNLESS OUR TRACKING OUTPUT FILE ORGANIZATION SCHEME CHANGES
                        for filename in os.listdir(tracking_dir):
                            if filename.endswith(tracking_file_ext):
                                tracking_file = os.path.join(tracking_dir,filename)
                                files_to_process_list.append(tracking_file)
                        # -------------------------------------------------------------------------------------------------------------------------------------------------
                        

#                break
#    break


with open(job_list_file_out, "w") as file:
    for file_string in files_to_process_list:
        file.write(file_string + "\n")










