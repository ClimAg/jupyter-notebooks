#!/usr/bin/env python
# coding: utf-8

# # ModVege grass growth model (Jouven et al. 2006) with HiResIreland data
#
# - Jouven, M., Carrère, P., and Baumont, R. (2006a). 'Model predicting
#   dynamics of biomass, structure and digestibility of herbage in managed
#   permanent pastures. 1. Model description', *Grass and Forage Science*,
#   vol. 61, no. 2, pp. 112-124. DOI:
#   [10.1111/j.1365-2494.2006.00515.x][Jouven1].
# - Jouven, M., Carrère, P., and Baumont, R. (2006b). 'Model predicting
#   dynamics of biomass, structure and digestibility of herbage in managed
#   permanent pastures. 2. Model evaluation', *Grass and Forage Science*,
#   vol. 61, no. 2, pp. 125-133. DOI:
#   [10.1111/j.1365-2494.2006.00517.x][Jouven2].
# - Chemin, Y. (2022). 'modvege', Python. [Online]. Available at
#   <https://github.com/YannChemin/modvege> (Accessed 6 September 2022).
#
# [Jouven1]: https://doi.org/10.1111/j.1365-2494.2006.00515.x
# [Jouven2]: https://doi.org/10.1111/j.1365-2494.2006.00517.x

import glob
import os
from datetime import datetime, timezone

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr
from dask.distributed import Client

import climag.plot_configs as cplt

client = Client(n_workers=2, threads_per_worker=4, memory_limit="3GB")

client

DATA_DIR = os.path.join("data", "ModVege")

# Ireland boundary
GPKG_BOUNDARY = os.path.join("data", "boundaries", "boundaries_all.gpkg")
# ie = gpd.read_file(GPKG_BOUNDARY, layer="NUTS_RG_01M_2021_2157_IE")
ie = gpd.read_file(GPKG_BOUNDARY, layer="NUTS_RG_01M_2021_2157_IE_BBOX_DIFF")

# met station coords
LON_VAL, LAT_VAL = -10.24333, 51.93806  # Valentia Observatory
LON_ROC, LAT_ROC = -8.24444, 51.79306  # Roche's Point
LON_JOH, LAT_JOH = -6.5, 52.29167  # Johnstown Castle
LON_MUL, LAT_MUL = -7.36222, 53.53722  # Mullingar

# ## rcp45

data = xr.open_mfdataset(
    glob.glob(
        os.path.join(DATA_DIR, "HiResIreland", "rcp45", "EC-EARTH", "*.nc")
    ),
    chunks="auto",
    decode_coords="all",
)

data

# remove the spin-up year
data = data.sel(time=slice("2042", "2070"))

# ### Seasonal averages

for var in ["gro", "bm", "pgro", "aet"]:
    cplt.plot_averages(
        data=data, var=var, averages="season", boundary_data=ie, cbar_levels=12
    )

# ### Point subset

# #### Valentia Observatory

cds = cplt.rotated_pole_point(data=data, lon=LON_VAL, lat=LAT_VAL)
data_ie = data.sel({"rlon": cds[0], "rlat": cds[1]}, method="nearest").sel(
    time=slice("2054", "2056")
)

data_ie_df = pd.DataFrame({"time": data_ie["time"]})
for var in data_ie.data_vars:
    data_ie_df[var] = data_ie[var]

data_ie_df.set_index("time", inplace=True)

# configure plot title
plot_title = []
for var in data_ie.data_vars:
    plot_title.append(
        f"{data_ie[var].attrs['long_name']} [{data_ie[var].attrs['units']}]"
    )

data_ie_df.plot(
    subplots=True,
    layout=(5, 3),
    figsize=(15, 11),
    legend=False,
    xlabel="",
    title=plot_title,
)

plt.tight_layout()
plt.show()

# #### Roche's Point

cds = cplt.rotated_pole_point(data=data, lon=LON_ROC, lat=LAT_ROC)
data_ie = data.sel({"rlon": cds[0], "rlat": cds[1]}, method="nearest").sel(
    time=slice("2054", "2056")
)

data_ie_df = pd.DataFrame({"time": data_ie["time"]})
for var in data_ie.data_vars:
    data_ie_df[var] = data_ie[var]

data_ie_df.set_index("time", inplace=True)

# configure plot title
plot_title = []
for var in data_ie.data_vars:
    plot_title.append(
        f"{data_ie[var].attrs['long_name']} [{data_ie[var].attrs['units']}]"
    )

data_ie_df.plot(
    subplots=True,
    layout=(5, 3),
    figsize=(15, 11),
    legend=False,
    xlabel="",
    title=plot_title,
)

plt.tight_layout()
plt.show()

# #### Johnstown Castle

cds = cplt.rotated_pole_point(data=data, lon=LON_JOH, lat=LAT_JOH)
data_ie = data.sel({"rlon": cds[0], "rlat": cds[1]}, method="nearest").sel(
    time=slice("2054", "2056")
)

data_ie_df = pd.DataFrame({"time": data_ie["time"]})
for var in data_ie.data_vars:
    data_ie_df[var] = data_ie[var]

data_ie_df.set_index("time", inplace=True)

# configure plot title
plot_title = []
for var in data_ie.data_vars:
    plot_title.append(
        f"{data_ie[var].attrs['long_name']} [{data_ie[var].attrs['units']}]"
    )

data_ie_df.plot(
    subplots=True,
    layout=(5, 3),
    figsize=(15, 11),
    legend=False,
    xlabel="",
    title=plot_title,
)

plt.tight_layout()
plt.show()

# #### Mullingar

cds = cplt.rotated_pole_point(data=data, lon=LON_MUL, lat=LAT_MUL)
data_ie = data.sel({"rlon": cds[0], "rlat": cds[1]}, method="nearest").sel(
    time=slice("2054", "2056")
)

data_ie_df = pd.DataFrame({"time": data_ie["time"]})
for var in data_ie.data_vars:
    data_ie_df[var] = data_ie[var]

data_ie_df.set_index("time", inplace=True)

# configure plot title
plot_title = []
for var in data_ie.data_vars:
    plot_title.append(
        f"{data_ie[var].attrs['long_name']} [{data_ie[var].attrs['units']}]"
    )

data_ie_df.plot(
    subplots=True,
    layout=(5, 3),
    figsize=(15, 11),
    legend=False,
    xlabel="",
    title=plot_title,
)

plt.tight_layout()
plt.show()
