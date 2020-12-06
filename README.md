# Weather Analysis

## Requirements

* Python 3
* [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)
* [eccodes](https://confluence.ecmwf.int/display/ECC/ecCodes+installation) (Available with [brew](https://brew.sh/))
* [cartopy](https://scitools.org.uk/cartopy/docs/latest/installing.html#installing)

You can install the two last ones on MacOS and rest of dependancies by running ./scripts/install_mac.sh

You must have 10Gb available on your disk, big files of data are required later.

## Get started

```bash
# create and activate virtual environment
virtualenv venv 
source venv/bin/activate

pip install -r requirements.txt

jupyter labextension install jupyterlab-plotly plotlywidget

# optional
./scripts/install_jupyterlab_extensions.sh

mkdir data
```


Now you can download data from Copernicus by registring and install your api key on your computer as described [here](https://cds.climate.copernicus.eu/api-how-to) and then running 
```bash
python download.py
```

⚠️ **Warning**: it can be really long (more than 1 hour depending of your connection). You can also modify `dowload.py` to shorter requested data.

Last step, convert your downloaded .grib file into a Netcdf file quicker to open later by `python convert.py`
```bash
python convert.py
```

Finally you can run jupyterlab:
```bash
jupyter lab
```