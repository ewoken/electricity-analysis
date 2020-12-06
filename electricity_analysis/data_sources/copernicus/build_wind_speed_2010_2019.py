import xarray as xr
import numpy as np

ds = xr.open_dataset("./_data/copernicus/europe_wind_2010_2014.nc")
ds = ds.reset_coords(['valid_time', 'number', 'step', 'surface'], drop=True)
ds.attrs = {}
da = np.sqrt(ds['u100']**2 + ds['v100']**2)

ds2 = xr.open_dataset("./_data/copernicus/europe_wind_2015_2019.nc")
ds2 = ds2.reset_coords(['valid_time', 'number', 'step', 'surface'], drop=True)
ds2.attrs = {}
da2 = np.sqrt(ds2['u100']**2 + ds2['v100']**2)

res = xr.combine_by_coords([
    da.to_dataset(name='wind_speed'),
    da2.to_dataset(name='wind_speed')
])
res.to_netcdf('./_data/copernicus/europe_wind_speed_2010_2019.nc')