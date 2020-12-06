import xarray as xr
import numpy as np
import pandas as pd
from functools import reduce

from data_sources.country_geojson import get_data
from helpers import load_copernicus_dataset, filter_da_by_geometry


def get_country_data_frame(da, country_code, country_geometries):
    print(country_code)
    country_geometry = country_geometries[country_code]
    da = filter_da_by_geometry(da, country_geometry)
    res = da.mean(dim='lat_lng')
    return res.to_dataframe(country_code)


def get_countries_day_wind_df(data_path, countries, country_geometries):
    print(data_path)
    ds = load_copernicus_dataset(data_path)
    da = np.sqrt(ds['u100']**2 + ds['v100']**2)
    da = da.resample(time="1D").mean().stack(lat_lng=["latitude", "longitude"])

    data_frames = [
        get_country_data_frame(da, country_code, country_geometries)
        for country_code in countries
    ]

    df = reduce(
        lambda r, df: pd.merge(r, df, left_index=True, right_index=True),
        data_frames
    )
    return df


if __name__ == "__main__":
    countries = ['FRA', 'BEL', 'GBR', 'DEU', 'CHE', 'NLD', 'ITA', 'ESP', 'PRT',
        'DNK', 'IRL']
    country_geometries = get_data()

    df_2010_2014 = get_countries_day_wind_df(
        './_data/copernicus/europe_wind_2010_2014.nc',
        countries,
        country_geometries
    )
    df_2015_2019 = get_countries_day_wind_df(
        './_data/copernicus/europe_wind_2015_2019.nc',
        countries,
        country_geometries
    )

    df = pd.concat([df_2010_2014, df_2015_2019]).rename({ 'time': 'date' })
    df.to_csv('./_data/country_day_winds_2010_2019.csv')

