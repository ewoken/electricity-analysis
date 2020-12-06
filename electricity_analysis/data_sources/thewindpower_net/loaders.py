import os
import json

import xarray as xr
import numpy as np
import pandas as pd
import pycountry

from scipy.interpolate import interp1d
from scipy.ndimage import gaussian_filter1d

def load_country_wind_farms(country_code):
    country_code = pycountry.countries.get(alpha_3=country_code).alpha_2

    with open(f'./_data/thewindpower_net/wind_farms/{country_code}.json') as f:
        farms = json.load(f)
    
    farm_parts = []
    for farm in farms:
        for idx, part in enumerate(farm['parts']):
            farm_parts.append({
                **part,
                'name': farm['name'] + '_' + str(idx),
            })

    farm_df = pd.DataFrame(farm_parts).set_index('name', drop=False)
    farm_df['commissioningDate'] = pd.to_datetime(farm_df['commissioningDate'])

    serie = farm_df['dismantlementDate']
    farm_df['dismantlementDate'] = pd.to_datetime(
        serie[serie.notna()].astype(int).astype(str) + "-01-01"
    )
    return farm_df

def load_turbine_profiles(smoothing=True, sigma=2):
    turbine_df = pd.read_json('./_data/thewindpower_net/world_turbines.json', orient='records').set_index('url')

    loadind_curves = {}

    for url, row in turbine_df.iterrows():
        if row['loadingCurve'] is not None:
            loading_curve = np.array(row['loadingCurve']) / np.array(row['power_kW'])
            loadind_curves[url] = loading_curve

    df = pd.DataFrame.from_dict(loadind_curves, orient='index')
    profiles = xr.DataArray(df, dims=['turbine', 'wind_speed'])
    profiles = profiles.assign_coords(wind_speed=profiles.wind_speed / 2)

    # smoothing
    if smoothing:
        f = interp1d(profiles['wind_speed'], profiles, kind='cubic')
        new_wind_speed = np.arange(0, 35, 0.1)
        new_profiles = gaussian_filter1d(
            np.maximum(f(new_wind_speed), 0),
            sigma=sigma,
            order=0,
            mode='nearest'
        )
        profiles = xr.DataArray(
            new_profiles,
            coords=[profiles['turbine'], new_wind_speed],
            dims=['turbine', 'wind_speed']
        )
    
    return profiles