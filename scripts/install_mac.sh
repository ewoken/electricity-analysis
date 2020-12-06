#!/bin/bash

brew install eecodes proj geos

virtualenv venv 
source venv/bin/activate
pip install cython numpy pyshp six
pip install shapely --no-binary shapely