#!/usr/bin/env python
# coding: utf-8

# # HiResIreland

# import libraries
import glob
import itertools
import os
from datetime import datetime, timezone
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr
from dask.distributed import Client
import climag.plot_configs as cplt

print("Last updated:", datetime.now(tz=timezone.utc))

client = Client(n_workers=2, threads_per_worker=4, memory_limit="3GB")

client

DATA_DIR_BASE = os.path.join("data", "HiResIreland")

# directory to store outputs
DATA_DIR = os.path.join(DATA_DIR_BASE, "IE")
os.makedirs(DATA_DIR, exist_ok=True)

# Moorepark met station coords
LON, LAT = -8.26389, 52.16389

# Ireland boundary
GPKG_BOUNDARY = os.path.join("data", "boundaries", "boundaries.gpkg")
ie = gpd.read_file(GPKG_BOUNDARY, layer="NUTS_RG_01M_2021_2157_IE")
ie_bbox = gpd.read_file(
    GPKG_BOUNDARY, layer="NUTS_RG_01M_2021_2157_IE_BBOX_DIFF"
)

# ## Read a subset (historical)

data = xr.open_mfdataset(
    glob.glob(
        os.path.join(
            DATA_DIR_BASE, "COSMO5-CLM", "historical", "EC-EARTH", "*.nc"
        )
    ),
    chunks="auto",
    decode_coords="all",
)

# data = xr.open_mfdataset(
#     list(itertools.chain(*list(
#         glob.glob(os.path.join(
#             DATA_DIR_BASE, "COSMO5-CLM", "historical", "EC-EARTH", e
#         ))
#         for e in ["*mean_T_2M*.nc", "*ASOB_S*.nc", "*ET*.nc", "*TOT_PREC*.nc"]
#     ))),
#     chunks="auto",
#     decode_coords="all"
# )

data

# # copy time_bnds
# data_time_bnds = data.coords["time_bnds"]

# copy CRS
data_crs = data.rio.crs

data_crs

# drop spin-up year, for now
data = data.sel(time=slice("1976", "2005"))

# ## Ireland subset

# clip to Ireland's boundary
data = data.rio.clip(ie.buffer(1).to_crs(data_crs))

# # reassign time_bnds
# data.coords["time_bnds"] = data_time_bnds

# rename and assign attributes to ET var
data = data.rename({"w": "PET"})
data["PET"].attrs["long_name"] = "evapotranspiration"
data["PET"].attrs["units"] = "mm"

data

# ## Visualise fields

# ### Monthly averages

for var in ["ASWDIR_S", "ASWDIFD_S", "ASWDIFU_S", "ASOB_S"]:
    cplt.plot_averages(
        data=data,
        var=var,
        averages="month",
        boundary_data=ie_bbox,
        cbar_levels=16,
    )

for var in ["TOT_PREC", "PET", "T_2M", "ALB_RAD"]:
    cplt.plot_averages(
        data=data,
        var=var,
        averages="month",
        boundary_data=ie_bbox,
        cbar_levels=16,
    )

# ### Time series

# using Moorepark met station coordinates
cds = cplt.rotated_pole_point(data=data, lon=LON, lat=LAT)

data_ie = data.sel({"rlon": cds[0], "rlat": cds[1]}, method="nearest")

for var in data.data_vars:
    plt.figure(figsize=(12, 4))
    plt.plot(data_ie["time"], data_ie[var], linewidth=0.5)
    plt.ylabel(
        f"{data_ie[var].attrs['long_name']}\n[{data_ie[var].attrs['units']}]"
    )
    plt.tight_layout()
    plt.show()

# ### Box plots

data_ie_df = pd.DataFrame({"time": data_ie["time"]})
for var in data_ie.data_vars:
    data_ie_df[var] = data_ie[var]
data_ie_df.set_index("time", inplace=True)

for var in data_ie.data_vars:
    data_ie_df.plot.box(
        column=var, vert=False, showmeans=True, figsize=(12, 2)
    )
    plt.xlabel(
        f"{data_ie[var].attrs['long_name']} [{data_ie[var].attrs['units']}]"
    )
    plt.tight_layout()
    plt.show()

