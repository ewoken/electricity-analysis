import os

from pathlib import Path
from entsoe import EntsoePandasClient
import pandas as pd
import pycountry

client = EntsoePandasClient('360846f6-6ab3-445c-925f-8d2b4d3a2c6c')

# 'CH', 'GR', 'HR', 'HU', 'LT', 'LU', 'LV', 'MT', 'NO', 'PL', 'RO', 'RS', 'SE', 'SI','SK'
default_countries = ['AUT', 'BEL', 'DEU', 'DNK', 'ESP', 'GBR',  'IRL', 'ITA', 'NLD', 'PRT']
years = [2015, 2016, 2017, 2018, 2019]

base_dir = './_data/entsoe/'

all_columns = [
    'Biomass/Actual Aggregated',
    'Fossil Gas/Actual Aggregated',
    'Fossil Brown coal/Lignite/Actual Aggregated',
    'Fossil Coal-derived gas/Actual Aggregated',
    'Fossil Hard coal/Actual Aggregated',
    'Fossil Oil/Actual Aggregated',
    'Fossil Oil shale/Actual Aggregated',
    'Fossil Peat/Actual Aggregated',
    'Geothermal/Actual Aggregated',
    'Marine/Actual Aggregated',
    'Other/Actual Aggregated',
    'Other renewable/Actual Aggregated',
    'Hydro Pumped Storage/Actual Aggregated',
    'Hydro Pumped Storage/Actual Consumption',
    'Hydro Run-of-river and poundage/Actual Aggregated',
    'Hydro Water Reservoir/Actual Aggregated',
    'Nuclear/Actual Aggregated',
    'Solar/Actual Aggregated',
    'Waste/Actual Aggregated',
    'Wind Onshore/Actual Aggregated',
    'Wind Offshore/Actual Aggregated',
]

rename_map = {
    'Fossil Hard coal/Actual Aggregated': 'hard_coal_prod_MW',
    'Hydro Pumped Storage/Actual Aggregated': 'hydro_pumped_prod_MW',
    'Hydro Pumped Storage/Actual Consumption': 'hydro_pumped_storage_MW',
    'Hydro Run-of-river and poundage/Actual Aggregated': 'hydro_run_of_river_prod_MW',
    'Hydro Water Reservoir/Actual Aggregated': 'hydro_lakes_prod_MW',
    'Nuclear/Actual Aggregated': 'nuclear_prod_MW',
    'Solar/Actual Aggregated': 'solar_prod_MW',
    'Wind Onshore/Actual Aggregated': 'wind_onshore_prod_MW',
    'Wind Offshore/Actual Aggregated': 'wind_offshore_prod_MW',
    'Other/Actual Aggregated': 'other_prod_MW'
}
    
 
def get_year_country_data(country_code, year):
    country_code = pycountry.countries.get(alpha_3=country_code).alpha_2

    folder = os.path.join(base_dir, country_code, str(year))
    Path(folder).mkdir(parents=True, exist_ok=True)
    generation_file_path = os.path.join(folder, "generation.csv")
    load_file_path = os.path.join(folder, "load.csv")
    start = pd.Timestamp(year=year, month=1, day=1, tz="Europe/Brussels")
    end = pd.Timestamp(year=(year + 1), month=1, day=1, tz="Europe/Brussels")

    if not os.path.isfile(generation_file_path):
        print(f'Downloading {generation_file_path} ...')
        generation = client.query_generation(
            country_code,
            start=start,
            end=end,
            psr_type=None
        )
        columns = generation.columns

        if (columns.nlevels > 1):
            header = columns.get_level_values(0).astype(str).values + '/' +\
                columns.get_level_values(1).astype(str).values
        else:
            header = columns.map(str).values + '/Actual Aggregated'
        generation.to_csv(
            generation_file_path,
            header=header,
            index_label='date_time'
        )
    else:
        generation = pd.read_csv(
            generation_file_path,
            parse_dates=['date_time'],
            date_parser=lambda col: pd.to_datetime(col, utc=True)
        )
        
    if not os.path.isfile(load_file_path):
        print(f'Downloading {load_file_path} ...')
        load = client.query_load(
            country_code,
            start=start,
            end=end,
        )
        load.to_csv(load_file_path, index_label='date_time', header=['load_MW'])
    else:
        load = pd.read_csv(
            load_file_path,
            parse_dates=['date_time'],
            date_parser=lambda col: pd.to_datetime(col, utc=True)
        )

    generation = generation.filter(items=[
        col
        for col in generation.columns
        if col.startswith('Hydro Pumped Storage') or not col.endswith('Actual Consumption')
    ])

    for col in all_columns:
        if not col in generation.columns:
            generation[col] = 0
        elif generation[col].isnull().all():
            generation[col] = 0

    generation.set_index('date_time', inplace=True)
    load.set_index('date_time', inplace=True)

    generation = generation.resample('1H').mean().interpolate(limit=1)
    load = load.resample('1H').mean().interpolate(limit=1)

    generation.rename(rename_map, axis=1, inplace=True)
    generation['oil_prod_MW'] = generation['Fossil Oil/Actual Aggregated'] +\
        generation['Fossil Oil shale/Actual Aggregated']

    generation['brown_coal_prod_MW'] = generation['Fossil Brown coal/Lignite/Actual Aggregated'] +\
        generation['Fossil Peat/Actual Aggregated']

    generation['bio_prod_MW'] = generation['Waste/Actual Aggregated'] +\
        generation['Biomass/Actual Aggregated'] +\
        generation['Geothermal/Actual Aggregated'] +\
        generation['Marine/Actual Aggregated'] +\
        generation['Other renewable/Actual Aggregated']
    
    generation['gas_prod_MW'] = generation['Fossil Gas/Actual Aggregated'] +\
        generation['Fossil Coal-derived gas/Actual Aggregated']

    generation['hydro_prod_MW'] = generation['hydro_pumped_prod_MW'] +\
        generation['hydro_run_of_river_prod_MW'] +\
        generation['hydro_lakes_prod_MW']

    generation['wind_prod_MW'] = generation['wind_onshore_prod_MW'] +\
        generation['wind_offshore_prod_MW']

    for col in all_columns:
        if col in generation.columns:
            del generation[col]

    res = load.join(generation)
    res.reset_index(inplace=True)
    
    return res

    
def get_country_data(country_code):
    return pd.concat([
        get_year_country_data(country_code, year)
        for year in years
    ])


def get_formated_country_data(country_code):
    data = get_country_data(country_code)
    data['country'] = country_code
    return data

def get_all_data(countries=default_countries):
    return pd.concat([
        get_formated_country_data(country_code)
        for country_code in countries
    ])