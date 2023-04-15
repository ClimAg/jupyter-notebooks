#!/usr/bin/env python
# coding: utf-8

# # ModVege results - EURO-CORDEX - Difference in max - historical and rcp45/rcp85

# import libraries
from datetime import datetime, timezone
import climag.plot_stats as cstats
import importlib

season_list = ["DJF", "MAM", "JJA", "SON"]

data = cstats.hist_rcp_stats_data(dataset="EURO-CORDEX", stat="max")

importlib.reload(cstats)

# ## Total growth (daily)

for season in season_list:
    cstats.plot_all(
        data=data["EURO-CORDEX_s"],
        var="gro",
        season=season,
        levels=cstats.colorbar_levels(35),
        ticks=cstats.colorbar_ticks(35),
    )

# ## Potential growth (daily)

for season in season_list:
    cstats.plot_all(
        data=data["EURO-CORDEX_s"],
        var="pgro",
        season=season,
        levels=cstats.colorbar_levels(90),
        ticks=cstats.colorbar_ticks(90),
    )

# ## Total ingestion (daily)

for season in season_list:
    cstats.plot_all(
        data=data["EURO-CORDEX_s"],
        var="c_bm",
        season=season,
        levels=cstats.colorbar_levels(15),
        ticks=cstats.colorbar_ticks(15),
    )

# ## Standing biomass (cumulative)

for season in season_list:
    cstats.plot_all(
        data=data["EURO-CORDEX_s"],
        var="bm",
        season=season,
        levels=cstats.colorbar_levels(1800),
        ticks=cstats.colorbar_ticks(1800),
    )

# ## Defoliation (senescence + abscission) (daily)

for season in season_list:
    cstats.plot_all(
        data=data["EURO-CORDEX_s"],
        var="sen_abs",
        season=season,
        levels=cstats.colorbar_levels(90),
        ticks=cstats.colorbar_ticks(90),
    )

# ## Total biomass consumption (ingested + harvested) (yearly total)

cstats.plot_all(
    data=data["EURO-CORDEX_c"],
    var="c_bm_all",
    season=None,
    levels=cstats.colorbar_levels(900),
    ticks=cstats.colorbar_ticks(900),
)

print("Last updated:", datetime.now(tz=timezone.utc))