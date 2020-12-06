import xarray as xr
import numpy as np
import pandas as pd
from functools import reduce

from data_sources.country_geojson import get_data
from helpers import load_copernicus_dataset, filter_da_by_geometry


def get_country_data_frame(ds, country_code, country_geometries):
    print(country_code)
    country_geometry = country_geometries[country_code]
    ds = filter_da_by_geometry(ds, country_geometry)
    res = ds.mean(dim='lat_lng')
    df = res.to_dataframe()
    df['country'] = country_code
    df['temperature'] = df['t2m'] - 273.15
    del df['u100']
    del df['v100']
    del df['t2m']
    return df


def get_df(data_path, countries, country_geometries):
    print(data_path)
    ds = load_copernicus_dataset(data_path, engine="cfgrib").resample(time="1D").mean()
    ds['wind_speed'] = np.sqrt(ds['u100']**2 + ds['v100']**2)
    ds = ds.stack(lat_lng=["latitude", "longitude"])

    data_frames = [
        get_country_data_frame(ds, country_code, country_geometries)
        for country_code in countries
    ]

    df = pd.concat(data_frames)
    return df


if __name__ == "__main__":
    years = [1985, 1986, 1987, 1991, 1996, 1997, 2001, 2003, 2005, 2009]
    countries = ['FRA', 'BEL', 'GBR', 'DEU', 'CHE', 'NLD', 'ITA', 'ESP', 'PRT',
        'DNK', 'IRL']
    country_geometries = get_data()

    data_frames = [
        get_df(f'./_data/copernicus/europe_cold_wave_{year}.grib', countries, country_geometries)
        for year in years
    ]

    df = pd.concat(data_frames).rename({ 'time': 'date' })
    df.to_csv('./_data/country_cold_waves.csv')