# ## Calculate surface downwelling shortwave radiation

# ### Using net shortwave and albedo

data = data.assign(rsds=data["ASOB_S"] / (1 - data["ALB_RAD"]))
data["rsds"].attrs["units"] = "W m-2"
data["rsds"].attrs["long_name"] = "Surface Downwelling Shortwave Radiation"

cplt.plot_averages(
    data=data,
    var="rsds",
    averages="month",
    boundary_data=ie_bbox,
    cbar_levels=16,
)

data_ie = data.sel({"rlon": cds[0], "rlat": cds[1]}, method="nearest")

plt.figure(figsize=(12, 4))
plt.plot(data_ie["time"], data_ie["rsds"], linewidth=0.5)
plt.ylabel(
    f"{data_ie['rsds'].attrs['long_name']}\n[{data_ie['rsds'].attrs['units']}]"
)
plt.tight_layout()
plt.show()

data_ie_df = pd.DataFrame({"time": data_ie["time"]})
data_ie_df["rsds"] = data_ie["rsds"]
data_ie_df.set_index("time", inplace=True)

data_ie_df.plot.box(column="rsds", vert=False, showmeans=True, figsize=(12, 2))
plt.xlabel(
    f"{data_ie['rsds'].attrs['long_name']} [{data_ie['rsds'].attrs['units']}]"
)
plt.tight_layout()
plt.show()

# ### Using direct and diffuse downward components

data = data.assign(rsds=data["ASWDIR_S"] + data["ASWDIFD_S"])
data["rsds"].attrs["units"] = "W m-2"
data["rsds"].attrs["long_name"] = "Surface Downwelling Shortwave Radiation"

cplt.plot_averages(
    data=data,
    var="rsds",
    averages="month",
    boundary_data=ie_bbox,
    cbar_levels=16,
)

data_ie = data.sel({"rlon": cds[0], "rlat": cds[1]}, method="nearest")

plt.figure(figsize=(12, 4))
plt.plot(data_ie["time"], data_ie["rsds"], linewidth=0.5)
plt.ylabel(
    f"{data_ie['rsds'].attrs['long_name']}\n[{data_ie['rsds'].attrs['units']}]"
)
plt.tight_layout()
plt.show()

data_ie_df = pd.DataFrame({"time": data_ie["time"]})
data_ie_df["rsds"] = data_ie["rsds"]
data_ie_df.set_index("time", inplace=True)

data_ie_df.plot.box(column="rsds", vert=False, showmeans=True, figsize=(12, 2))
plt.xlabel(
    f"{data_ie['rsds'].attrs['long_name']} [{data_ie['rsds'].attrs['units']}]"
)
plt.tight_layout()
plt.show()

# ## Calculate photosynthetically active radiation

# Papaioannou et al. (1993) - irradiance ratio
data = data.assign(PAR=data["rsds"] * 0.473)

data

# compare radiation vals
data_ie = data.sel({"rlon": cds[0], "rlat": cds[1]}, method="nearest").sel(
    time=slice("1989", "1991")
)

data_ie_df = pd.DataFrame({"time": data_ie["time"]})
for var in ["rsds", "ASOB_S", "ASWDIFD_S", "ASWDIR_S", "PAR"]:
    data_ie_df[var] = data_ie[var]

data_ie_df.set_index("time", inplace=True)

data_ie_df.plot(figsize=(12, 4), colormap="viridis", xlabel="")
plt.tight_layout()
plt.show()

data_ie_df[["rsds", "PAR"]].plot(
    figsize=(12, 4), colormap="viridis", xlabel=""
)
plt.tight_layout()
plt.show()

data_ie = data.sel({"rlon": cds[0], "rlat": cds[1]}, method="nearest")
data_ie_df.plot.box(vert=False, showmeans=True, figsize=(12, 4))
plt.tight_layout()
plt.show()

# ## Convert units and rename variables

