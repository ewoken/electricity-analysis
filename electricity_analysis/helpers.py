import xarray as xr
from shapely.geometry import mapping, shape, Point

def load_copernicus_dataset(path, **kwargs):
    ds = xr.open_dataset(path, **kwargs)
    ds = ds.reset_coords(['valid_time', 'number', 'step', 'surface'], drop=True)
    ds.attrs = {}
    return ds


def filter_da_by_geometry(da, geometry, cell_coord='lat_lng'):
    country_shape = shape(geometry)
    cells = [
        (lat, lng)
        for lat,lng in da[cell_coord].values
        if country_shape.contains(Point(lng, lat))
    ]
    return da.sel({ cell_coord: cells })