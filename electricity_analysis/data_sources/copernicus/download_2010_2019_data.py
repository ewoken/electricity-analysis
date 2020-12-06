import cdsapi

c = cdsapi.Client()

common_options = {
    'product_type': 'reanalysis',
    'month': [
        '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12',
    ],
    'day': [
        '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12',
        '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24',
        '25', '26', '27', '28', '29', '30', '31',
    ],
    'time': [
        '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00',
        '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00',
        '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00',
    ],
    'area': [60, -12, 35, 32],
    'format': 'grib',
}

wind_variables = [
    '100m_u_component_of_wind', '100m_v_component_of_wind'
]

c.retrieve(
    'reanalysis-era5-single-levels',
    {
        **common_options,
        'variable': wind_variables,
        'year': [
           '2010', '2011' , '2012', '2013', '2014',
        ],
    },
    './_data/copernicus/europe_wind_2010_2014.grib'
)

c.retrieve(
    'reanalysis-era5-single-levels',
    {
        **common_options,
        'variable': wind_variables,
        'year': [
           '2015', '2016' , '2017', '2018', '2019',
        ],
    },
    './_data/copernicus/europe_wind_2015_2019.grib'
)

c.retrieve(
    'reanalysis-era5-single-levels',
    {
        **common_options,
        'variable': ['2m_temperature'],
        'year': [
           '2010', '2011' , '2012', '2013', '2014',
        ],
    },
    './_data/copernicus/europe_temperature_2010_2014.grib'
)

c.retrieve(
    'reanalysis-era5-single-levels',
    {
        **common_options,
        'variable': ['2m_temperature'],
        'year': [
           '2015', '2016' , '2017', '2018', '2019',
        ],
    },
    './_data/copernicus/europe_temperature_2015_2019.grib'
)