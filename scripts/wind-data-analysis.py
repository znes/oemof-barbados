import os

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

solar = pd.read_excel("data/solar.xlsx", sheet_name="all")
solar.index = pd.date_range("2014", freq="h", periods=8760)
solar.resample("D").mean().plot()
solar["Day of Year"] = solar.index.dayofyear
solar.set_index("Day of Year",append=True, inplace=True)
solar_plot = solar.stack().to_frame().reset_index()
solar_plot.rename(columns={0: "Capacity Factor"} ,inplace=True)
# ax = sns.lineplot(data=solar_plot, y="Capacity Factor", x="Day of Year", color="orange")
# ax.set_xlim(0,365)
# plt.savefig(
#     "visualization/figures/solar_analysis.pdf",
#     #bbox_extra_artists=(lgd,),
#     bbox_inches="tight",
# )

df = pd.read_excel("data/wind_2014.xlsx", sheet_name="zone_1")
data14 = df["BB_wind_onshore_profile_zone_1"].to_frame()

df2 = pd.read_excel("data/wind_2002.xlsx", sheet_name="zone_1")
data02 = df2["BB_wind_onshore_profile_zone_1"].to_frame()

df3 = pd.read_excel("data/wind_2006.xlsx", sheet_name="zone_1", skiprows=[0,1,2])
data06 = df3["BB_wind_onshore_profile_zone_1"].to_frame()

df4 = pd.read_excel("data/wind_2010.xlsx", sheet_name="zone_1")
data10 = df4["BB_wind_onshore_profile_zone_1"].to_frame()

# 2014 for all years to allow concat after resample
data14.index = pd.date_range("2014", freq="h", periods=8760)
data02.index = pd.date_range("2014", freq="h", periods=8760)
data10.index = pd.date_range("2014", freq="h", periods=8760)
data06.index = pd.date_range("2014", freq="h", periods=8760)

means = pd.concat([
 data14.resample("D").mean(),
 data06.resample("D").mean(),
 data02.resample("D").mean(),
data10.resample("D").mean()
],
axis=1)

means["Day of Year"] = means.index.dayofyear
means.set_index("Day of Year",append=True, inplace=True)
means_plot = means.stack().to_frame().reset_index()
means_plot.rename(columns={0: "Capacity Factor"} ,inplace=True)
ax = sns.lineplot(data=means_plot, y="Capacity Factor", x="Day of Year")
ax.set_xlim(0,365)
plt.savefig(
    "visualization/figures/wind_analysis.pdf",
    #bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)


means_plot["Type"] = "wind"
solar_plot["Type"] = "solar"
both = pd.concat([means_plot, solar_plot])
ax = sns.lineplot(data=both, y="Capacity Factor", x="Day of Year", hue="Type")
ax.set_xlim(0,365)
plt.savefig(
    "visualization/figures/wind_solar_analysis.pdf",
    #bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)
# heat map plot ....
data14.index = pd.date_range("2014", freq="h", periods=8760)
data14["hour"] = data14.index.hour
data14["day"] = data14.index.dayofyear
data14.set_index(["hour", "day"], inplace=True)
data14 = data14.unstack()
data14.columns = data14.columns.droplevel(0)
ax = sns.heatmap(data14, cmap="YlGnBu")

# turn the axis label
for item in ax.get_yticklabels():
    item.set_rotation(0)

for item in ax.get_xticklabels():
    item.set_rotation(90)
