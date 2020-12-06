import os
import requests
import pandas as pd
import pytz
from pathlib import Path

download_path = './_data/ORE/national_eco2mix'

def get_year_data(year):
    file_path = os.path.join(download_path, f'{year}.csv')

    if not os.path.isfile(file_path):
        print(f'Downloading {file_path} ...')
        url = f'https://opendata.reseaux-energies.fr/explore/dataset/eco2mix-national-cons-def/download/?format=csv&refine.date_heure={year}'
        r = requests.get(url)

        Path(download_path).mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(r.text)

    return format_data(pd.read_csv(file_path, sep=';'))

       
def format_data(data):
    data = data[data['consommation'].notnull()]
    data.drop(columns=[
        'perimetre',
        'nature',
        'date',
        'heure',
        'taux_co2',
        'ech_comm_angleterre',
        'ech_comm_espagne',
        'ech_comm_italie',
        'ech_comm_suisse',
        'ech_comm_allemagne_belgique',
    ], inplace=True)
    data.rename(columns={
        'prevision_j1': 'day_ahead_forecast', 
        'prevision_j': 'd_day_forecast',
        'date_heure': 'date_time',
        'consommation': 'load_MW',
        'fioul': 'oil_prod_MW',
        'charbon': 'hard_coal_prod_MW',
        'gaz': 'gas_prod_MW',
        'nucleaire': 'nuclear_prod_MW',
        'eolien': 'wind_prod_MW',
        'solaire': 'solar_prod_MW',
        'hydraulique': 'hydro_prod_MW',
        'pompage': 'hydro_pumped_storage_MW',
        'bioenergies': 'bio_prod_MW',
        'ech_physiques': 'total_physical_exchange_MW',
        'fioul_tac': 'oil_turbines_prod_MW',
        'fioul_cogen': 'oil_cogen_prod_MW',
        'fioul_autres': 'oil_others_prod_MW',
        'gaz_tac': 'gas_turbines_prod_MW',
        'gaz_cogen': 'gas_cogen_prod_MW',
        'gaz_ccg': 'gas_cc_prod_MW',
        'gaz_autres': 'gas_others_prod_MW',
        'hydraulique_fil_eau_eclusee': 'hydro_run_of_river_prod_MW',
        'hydraulique_lacs': 'hydro_lakes_prod_MW',
        'hydraulique_step_turbinage': 'hydro_pumped_prod_MW',
        'bioenergies_dechets': 'bio_waste_prod_MW',
        'bioenergies_biomasse': 'bio_biomass_prod_MW',
        'bioenergies_biogaz': 'bio_biogas_prod_MW',
    }, inplace=True)
    data['date_time'] = pd.to_datetime(data['date_time'].values, utc=True)
    return data

def get_data(start=None, end=None):
    start_dt = pd.Timestamp(start) if start is not None else pd.Timestamp('2012-01-01', tz=pytz.utc)
    end_dt = pd.Timestamp(end) if end is not None else pd.Timestamp.now(tz=pytz.utc)

    res = pd.concat([
        get_year_data(year)
        for year in  range(start_dt.year, end_dt.year + 1)
    ])
    
    return res[(start_dt <= res['date_time']) & (res['date_time'] <= end_dt)]



