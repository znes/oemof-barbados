import pandas as pd
#from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

# some processing stuff
df = pd.read_excel(
    "data/cruise-demand.xlsx",
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

# fix missing indices and fillna with 0
demand_agg_sum = demand_agg_sum.reindex(pd.date_range(start="2018", periods=8760, freq="H")).fillna(0)["demand"]

# plot to see how it looks :-)
ax = demand_agg_sum.plot()
ax.set_ylabel("Aggregated Cruise Ship Demand in MW")
plt.savefig("visualization/input-cruise-ship-demand.pdf")
# to see the structure of the arrivals and depatures
df["ARRIVAL TIME"] = pd.to_timedelta(df["TIME"]) / pd.offsets.Hour(1) #.astype("float")
df["HOURS OF STAY"] = pd.to_timedelta(df["HOURS"]) / pd.offsets.Hour(1) #.astype("float")
df.plot.scatter(x="ARRIVAL TIME", y="HOURS OF STAY")
plt.savefig("visualization/input-arrival-and-stay.pdf")