for v in data.data_vars:
    var_attrs = data[v].attrs  # extract attributes
    if v == "T_2M":
        var_attrs["units"] = "°C"
        data[v] = data[v] - 273.15
        var_attrs["note"] = "Converted from K to °C by subtracting 273.15"
        var_attrs["long_name"] = "Near-Surface Air Temperature"
    elif v == "PAR":
        var_attrs["units"] = "MJ m⁻² day⁻¹"
        data[v] = data[v] * (60 * 60 * 24 / 1e6)
        var_attrs["long_name"] = "Surface Photosynthetically Active Radiation"
        var_attrs["note"] = (
            "Calculated by multiplying the surface downwelling shortwave "
            "radiation (calculated by summing the direct and diffuse "
            "downward shortwave radiation components) with an irradiance "
            "ratio of 0.473 based on Papaioannou et al. (1993); converted "
            "from W m⁻² to MJ m⁻² day⁻¹ by multiplying 0.0864 as "
            "documented in the FAO Irrigation and Drainage Paper No. "
            "56 (Allen et al., 1998, p. 45)"
        )
    elif v in ("TOT_PREC", "PET", "w"):
        var_attrs["units"] = "mm day⁻¹"
        if v in ("w", "PET"):
            var_attrs["long_name"] = "Potential Evapotranspiration"
        else:
            var_attrs["long_name"] = "Precipitation"
            var_attrs["note"] = (
                "kg m⁻² is equivalent to mm day⁻¹, assuming a water density "
                "of 1,000 kg m⁻³"
            )
    data[v].attrs = var_attrs  # reassign attributes

# rename
data = data.rename({"T_2M": "T", "TOT_PREC": "PP"})

# remove dataset history
del data.attrs["history"]

# assign dataset name
data.attrs["dataset"] = f"IE_HiResIreland_{data.attrs['title'][:-4]}"

# keep only required variables
data = data.drop_vars(
    ["ASWDIR_S", "ASWDIFD_S", "ASWDIFU_S", "ALB_RAD", "ASOB_S", "rsds"]
)

# assign attributes to the data
data.attrs["comment"] = (
    "This dataset has been clipped with the Island of Ireland's boundary and "
    "units have been converted. "
    "Last updated: "
    + str(datetime.now(tz=timezone.utc))
    + " by nstreethran@ucc.ie."
)

data

# ## Visualise

# ### Monthly averages

cplt.plot_averages(
    data=data,
    var="T",
    averages="month",
    boundary_data=ie_bbox,
    cbar_levels=[3 + 1 * n for n in range(13)],
)

for var in ["PP", "PET", "PAR"]:
    cplt.plot_averages(
        data=data,
        var=var,
        averages="month",
        boundary_data=ie_bbox,
        cbar_levels=16,
    )

# ### Seasonal averages

for var in ["PP", "PET", "PAR", "T"]:
    cplt.plot_averages(
        data=data,
        var=var,
        averages="season",
        boundary_data=ie_bbox,
        cbar_levels=14,
    )

# ### Time series

data_ie = data.sel({"rlon": cds[0], "rlat": cds[1]}, method="nearest")

data_ie

for var in data.data_vars:
    plt.figure(figsize=(12, 4))
    plt.plot(data_ie["time"], data_ie[var], linewidth=0.5)
    plt.title(f"{data_ie.attrs['dataset']}, lon={LON}, lat={LAT}")
    plt.ylabel(
        f"{data_ie[var].attrs['long_name']}\n[{data_ie[var].attrs['units']}]"
    )
    plt.tight_layout()
    plt.show()

data_ie = data_ie.sel(time=slice("1989", "1991"))

for var in data.data_vars:
    plt.figure(figsize=(12, 4))
    plt.plot(data_ie["time"], data_ie[var], linewidth=1)
    plt.title(f"{data_ie.attrs['dataset']}, lon={LON}, lat={LAT}")
    plt.ylabel(
        f"{data_ie[var].attrs['long_name']}\n[{data_ie[var].attrs['units']}]"
    )
    plt.tight_layout()
    plt.show()

