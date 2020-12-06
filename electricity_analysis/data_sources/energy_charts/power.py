import os
import requests
import pandas as pd
import numpy as np
import json
import pytz
from pathlib import Path
from functools import reduce

download_path = './_data/energy_charts/power'

def get_year_data(year):
    file_path = os.path.join(download_path, f'{year}.json')

    if not os.path.isfile(file_path):
        print(f'Downloading {file_path} ...')
        url = f'https://energy-charts.info/charts/power/raw_data/de/year_{year}.json'
        r = requests.get(url)

        Path(download_path).mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(r.text)

    with open(file_path, 'r') as f:
        df = format_data(json.load(f))

    return df


def format_data(data):
    data_frames = [
        pd.DataFrame.from_records(
            serie['values'],
            columns=['timestamp', serie['key'][0]['en']]
        ).set_index('timestamp')
        for serie in data
    ]
    df = reduce(
        lambda r, df: pd.merge(r, df, left_index=True, right_index=True),
        data_frames
    )
    df = df * 1000
    df.rename(columns={
        'Import Balance': 'total_physical_exchange_MW',
        'Hydro Power': 'hydro_prod_MW',
        'Biomass': 'bio_prod_MW',
        'Uranium': 'nuclear_prod_MW',
        'Brown Coal': 'brown_coal_prod_MW',
        'Hard Coal': 'hard_coal_prod_MW',
        'Oil': 'oil_prod_MW',
        'Gas': 'gas_prod_MW',
        'Pumped Storage': 'hydro_pumped_prod_MW',
        'Seasonal Storage': 'seasonal_storage_MW',
        'Wind': 'wind_prod_MW',
        'Solar': 'solar_prod_MW',
        'Others': 'others_prod_MW',
    }, inplace=True)

    if 'others_prod_MW' not in df.columns:
        df['others_prod_MW'] = 0

    df['others_prod_MW'] = df['others_prod_MW'] + df['seasonal_storage_MW']
    df['hydro_prod_MW'] = df['hydro_prod_MW'] + df['hydro_pumped_prod_MW']

    del df['seasonal_storage_MW']

    df['date_time'] = [pd.Timestamp(time, unit='ms', tz=pytz.utc) for time in df.index]
    df.set_index('date_time', drop=False, inplace=True)
    return df


def get_data(start=None, end=None):
    start_dt = pd.Timestamp(start) if start is not None else pd.Timestamp('2010-01-01', tz=pytz.utc)
    end_dt = pd.Timestamp(end) if end is not None else pd.Timestamp.now(tz=pytz.utc)

    res = pd.concat([
        get_year_data(year)
        for year in  range(start_dt.year, end_dt.year + 1)
    ])
    
    return res[(start_dt <= res['date_time']) & (res['date_time'] <= end_dt)]