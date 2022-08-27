# jupyter-notebooks

Jupyter notebooks for the [ClimAg](https://www.ucc.ie/en/eel/projects/climag/) research project

This research was funded by the Environment Protection Agency (EPA), Ireland
project "ClimAg: Multifactorial causes of fodder crises in Ireland and risks
due to climate change" under the Climate Change Research Programme grant
number 2018-CCRP-MS.50.

## Requirements

- Python 3
- JupyterLab
- Dask
- Matplotlib

## Python environment

Create a Conda environment:

```sh
conda env create
conda activate ClimAg
```

To update the environment:

```sh
conda env update --name ClimAg --file environment.yml
```

`environment.yml`:

```yml
name: ClimAg
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - jupyterlab
  - dask
  - matplotlib
  - rioxarray
  - geopandas
  - netcdf4
  - bottleneck
  - nc-time-axis
  - py-cordex
  - python-cdo
  - regionmask
```

## R environment

Create a Conda environment and install the Jupyter R kernel:

```sh
conda env create --file environment-r.yml
conda activate r-env
R -e "IRkernel::installspec()"
```

`environment-r.yml`:

```yml
name: r-env
channels:
  - conda-forge
  - defaults
dependencies:
  - r-base
  - r-essentials
  - r-rgdal
  - r-sf
  - r-geojsonio
  - r-rgeos
  - r-rastervis
  - jupyterlab
```

## Notebooks

Notebook | Link
--- | ---
Ireland boundary - NUTS 2021 | [nbviewer](https://nbviewer.org/gist/nmstreethran/20d0fdcb9fd282703aa24abd401bb8e1/ireland-boundary-nuts.ipynb)
Ireland boundary - Ordnance Survey Ireland / Northern Ireland | [nbviewer](https://nbviewer.org/gist/nmstreethran/20d0fdcb9fd282703aa24abd401bb8e1/ireland-boundary.ipynb)
CORINE land cover 2018 | [nbviewer](https://nbviewer.org/gist/nmstreethran/20d0fdcb9fd282703aa24abd401bb8e1/clc-2018.ipynb)
Met stations | [nbviewer](https://nbviewer.org/gist/nmstreethran/20d0fdcb9fd282703aa24abd401bb8e1/met-stations.ipynb)
py-cordex demo | [nbviewer](https://nbviewer.org/gist/nmstreethran/20d0fdcb9fd282703aa24abd401bb8e1/py-cordex.ipynb)
EURO-CORDEX | [nbviewer](https://nbviewer.org/gist/nmstreethran/20d0fdcb9fd282703aa24abd401bb8e1/eurocordex.ipynb)

### ISCRAES poster

Notebook | Link
--- | ---
Enniscorthy EURO-CORDEX | [nbviewer](https://nbviewer.org/gist/nmstreethran/20d0fdcb9fd282703aa24abd401bb8e1/enniscorthy.ipynb)

### [climate-change-droughts](https://github.com/ClimAg/climate-change-droughts) project

Notebook | Link
--- | ---
Find closest EURO-CORDEX icell to study location | [nbviewer](https://nbviewer.org/gist/nmstreethran/20d0fdcb9fd282703aa24abd401bb8e1/eurocordex-find-icell.ipynb)
SPI - historical - Cork Airport | [nbviewer](https://nbviewer.org/gist/nmstreethran/20d0fdcb9fd282703aa24abd401bb8e1/eurocordex-process-spi-hist-ca.ipynb)
SPI - future - Cork Airport | [nbviewer](https://nbviewer.org/gist/nmstreethran/20d0fdcb9fd282703aa24abd401bb8e1/eurocordex-process-spi-future-ca.ipynb)
SPEI - historical - Cork Airport | [nbviewer](https://nbviewer.org/gist/nmstreethran/20d0fdcb9fd282703aa24abd401bb8e1/eurocordex-process-spei-hist-ca.ipynb)
SPEI - future - Cork Airport | [nbviewer](https://nbviewer.org/gist/nmstreethran/20d0fdcb9fd282703aa24abd401bb8e1/eurocordex-process-spei-future-ca.ipynb)

## References

- Coordinate reference system for Ireland: [ETRS89 / Irish TM EPSG 2157](https://www.gov.uk/government/publications/uk-geospatial-data-standards-register/national-geospatial-data-standards-register#standards-for-coordinate-reference-systems)

## Licence

Copyright 2022 N. M. Streethran

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  <https://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
