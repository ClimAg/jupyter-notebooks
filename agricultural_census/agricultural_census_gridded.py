# %% [markdown]
# # Gridding agricultural census data
#
# <https://james-brennan.github.io/posts/fast_gridding_geopandas/>

# %%
# import libraries
import os
import itertools
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import shapely
import xarray as xr
import climag.plot_configs as cplt

# %% [markdown]
# ## Open some gridded climate data

# %%
TS_FILE = os.path.join(
    "data", "EURO-CORDEX", "IE",
    "IE_EUR-11_ICHEC-EC-EARTH_rcp85_r12i1p1_SMHI-RCA4_v1_day_"
    "20410101-20701231.nc"
)

# %%
data = xr.open_dataset(TS_FILE, chunks="auto", decode_coords="all")

# %%
data

# %%
# keep only one variable
data = data.drop_vars(names=["PET", "PP", "RG", "PAR"])

# %%
data

# %%
# copy CRS
crs = data.rio.crs

# %%
crs

# %% [markdown]
# ## Use the gridded data's bounds to generate a gridded vector layer

# %%
data.rio.bounds()

# %%
xmin, ymin, xmax, ymax = data.rio.bounds()
# the difference between two adjacent rotated lat or lon values is the
# cell size
cell_size = float(data["rlat"][1] - data["rlat"][0])

# %%
# create the cells in a loop
grid_cells = []
for x0 in np.arange(xmin, xmax + cell_size, cell_size):
    for y0 in np.arange(ymin, ymax + cell_size, cell_size):
        # bounds
        x1 = x0 - cell_size
        y1 = y0 + cell_size
        grid_cells.append(shapely.geometry.box(x0, y0, x1, y1))
grid_cells = gpd.GeoDataFrame(grid_cells, columns=["geometry"], crs=crs)

# %%
grid_cells.shape

# %%
grid_cells.head()

# %% [markdown]
# ## Subset climate data to visualise the cells

# %%
data_ = data.sel(time="2041-06-21T12:00:00.000000000")

# %%
data_

# %%
# find number of grid cells with data
len(
    data_["T"].values.flatten()[np.isfinite(data_["T"].values.flatten())]
)

# %%
plot_transform = cplt.rotated_pole_transform(data_)
plt.figure(figsize=(9, 7))
axs = plt.axes(projection=cplt.plot_projection)

# plot data for the variable
data_["T"].plot(
    ax=axs,
    cmap="Spectral_r",
    x="rlon",
    y="rlat",
    robust=True,
    transform=plot_transform
)
grid_cells.to_crs(cplt.plot_projection).boundary.plot(
    ax=axs, color="darkslategrey", linewidth=.2
)

axs.set_title(None)
plt.axis("equal")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## Read stocking rate data

# %%
sr = gpd.read_file(
    os.path.join("data", "agricultural_census", "agricultural_census.gpkg"),
    layer="stocking_rate"
)

# %%
sr.crs

# %%
sr.head()

# %%
sr.shape

# %%
sr["stocking_rate"].max()

# %%
sr["stocking_rate"].min()

# %%
sr.plot(column="stocking_rate", cmap="Spectral_r")
plt.tick_params(labelbottom=False, labelleft=False)
plt.show()

# %% [markdown]
# ## Reproject cells to the CRS of the stocking rate data

# %%
# use a projected CRS (e.g. 2157) instead of a geographical CRS (e.g. 4326)
grid_cells = grid_cells.to_crs(sr.crs)

# %%
grid_cells.head()

# %%
axs = sr.plot(column="stocking_rate", cmap="Spectral_r")
grid_cells.boundary.plot(color="darkslategrey", linewidth=.2, ax=axs)
axs.tick_params(labelbottom=False, labelleft=False)
plt.show()

# %% [markdown]
# ## Create gridded stocking rate data

# %%
merged = gpd.sjoin(sr, grid_cells, how="left")

# %%
merged.head()

# %%
merged.shape

# %%
axs = merged.plot(column="stocking_rate", cmap="Spectral_r")
grid_cells.boundary.plot(color="darkslategrey", linewidth=.2, ax=axs)
axs.tick_params(labelbottom=False, labelleft=False)
plt.show()