data_ie_df = pd.DataFrame({"time": data_ie["time"]})
# configure plot title
plot_title = []
for var in data_ie.data_vars:
    data_ie_df[var] = data_ie[var]
    plot_title.append(
        f"{data_ie[var].attrs['long_name']} [{data_ie[var].attrs['units']}]"
    )

data_ie_df.set_index("time", inplace=True)

data_ie_df.plot(
    subplots=True,
    layout=(4, 1),
    figsize=(9, 11),
    legend=False,
    xlabel="",
    title=plot_title,
)

plt.tight_layout()
plt.show()

# ### Box plots

data_ie = data.sel({"rlon": cds[0], "rlat": cds[1]}, method="nearest")

data_ie_df = pd.DataFrame({"time": data_ie["time"]})
for var in data_ie.data_vars:
    data_ie_df[var] = data_ie[var]
data_ie_df.set_index("time", inplace=True)

for var in data_ie.data_vars:
    data_ie_df.plot.box(
        column=var, vert=False, showmeans=True, figsize=(12, 2)
    )
    plt.xlabel(
        f"{data_ie[var].attrs['long_name']} [{data_ie[var].attrs['units']}]"
    )
    plt.tight_layout()
    plt.show()

# ## Extend data to a spin-up year

data_interp = data.interp(
    time=pd.date_range(
        f"{int(data['time'][0].dt.year) - 1}-01-01T10:30:00",
        f"{int(data['time'][0].dt.year) - 1}-12-31T10:30:00",
        freq="D",
    ),
    kwargs={"fill_value": None},
)

data_interp.rio.write_crs(data_crs, inplace=True)

# merge spin-up year with first two years of the main data
data_interp = xr.combine_by_coords(
    [
        data_interp,
        data.sel(
            time=slice(
                str(int(data["time"][0].dt.year)),
                str(int(data["time"][0].dt.year) + 1),
            )
        ),
    ]
)

data_interp

data_ie = data_interp.sel({"rlon": cds[0], "rlat": cds[1]}, method="nearest")

plt.figure(figsize=(12, 4))
plt.plot(data_ie["time"], data_ie["T"], linewidth=1)
plt.title(f"{data_ie.attrs['dataset']}, lon={LON}, lat={LAT}")
plt.ylabel(
    f"{data_ie['T'].attrs['long_name']}\n[{data_ie['T'].attrs['units']}]"
)
plt.tight_layout()
plt.show()

# check value for the first day of the first year
data_ie["T"][
    data_interp.sel(time=str(int(data_interp["time"][0].dt.year))).dims["time"]
].values

# check first value of spin-up year - should be nan
data_ie["T"][0].values

# shift first year of the main data to the spin-up year
data_interp = data_interp.shift(
    time=-data_interp.sel(time=str(int(data_interp["time"][0].dt.year))).dims[
        "time"
    ]
)

data_ie = data_interp.sel({"rlon": cds[0], "rlat": cds[1]}, method="nearest")

# should be the same as before, but shifted forwards to the spin-up year
plt.figure(figsize=(12, 4))
plt.plot(data_ie["time"], data_ie["T"], linewidth=1)
plt.title(f"{data_ie.attrs['dataset']}, lon={LON}, lat={LAT}")
plt.ylabel(
    f"{data_ie['T'].attrs['long_name']}\n[{data_ie['T'].attrs['units']}]"
)
plt.tight_layout()
plt.show()

# check first value
data_ie["T"][0].values

# keep only spin-up year
data_interp = data_interp.sel(time=str(int(data_interp["time"][0].dt.year)))

data_interp

# merge with main dataset
data = xr.combine_by_coords([data, data_interp])

data

data_ie = data.sel({"rlon": cds[0], "rlat": cds[1]}, method="nearest").sel(
    time=slice("1975", "1977")
)

# spin-up year and first year should be identical
plt.figure(figsize=(12, 4))
plt.plot(data_ie["time"], data_ie["T"], linewidth=1)
plt.title(f"{data_ie.attrs['dataset']}, lon={LON}, lat={LAT}")
plt.ylabel(
    f"{data_ie['T'].attrs['long_name']}\n[{data_ie['T'].attrs['units']}]"
)
plt.tight_layout()
plt.show()
