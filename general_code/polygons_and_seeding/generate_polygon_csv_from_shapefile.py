# Write polygons lat/lon to a csv file

import numpy as np
import os
import csv
import argparse
from pathlib import Path
import shapefile

parser = argparse.ArgumentParser()
parser.add_argument("inputfile", type=str)
args = parser.parse_args()

input_file = args.inputfile

cwd = os.getcwd()
output_dir = os.path.join(str(cwd),"z_output")
Path(output_dir).mkdir(parents=True, exist_ok=True)

output_file = os.path.join(output_dir,Path(input_file).stem) + ".txt"

field_names = ['cell #', ' vertex #', ' lat', ' lon']
csv_data = []
csv_data.append(field_names)
cell_number = 0

shapefile_object = shapefile.Reader(input_file)

for polygon_index in range(len(shapefile_object)): 
    
    cell_number += 1

    print(f"cell {cell_number:04d}/{len(shapefile_object)}")

    for vertex_number in range(len(shapefile_object.shape(polygon_index).points)):   

        vertex_number_print = vertex_number + 1

        data = []
        data.append(f"{cell_number:04d}")
        data.append(f" {vertex_number_print:03d}")
        data.append(f" {shapefile_object.shape(polygon_index).points[vertex_number][1]:.6f}")
        data.append(f" {shapefile_object.shape(polygon_index).points[vertex_number][0]:.6f}")

        csv_data.append(data)


with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(csv_data)



