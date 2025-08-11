from datetime import timedelta
import zipfile
import os
import matplotlib.pyplot as plt
import numpy as np
import xarray
import cf_xarray
from glob import glob
from parcels import (FieldSet, ParticleSet, 
                     JITParticle, ParticleFile,
                     AdvectionRK4)

dataset_folder = "/home/blaughli/symbolic_links_ROMS/WCR30_ERA_v1_1999_2024"
model_files = sorted(glob(f'{dataset_folder}/*.nc'))
grid_file = "/home/blaughli/tracking_project_v2/grid_data/wcr30test1_grd.nc"

model_files = model_files[0]

#def DeleteParticle(particle, fieldset, time):
#    particle.delete()

def DeleteParticle(particle, fieldset, time):
    if particle.state >= 50:
        particle.delete()

ds = xarray.open_dataset(model_files)
#timestamp = str(ds.ocean_time.min().values)[:13]

'''
N=200
u = xarray.DataArray(data=ds.u[:, -1, :-1, N:].values,
                coords=dict(lon=(["y", "x"], ds.lon_psi.values[:, N:]),
                            lat=(["y", "x"], ds.lat_psi.values[:, N:]),
                            time=ds.ocean_time),
                dims=['ocean_time', 'y', 'x'])
v = xarray.DataArray(data=ds.v[:, -1, :, N:-1].values,
                coords=dict(lon=(["y", "x"], ds.lon_psi.values[:, N:]),
                            lat=(["y", "x"], ds.lat_psi.values[:, N:]),
                            time=ds.ocean_time),
                dims=['ocean_time', 'y', 'x'])
'''

u = xarray.DataArray(data=ds.u[:, -1, :, :].values,
                coords=dict(lon=(["y", "x"], ds.lon_psi.values[:, :]),
                            lat=(["y", "x"], ds.lat_psi.values[:, :]),
                            time=ds.ocean_time),
                dims=['ocean_time', 'y', 'x'])
v = xarray.DataArray(data=ds.v[:, -1, :, :].values,
                coords=dict(lon=(["y", "x"], ds.lon_psi.values[:, :]),
                            lat=(["y", "x"], ds.lat_psi.values[:, :]),
                            time=ds.ocean_time),
                dims=['ocean_time', 'y', 'x'])

ds_parcels = xarray.Dataset({'u': u, 'v': v})

variables = {'U': 'u', 'V': 'v'}
dimensions = {'lon': 'lon', 'lat': 'lat', 'time': 'time'}
fieldset = FieldSet.from_xarray_dataset(ds_parcels, variables, dimensions, 
                                        interp_method='cgrid_velocity',
                                        gridindexingtype='nemo')

nparticles = 30
lon, lat = np.meshgrid(np.linspace(-125, -122, nparticles), np.linspace(40., 41, nparticles))
pset = ParticleSet(fieldset=fieldset, 
                   pclass=JITParticle,
                   lon=lon, lat=lat)   

output_file = pset.ParticleFile(name='tracks.nc', outputdt=timedelta(hours=1))
pset.write=True
pset.execute([AdvectionRK4, DeleteParticle],                 # the kernel (which defines how particles move)
             endtime=ds_parcels.time[-1].values,    # the total length of the run
             dt=timedelta(minutes=5),      # the timestep of the kernel
             output_file=output_file,
 )

output_file.export()

#floats=xarray.open_dataset('tracks.nc')

