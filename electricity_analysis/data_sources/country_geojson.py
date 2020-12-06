import requests
import json
import os
from pathlib import Path
import zipfile
import shutil

def get_data():
    file_path = '_data/countries.geojson'

    if not os.path.isfile(file_path):
        print(f'Downloading {file_path} ...')
        url = 'https://datahub.io/core/geo-countries/r/1.geojson'
        r = requests.get(url)

        Path('_data').mkdir(parents=True, exist_ok=True)
        with open('_data/countries.zip', 'wb') as f:
            f.write(r.content)

        with zipfile.ZipFile('_data/countries.zip', 'r') as zip_ref:
            res = zip_ref.extractall('_data/countries')
        
        os.replace('_data/countries/archive/countries.geojson', file_path)
        shutil.rmtree('_data/countries')
        os.remove('_data/countries.zip')

    with open(file_path) as f:
        res = json.load(f)

    return {
        feature['properties']['ISO_A3']: feature['geometry']
        for feature in res['features']
    }

