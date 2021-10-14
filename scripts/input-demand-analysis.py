import pandas as pd
#from datetime import datetime
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.pyplot as plt
from scipy import interpolate

# some processing stuff
df = pd.read_excel(
    "data/cruise-arrivals.xlsx",
    dtype= {"YEAR":int, "ARRIVED DATE": str, "TIME": str, "HOURS": str})
df = df[df["Year"] == 2018]

df["ARRIVAL"] =  pd.to_datetime(df["ARRIVED DATE"] + " " + df["TIME"] )
df["DEPATURE"] = df["ARRIVAL"] + pd.to_timedelta(df['HOURS'],"h")

# create function to interpolate based on relative time length stay of ship
demand = np.array([12, 12, 10, 6, 4, 4, 4, 4, 6, 10, 12, 12])
timerel = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])/11
f = interpolate.interp1d(timerel, demand)

# create demand profiles for every arrived ships based on its duration
stays = {}
for _, row in df.iterrows():
    df_ = pd.DataFrame(index= pd.date_range(row["ARRIVAL"], row["DEPATURE"], freq="h"))
    df_["timerel"] = [i/len(df_) for i in range(1, len(df_)+1)]
    df_["demand"] = df_.apply(lambda x: f(x["timerel"]), axis=1)
    stays[_] = df_

# concat, resample and aggregated values,
demand_agg = pd.concat(stays.values(), axis=0).sort_index()
demand_agg_sum = demand_agg.resample("H").sum()
demand_agg_sum.sum()
# fix missing indices and fillna with 0
demand_agg_sum = demand_agg_sum.reindex(pd.date_range(start="2018", periods=8760, freq="H")).fillna(0)["demand"]

cruise_profile = demand_agg_sum / demand_agg_sum.sum()
cruise_profile.to_csv("data/cruise_ship_profile.csv")

# plot to see how it looks :-)
ax = demand_agg_sum.plot()
ax.set_ylabel("Aggregated Cruise Ship Demand in MW")
plt.savefig("visualization/figures/input-cruise-ship-demand.pdf")
# to see the structure of the arrivals and depatures
df["ARRIVAL TIME"] = pd.to_timedelta(df["TIME"]) / pd.offsets.Hour(1) #.astype("float")
df["HOURS OF STAY"] = pd.to_timedelta(df["HOURS"]) / pd.offsets.Hour(1) #.astype("float")
df.plot.scatter(x="ARRIVAL TIME", y="HOURS OF STAY")
plt.savefig("visualization/figures/input-arrival-and-stay.pdf")

load = pd.read_excel("scenarios/REF.xls", sheet_name="load", index_col=0)
df = pd.read_excel("scenarios/REF.xls", sheet_name="profiles", index_col=0, parse_dates=True)

profiles= df.iloc[:, 0:3]
amount = load["amount"].values
abs_profiles = profiles.multiply(amount)
abs_profiles["BB-Aggregated"] = abs_profiles.sum(axis=1)


ax = abs_profiles.iloc[4:168+4].plot(grid=True, color=["orange", "green", "skyblue", "darkred"])
#ax.set_ylim(0, 400)
ax.set_ylabel("Demand in MWh")
ax.set_xlabel("Hour")
handles, labels = ax.get_legend_handles_labels()
lgd = {k: v for k, v in dict(zip(handles, labels)).items()}

ax.set_ylabel("Demand in MW")
ax.grid(linestyle="--", lw=0.2)
lgd = ax.legend(
    list(lgd.keys()),
    ["el-demand", "evcc-demand", "cruise-demand", "aggregated-demand"],
    loc="lower left",
    bbox_to_anchor=(0.1, -0.40),
    ncol=2,
    borderaxespad=0,
    frameon=False,
)


inset = inset_axes(ax,
                    width="30%", # width = 30% of parent_bbox
                    height=1, # height : 1 inch
                    loc=1)
abs_profiles.iloc[:,2].plot(ax=inset, color="skyblue")
inset.set_title("Cruise Ships", backgroundcolor='w')
inset.set_ylabel("Demand in MW.", backgroundcolor='w')
inset.set_xlabel("Hour of year", backgroundcolor='w')
inset.set_xticklabels([""], backgroundcolor='w')

plt.savefig(
    "visualization/figures/load-profiles-input.pdf",
    #bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)
