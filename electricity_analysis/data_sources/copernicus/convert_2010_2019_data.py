import xarray as xr

print('Wind 2010-2014')
ds = xr.open_dataset("./_data/copernicus/europe_wind_2010_2014.grib", engine="cfgrib")
ds.to_netcdf('./_data/copernicus/europe_wind_2010_2014.nc')

print('Wind 2015-2019')
ds = xr.open_dataset("./_data/copernicus/europe_wind_2015_2019.grib", engine="cfgrib")
ds.to_netcdf('./_data/copernicus/europe_wind_2015_2019.nc')

print('Temperature 2010-2014')
ds = xr.open_dataset("./_data/copernicus/europe_temperature_2010_2014.grib", engine="cfgrib")
ds.to_netcdf('./_data/copernicus/europe_temperature_2010_2014.nc')

print('Temperature 2014-2019')
ds = xr.open_dataset("./_data/copernicus/europe_temperature_2015_2019.grib", engine="cfgrib")
ds.to_netcdf('./_data/copernicus/europe_temperature_2015_2019.nc')