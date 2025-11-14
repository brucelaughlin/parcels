
import os
import argparse
import yaml
from pathlib import Path
import xarray as xr

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

parser = argparse.ArgumentParser()
parser.add_argument('configfile', type=str)
args = parser.parse_args()


config_file = args.configfile

with open(config_file,'r') as stream:
    config_dict = yaml.safe_load(stream)

string_list = [str(num) for num in config_dict['yearsEnd']]

print(" ".join(string_list))
