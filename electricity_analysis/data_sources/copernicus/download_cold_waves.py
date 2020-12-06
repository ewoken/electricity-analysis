import cdsapi
import os

c = cdsapi.Client()

common_options = {
    'product_type': 'reanalysis',
    'variable': ['100m_u_component_of_wind', '100m_v_component_of_wind',
        '2m_temperature'
    ],
    'time': [
        '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00',
        '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00',
        '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00',
    ],
    'area': [60, -12, 35, 32],
    'format': 'grib',
}

# http://www.meteofrance.fr/documents/10192/33043852/Vagues+de+froid+en+France+de+1947+a+2015_HD/e199e36b-f650-42e9-b719-865697900238?t=1454408063411&json={%27type%27:%27Media_Image%27,%27titre%27:%27Vagues%20de%20froid%20en%20France%20de%201947%20%C3%A0%202015%27,%27alternative%27:%27%27,%27legende%27:%27%27,%27credits%27:%27M%C3%A9t%C3%A9o-France%27,%27poids%27:%27687,2ko%27}
# http://www.meteofrance.fr/documents/10192/68248105/ColdWaves2018.png/cfa7e59b-43b8-4c4b-ad01-12d6cb69c697?t=1542980754194&json={%27type%27:%27Media_Image%27,%27titre%27:%27Vagues%20de%20froid%20observ%C3%A9es%20en%20France%20de%201947%20%C3%A0%202018%27,%27alternative%27:%27Vagues%20de%20froid%20observ%C3%A9es%20en%20France%20de%201947%20%C3%A0%202018%27,%27legende%27:%27Vagues%20de%20froid%20observ%C3%A9es%20en%20France%20de%201947%20%C3%A0%202018%27,%27credits%27:%27M%C3%A9t%C3%A9o-France%27,%27poids%27:%27404,3ko%27}

print('1985')
file_path = './_data/copernicus/europe_cold_wave_1985.grib'
if not os.path.isfile(file_path):
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            **common_options,
            'year': ['1985'],
            'month': ['01'],
            'day': [
                '03', '04', '05', '06', '07', '08', '09', '10', '11',
                '12', '13', '14', '15', '16', '17',
            ]
        },
        file_path
    )

print('1986')
file_path = './_data/copernicus/europe_cold_wave_1986.grib'
if not os.path.isfile(file_path):
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            **common_options,
            'year': ['1986'],
            'month': ['02'],
            'day': ['07', '08', '09', '10', '11', '12', '13']
        },
        file_path
    )

print('1987')
file_path = './_data/copernicus/europe_cold_wave_1987.grib'
if not os.path.isfile(file_path):
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            **common_options,
            'year': ['1987'],
            'month': ['01'],
            'day': [
                '08', '09', '10', '11', '12', '13', '14', '15', '16', '17',
                '18', '19', '20', '21', '22', '23',
            ]
        },
        file_path
    )

print('1991')
file_path = './_data/copernicus/europe_cold_wave_1991.grib'
if not os.path.isfile(file_path):
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            **common_options,
            'year': ['1991'],
            'month': ['02'],
            'day': ['05', '06', '07', '08', '09', '10', '11', '12', '13', '14']
        },
        file_path
    )

print('1996')
file_path = './_data/copernicus/europe_cold_wave_1996.grib'
if not os.path.isfile(file_path):
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            **common_options,
            'year': ['1996'],
            'month': ['12'],
            'day': ['26', '27', '28', '29', '30', '31']
        },
        file_path
    )

print('1997')
file_path = './_data/copernicus/europe_cold_wave_1997.grib'
if not os.path.isfile(file_path):
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            **common_options,
            'year': ['1997'],
            'month': ['01'],
            'day': ['01', '02', '03', '04', '05', '06', '07', '08']
        },
        file_path
    )

print('2001')
file_path = './_data/copernicus/europe_cold_wave_2001.grib'
if not os.path.isfile(file_path):
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            **common_options,
            'year': ['2001'],
            'month': ['12'],
            'day': [
                '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24',
            ]
        },
        file_path
    )

print('2003')
file_path = './_data/copernicus/europe_cold_wave_2003.grib'
if not os.path.isfile(file_path):
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            **common_options,
            'year': ['2003'],
            'month': ['01'],
            'day': ['06', '07', '08', '09', '10', '11', '12', '13']
        },
        file_path
    )

print('2005')
file_path = './_data/copernicus/europe_cold_wave_2005.grib'
if not os.path.isfile(file_path):
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            **common_options,
            'year': ['2005'],
            'month': ['02'],
            'day': ['20', '21', '22', '23', '24', '25', '26', '27', '28']
        },
        file_path
    )

print('2009')
file_path = './_data/copernicus/europe_cold_wave_2009.grib'
if not os.path.isfile(file_path):
    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            **common_options,
            'year': ['2009'],
            'month': ['12'],
            'day': ['15', '16', '17', '18', '19', '20']
        },
        file_path
    )