# %%
# compute stats per grid cell, use the mean stocking rate
dissolve = merged[["stocking_rate", "index_right", "geometry"]].dissolve(
    by="index_right", aggfunc=np.mean
)

# %%
dissolve.shape

# %%
dissolve.head()

# %%
len(dissolve.index.unique())

# %%
# merge with cell data
grid_cells.loc[dissolve.index, "stocking_rate"] = (
    dissolve["stocking_rate"].values
)

# %%
# drop rows with missing values
grid_cells.dropna(inplace=True)

# %%
grid_cells.head()

# %%
grid_cells.shape

# %%
len(grid_cells["geometry"].unique())

# %%
grid_cells["stocking_rate"].max()

# %%
grid_cells["stocking_rate"].min()

# %%
plt.figure(figsize=(9, 7))
axs = plt.axes(projection=cplt.plot_projection)

# plot data for the variable
data_["T"].plot(
    ax=axs,
    cmap="Spectral_r",
    x="rlon",
    y="rlat",
    robust=True,
    transform=plot_transform
)

grid_cells.to_crs(cplt.plot_projection).plot(
    column="stocking_rate", ax=axs, edgecolor="darkslategrey",
    facecolor="none", linewidth=.5
)

axs.set_title(None)
plt.axis("equal")
plt.tight_layout()
plt.show()

# %%
axs = grid_cells.plot(
    column="stocking_rate", cmap="Spectral_r", scheme="equal_interval",
    edgecolor="darkslategrey", linewidth=.2, figsize=(6, 7),
    legend=True, legend_kwds={
        "loc": "upper left", "fmt": "{:.2f}", "title": "Stocking rate"
    }
)
for legend_handle in axs.get_legend().legendHandles:
    legend_handle.set_markeredgewidth(.2)
    legend_handle.set_markeredgecolor("darkslategrey")
axs.tick_params(labelbottom=False, labelleft=False)
plt.axis("equal")
plt.tight_layout()
plt.show()

# %% [markdown]
# ## Find stocking rate for each EURO-CORDEX grid cell

# %%
grid_centroids = {
    "wkt": [],
    "rlon": [],
    "rlat": []
}

for rlon, rlat in itertools.product(
    range(len(data.coords["rlon"])),
    range(len(data.coords["rlat"]))
):
    data__ = data.isel(rlon=rlon, rlat=rlat)

    # ignore null cells
    if not data__["T"].isnull().all():
        grid_centroids["wkt"].append(
            f"POINT ({float(data__['rlon'].values)} "
            f"{float(data__['rlat'].values)})"
        )
        grid_centroids["rlon"].append(float(data__["rlon"].values))
        grid_centroids["rlat"].append(float(data__["rlat"].values))

# %%
grid_centroids = gpd.GeoDataFrame(
    grid_centroids,
    geometry=gpd.GeoSeries.from_wkt(grid_centroids["wkt"], crs=crs)
)

# %%
grid_centroids.head()

# %%
grid_centroids.crs

# %%
grid_centroids.shape

# %%
plt.figure(figsize=(9, 7))
axs = plt.axes(projection=cplt.plot_projection)

# plot data for the variable
data_["T"].plot(
    ax=axs,
    cmap="Spectral_r",
    x="rlon",
    y="rlat",
    robust=True,
    transform=plot_transform
)

grid_cells.to_crs(cplt.plot_projection).plot(
    column="stocking_rate", ax=axs, edgecolor="darkslategrey",
    facecolor="none", linewidth=.5
)

grid_centroids.to_crs(cplt.plot_projection).plot(
    ax=axs, color="darkslategrey", markersize=5
)

axs.set_title(None)
plt.axis("equal")
plt.tight_layout()
plt.show()

# %%
grid_cells = gpd.sjoin(grid_cells, grid_centroids.to_crs(grid_cells.crs))

# %%
grid_cells.drop(columns=["wkt", "index_right"], inplace=True)

# %%
grid_cells.head()

# %%
grid_cells.crs

# %%
grid_cells.shape
