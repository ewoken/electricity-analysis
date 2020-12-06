import time
import os

import xarray as xr
import numpy as np
import pandas as pd
from pathlib import Path

from data_sources.thewindpower_net.loaders import load_country_wind_farms, load_turbine_profiles

default_countries = ['AUT', 'BEL', 'DEU', 'DNK', 'ESP', 'GBR',  'IRL', 'ITA', 'NLD', 'PRT']

def compute_simulation(
    start_date,
    end_date,
    wind_speed_da,
    wind_farms_df,
    turbine_profile_da,
    with_height_interpol=True,
    with_log=False
):
    dates = pd.date_range(start=start_date, end=end_date, freq='1H')

    ds = xr.Dataset(
        {
            'production':  (['farm', 'time'], np.zeros((len(wind_farms_df), len(dates)))),
            'capacity': (['farm', 'time'], np.zeros((len(wind_farms_df), len(dates))))
        },
        coords={
            'farm': wind_farms_df['name'].values,
            'time': dates
        }
    )

    sel_wind_speed_da = wind_speed_da.sel(time=dates)
    mean_profile = turbine_profile_da.mean('turbine')

    mean_hubHeight = wind_farms_df['hubHeight_m'].mean()

    # select wind farms
    mask_with_coordinates = wind_farms_df['coordinates'].notnull()
    mask_with_total_power = wind_farms_df['totalPower_kW'].notnull()
    mask_commissionned = wind_farms_df['commissioningDate'] < dates[-1]
    mask_dismantled_null = wind_farms_df['dismantlementDate'].isnull()
    mask_not_dismantled = mask_dismantled_null | (dates[0] < wind_farms_df['dismantlementDate'])
    mask = mask_commissionned & mask_not_dismantled & mask_with_coordinates & mask_with_total_power
    sel_wind_farms_names = wind_farms_df[mask]['name']

    # Compute production for each wind farm
    start = time.clock_gettime(0)
    for i, farm_name in enumerate(sel_wind_farms_names):
        commissioning_date = wind_farms_df.at[farm_name, 'commissioningDate']
        dismantlement_date = wind_farms_df.at[farm_name, 'dismantlementDate']
        coordinates = wind_farms_df.at[farm_name, 'coordinates']
        turbine_type = wind_farms_df.at[farm_name, 'turbineTypeUrl']
        total_power_MW = wind_farms_df.at[farm_name, 'totalPower_kW'] / 1000
        
        # interpolate wind speed at position
        farm_wind_speed = sel_wind_speed_da.interp(
            latitude=coordinates[0],
            longitude=coordinates[1]
        )

        # interpolate wind speed at hub height
        if with_height_interpol:
            hub_height_m = wind_farms_df.at[farm_name, 'hubHeight_m']
            if np.isnan(hub_height_m):
                hub_height_m = mean_hubHeight
            farm_wind_speed = farm_wind_speed * (hub_height_m/100)**0.143

        # init capacity array
        capacity = xr.DataArray(
            np.full(len(dates), total_power_MW),
            coords = [dates],
            dims=['time']
        )

        # select wind turbine profile
        if turbine_type in turbine_profile_da['turbine']:
            profile = turbine_profile_da.sel(turbine=turbine_type)
        else:
            profile = mean_profile
        
        # take into account commissioning and dismantlements
        if dates[0] < commissioning_date:
            before_commissioning =  pd.date_range(
                start=dates[0],
                end=np.minimum(commissioning_date, dates[-1]),
                freq='1H'
            )
            # easier to change wind speed than prod
            farm_wind_speed.loc[{ 'time': before_commissioning }] = 0 
            capacity.loc[{ 'time': before_commissioning }] = 0

        if not pd.isnull(dismantlement_date) and dismantlement_date < dates[-1]:
            after_dismantlement = pd.date_range(
                start=np.maximum(dismantlement_date, dates[0]),
                end=dates[-1],
                freq='1H'
            )
            # easier to change wind speed than prod
            farm_wind_speed.loc[{ 'time': after_dismantlement }] = 0
            capacity.loc[{ 'time': after_dismantlement }] = 0

        # compute production
        prod = np.interp(
            farm_wind_speed.values,
            profile['wind_speed'].values,
            profile.values
        ) * total_power_MW
        
        # assigne results
        ds['production'].loc[{ 'farm': farm_name }] = prod
        ds['capacity'].loc[{ 'farm': farm_name }] = capacity

        if with_log & (i % 10 == 0):
            dt = time.clock_gettime(0) - start
            print(i, len(sel_wind_farms_names), dt)
    
    return ds


def do_country_simulation(
    country_code,
    start_date,
    end_date,
    turbine_profiles,
    wind_speed
):
    wind_farms = load_country_wind_farms(country_code)
    offshore = wind_farms[wind_farms['type'] == 'OFFSHORE']
    onshore = wind_farms[wind_farms['type'] != 'OFFSHORE']

    onshore_file = f'./_data/simulation/{country_code}_onshore_wind_prod.nc'
    if not os.path.isfile(onshore_file):
        print(country_code, 'onshore')
        ds = compute_simulation(
            start_date,
            end_date,
            wind_speed,
            onshore,
            turbine_profiles,
            with_height_interpol=True,
            with_log=True
        )
        ds.to_netcdf(onshore_file)

    offshore_file = f'./_data/simulation/{country_code}_offshore_wind_prod.nc'
    if not os.path.isfile(offshore_file):
        print(country_code, 'offshore')
        ds = compute_simulation(
            start_date,
            end_date,
            wind_speed,
            offshore,
            turbine_profiles,
            with_height_interpol=True,
            with_log=True
        )
        ds.to_netcdf(offshore_file)



if __name__ == '__main__':
    Path('./_data/simulation/').mkdir(parents=True, exist_ok=True)

    wind_speed = xr.load_dataset('./_data/copernicus/europe_wind_speed_2010_2019.nc')
    turbine_profiles = load_turbine_profiles()
    start_date = '2015-01-01T00:00'
    end_date = '2019-12-31T23:00'

    for country_code in default_countries:
        do_country_simulation(
            country_code,
            start_date,
            end_date,
            turbine_profiles,
            wind_speed['wind_speed']
        )
    