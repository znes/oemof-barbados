import os

import pandas as pd
import numpy as np

# from cydets.algorithm import detect_cycles
from oemof.tools.economics import annuity
import matplotlib.pyplot as plt
from matplotlib import colors
import seaborn as sns


color = {
    "hfo-msce": "lightgray",
    "hfo-lsce": "darkgray",
    "waste-ocgt": "darkgreen",
    "pv-utility": "gold",
    "pv-distributed": "lightyellow",
    "solar-pv-distributed": "lightyellow",
    "solar-pv-utility": "gold",
    "wind-onshore": "skyblue",
    "wind-offshore": "steelblue",
    "bagasse-st": "yellowgreen",
    "hydro-phs": "purple",
    "phs": "purple",
    "lithium-battery": "plum",
    "battery": "plum",
    # "waste-st": "yellowgreen",
    "demand": "slategray",
    "cruise-demand": "mediumturquoise",
    "ev-demand": "powderblue",
    "excess": "crimson",
    "fossil": "lightgray",
}
color_dict = {
    name: colors.to_hex(color) for name, color in color.items()
}

path = os.path.join(
    os.path.expanduser("~"), "oemof-results", "barbados"
)

renewables = ["bagasse-st", "wind-onshore", "solar-pv", "waste-ocgt"]
phs_storages = [
    "hydro-phs",
]
storages = ["lithium-battery", "hydro-phs"]

conventionals = [
    "hfo-lsce",
    "hfo-msce",
]
scenarios = ["SQ"] + ["SQ-" + name for name in ["100"]]
scenarios += ["HD"] + ["HD-" + name for name in ["100"]]
scenarios += ["RB"] + ["RB-" + name for name in ["100"]]
scenarios += ["REF"] + ["REF-" + name for name in ["100"]]
#scenarios += ["RW"] + ["RW-" + name for name in ["100"]]
scenarios += ["LOP"] + ["LOP-" + name for name in ["100"]]
scenarios += ["HRC"] + ["HRC-" + name for name in ["100"]]
scenarios += ["NPHS"] + ["NPHS-" + name for name in ["100"]]
scenarios += ["HCD2"] + ["HCD2-" + name for name in ["100"]]
scenarios += ["EVCC"] + ["EVCC-" + name for name in ["100"]]


bus = "BB-electricity"
all_capacities = pd.DataFrame()
co2 = pd.DataFrame()
energy = pd.DataFrame()

for dir in os.listdir(path):
    capacities = pd.read_csv(
        os.path.join(path, dir, "capacities.csv"), index_col=0
    )
    capacities.set_index("to", append=True, inplace=True)
    capacities = (
        capacities.groupby(["to", "carrier", "tech"])
        .sum()
        .unstack("to")
    )
    capacities.index = ["-".join(i) for i in capacities.index]

    temp = pd.read_csv(
        os.path.join(path, dir, bus + ".csv"), index_col=0
    )
    temp = temp.sum()
    temp.name = dir
    energy = pd.concat([energy, temp], axis=1, sort=False)

    capacities.columns = capacities.columns.droplevel(0)
    capacities.columns = [dir]
    all_capacities = pd.concat(
        [all_capacities, capacities], axis=1, sort=False
    )

    capacities.groupby(level=[0]).sum()

all_capacities = all_capacities.sort_index(axis=1)
re_share = (
    1
    - energy.loc[conventionals].sum()
    / energy.loc[[l for l in energy.index if "load" in l]].sum()
).sort_index()

# -capacity plot -----------------------------------------------------------
_df = all_capacities.copy()
order = [
    "hfo-lsce",
    "hfo-msce",
    "bagasse-st",
    "waste-ocgt",
    "pv-utility",
    "pv-distributed",
    "wind-onshore",
    "hydro-phs",
    "lithium-battery",
]

_df.columns = [c.replace("-base-", "-") for c in _df.columns]
re_share.index = [c.replace("-base-", "-") for c in re_share.index]
select = [i for i in scenarios if "" in i]
_df.index = [i.replace("solar-", "") for i in _df.index]
_df = (
    _df[select]
    .loc[_df.index.intersection(order)]
    .reindex(order)
    .stack()
    .reset_index()
)
# ax = (_df[select].loc[_df.index.intersection(order)].reindex(order)).T.plot(
_df.columns = ["Tech", "Scenario", "Capacity"]


colors = iter([plt.cm.tab20(i) for i in range(20)])
colors = [i for i in reversed([i for i in colors])]
fig, ax = plt.subplots(figsize=(8, 4))
ax = sns.barplot(
x="Tech", y="Capacity", hue="Scenario", palette=colors, data=_df
)
ax.set_xticklabels(labels=_df["Tech"].unique(), rotation="45")
ax.set_xlabel("")
#     kind="bar",
#     stacked=False,
#     #cmap="Paired",
#     color=[color_dict.get(c) for c in _df.loc[order].index],
#     rot=90,
# )

ax.legend()
# ax.set_ylim(-60, 70)
handles, labels = ax.get_legend_handles_labels()
lgd = {k: v for k, v in dict(zip(handles, labels)).items()}
ax.set_ylabel("Installed capacity in MW")
ax.grid(linestyle="--", lw=0.2)

# ax2 = ax.twinx()
# re_share.reindex(select).multiply(100).plot(
#    linestyle="", marker="D", color="green", label="RE-share", ax=ax2
# )
##ax2.set_ylim(0, 100)
# ax2.set_ylabel("RE-share in %")
# plt.xticks(rotation=0)
# lines2, labels2 = ax2.get_legend_handles_labels()
lgd = ax.legend(
    list(lgd.keys()),
    list(lgd.values()),
    loc="lower left",
    bbox_to_anchor=(0.1, -0.75),
    shadow=False,
    frameon=False,
    ncol=4,
)
plt.savefig(
    "visualization/figures/installed_capacities.pdf".format(""),
    bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)
_df.loc[_df.index.intersection(order)].reindex(order).T.to_latex(
    caption="Installed capacities in MW.",
    label="tab:installed_capacities",
    float_format="{:0.2f}".format,
    buf="visualization/tables/installed_capacities.tex",
)


all_capacities = pd.DataFrame()
storage_capacity = pd.DataFrame()
energy = pd.DataFrame()
peak_demand = {}
objective = pd.DataFrame()
investment_cost = pd.DataFrame()
for dir in os.listdir(path):
    filling_levels = pd.read_csv(
        os.path.join(path, dir, "filling_levels.csv"),
        index_col=0,
        parse_dates=True,
    )
    capacities = pd.read_csv(
        os.path.join(path, dir, "capacities.csv"), index_col=0
    )

    temp = pd.read_csv(
        os.path.join(path, dir, "costs.csv"), index_col=0
    )
    temp = temp.loc["Objective value"]
    temp.name = dir
    temp.index = ["Objective"]
    objective = pd.concat([objective, temp], axis=1, sort=False)

    temp = pd.read_csv(
        os.path.join(path, dir, "BB-electricity.csv"), index_col=0
    )
    peak_demand[dir] = (
        temp[[c for c in temp.columns if "load" in c]]
        .sum(axis=1)
        .max()
    )

    temp["phs-cos"] = temp[phs_storages].clip(upper=0).sum(axis=1)
    temp["phs"] = temp[phs_storages].clip(lower=0).sum(axis=1)
    temp["battery-cos"] = temp["lithium-battery"].clip(upper=0)
    temp["battery"] = temp["lithium-battery"].clip(lower=0)
    temp["el-load"] = temp["el-load"] * -1
    if "cruise-load-1" in temp.columns:
        cruiseload  = "cruise-load-1"
    elif "cruise-load" in temp.columns:
        cruiseload  = "cruise-load"
    else:
        cruiseload = "cruise-load-2"
    temp[cruiseload] = temp[cruiseload] * -1
    temp["ev-load"] = temp["ev-load"] * -1
    temp["el-excess"] = temp["el-excess"] * -1
    temp = temp.sum()
    temp.name = dir
    temp = temp.drop(storages)
    energy = pd.concat([energy, temp], axis=1, sort=False)

    temp = pd.read_csv(
        os.path.join(path, dir, "filling_levels.csv"), index_col=0,
    )
    temp = temp.max()
    temp.name = dir
    storage_capacity = pd.concat(
        [storage_capacity, temp], axis=1, sort=False
    )

    capacities.set_index(
        ["to", "carrier", "tech", "type"], append=True, inplace=True
    )
    capacities.columns = [dir]
    all_capacities = pd.concat(
        [all_capacities, capacities], axis=1, sort=False
    )
    temp_p = pd.read_csv(
        os.path.join(path, dir, "investment_power.csv"), index_col=0
    )
    temp_e = pd.read_csv(
        os.path.join(path, dir, "investment_energy.csv"), index_col=0
    )
    temp = (temp_p.iloc[0] * temp_p.iloc[1]).to_frame()
    temp.loc[temp_e.columns] = (
        temp.loc[temp_e.columns]
        + (temp_e.iloc[0] * temp_e.iloc[1]).to_frame()
    )
    temp.columns = [dir]
    investment_cost = pd.concat(
        [temp, investment_cost], axis=1, sort=False
    )

# wind = [i for i in investment_cost.index if "wind-onshore" in i]
# investment_cost.loc["wind-onshore"] = investment_cost.loc[wind].sum()
# investment_cost.drop(wind, inplace=True)
ax = (
    investment_cost[scenarios]
    .T.divide(1e6)
    .plot(
        kind="bar",
        stacked=True,
        color=[
            color_dict.get(i.replace("-cos", ""))
            for i in investment_cost[scenarios].index
        ],
    )
)
ax.legend()
# ax.set_ylim(-60, 70)
handles, labels = ax.get_legend_handles_labels()
lgd = {k: v for k, v in dict(zip(handles, labels)).items()}
ax.set_ylabel("Investment cost in Mio. BBD")
ax.grid(linestyle="--", lw=0.2)
lgd = ax.legend(
    list(lgd.keys()),
    list(lgd.values()),
    loc="lower left",
    bbox_to_anchor=(-0.05, -0.55),
    ncol=3,
    borderaxespad=0,
    frameon=False,
)
plt.savefig(
    "visualization/figures/investment_cost.pdf",
    bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)
investment_cost.T.divide(1e6).to_latex(
    caption="Annualised investment cost per technology for all scenarios in Mio. BBD.",
    label="tab:lcoe",
    column_format="lp{1.2cm}p{1.2cm}p{1.2cm}p{1.2cm}p{1.2cm}p{1.2cm}p{1.2cm}p{1.2cm}p{1.2cm}",
    float_format="{:0.2f}".format,
    buf="visualization/tables/investment_cost.tex",
)

# LCOE ----------------------------------------------------------------------
LCOE = (
    objective
    / energy.loc[[c for c in energy.index if "load" in c]].sum()
    / -1000
)
LCOE[scenarios].T.plot(kind="bar")

co = [i for i in scenarios if not "100" in i]
re = [i for i in scenarios if "100" in i]

ldf = pd.DataFrame(columns=co)
ldf.loc["COPT"] = LCOE[co].values[0]
ldf.loc["100RE"] = LCOE[re].values[0]
ax = ldf.T.plot(kind="bar", cmap="Accent_r", rot=0)
ax.legend()
# ax.set_ylim(-60, 70)
handles, labels = ax.get_legend_handles_labels()
lgd = {k: v for k, v in dict(zip(handles, labels)).items()}
ax.set_ylabel("LCOE in BBD/kWh")
ax.grid(linestyle="--", lw=0.2)
lgd = ax.legend(
    list(lgd.keys()),
    list(lgd.values()),
    loc="upper left",
    # bbox_to_anchor=(-0.05, -0.4),
    ncol=1,
    borderaxespad=0,
    frameon=False,
)
# plt.plot(figsize=(10, 5))
plt.savefig(
    "visualization/figures/lcoe.pdf",
    bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)
ldf.T.to_latex(
    caption="LCOE in BBD per kWh for all scenarios.",
    label="tab:lcoe",
    float_format="{:0.2f}".format,
    buf="visualization/tables/lcoe.tex",
)


# dispatchable capacities  ---------------------------------------------------
dispatchable_capacities = (
    all_capacities[scenarios]
    .T[
        [
            "hfo-lsce",
            "hfo-msce",
            "bagasse-st",
            "waste-ocgt",
            "hydro-phs",
            "lithium-battery",
        ]
    ]
    .sum(axis=1)
)
dispatchable_capacities / pd.Series(peak_demand)
df = pd.concat(
    [
        pd.Series(peak_demand),
        dispatchable_capacities,
        dispatchable_capacities / pd.Series(peak_demand),
    ],
    axis=1,
)
df.columns = [
    "Peak Demand in MW",
    "Dispatchable Capacity in MW",
    "Share in %",
]
df = df.T[scenarios].T
df.to_latex(
    caption="Peak demand and total dispatchable capacity in MW for all scenarios.",
    label="tab:energy",
    float_format="{:0.2f}".format,
    buf="visualization/tables/total_dispatchable_capacity.tex",
)

# energy plot ----------------------------------------------------------------

e = energy.dropna()
e.rename(
    index={
        "el-load": "demand",
        "cruise-load-1": "cruise-demand",
        "cruise-load-2": "cruise-demand",
        "ev-load": "ev-demand",
        "el-excess": "excess",
    },
    inplace=True,
)

e = e[scenarios].T

ax = e.divide(1e3).plot(
    kind="bar",
    stacked=True,
    color=[color_dict.get(i.replace("-cos", "")) for i in e.columns],
    label=[i if not "-cos" in i else None for i in e.columns],
)
ax.legend()
# ax.set_ylim(-60, 70)
handles, labels = ax.get_legend_handles_labels()
lgd = {
    k: v
    for k, v in dict(zip(handles, labels)).items()
    if "-cos" not in v
}
ax.set_ylabel("Energy in GWh")
ax.grid(linestyle="--", lw=0.5)
plt.xticks(rotation=90)

ax2 = ax.twinx()
re_share.reindex(select).multiply(100).plot(
    linestyle="",
    marker="o",
    markersize=4,
    color="darkred",
    label="RE-share",
    ax=ax2,
)
ax2.set_ylim(0, 100)
ax2.set_ylabel("RE share in %n")
lines2, labels2 = ax2.get_legend_handles_labels()
# lgd = ax.legend(list(lgd.keys()) + lines2, list(lgd.values()) + labels2, ...)
lgd = ax.legend(
    list(lgd.keys()) + lines2,
    list(lgd.values()) + labels2,
    loc="lower left",
    bbox_to_anchor=(-0.2, -0.55),
    ncol=4,
    borderaxespad=0,
    frameon=False,
)

# plt.plot(figsize=(10, 5))
plt.savefig(
    "visualization/figures/energy.pdf",
    bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)
e.divide(1e3).to_latex(
    caption="Energy supply and demand in GWh.",
    label="tab:energy",
    float_format="{:0.2f}".format,
    column_format="l"+ "p{1.3cm}" * 15,
    buf="visualization/tables/energy.tex",
)




hydro_ = {}
bio_ = {}
for dir in os.listdir(path):
    temp = pd.read_csv(
        os.path.join(path, dir, "BB-electricity.csv"), index_col=0, parse_dates=True
    )
    hydro = temp["hydro-phs"].to_frame()
    hydro["day"] = hydro.index.dayofyear.values
    hydro["hour"] = hydro.index.hour.values
    hydro.set_index(["hour", "day"], inplace=True)
    hydro = hydro.unstack("day")
    hydro.columns = hydro.columns.droplevel(0)
    hydro.sort_index(ascending=False, inplace=True)

    biomass = temp["bagasse-st"].to_frame()
    biomass["day"] = biomass.index.dayofyear.values
    biomass["hour"] = biomass.index.hour.values
    biomass.set_index(["hour", "day"], inplace=True)
    biomass = biomass.unstack("day")
    biomass.columns = biomass.columns.droplevel(0)
    biomass.sort_index(ascending=False, inplace=True)

    hydro_[dir] = hydro
    bio_[dir] = biomass


fig, axs = plt.subplots(2,2, sharex=True, sharey=True)
scenario1= "REF"
scenario2= "REF-100"
#vmax = max(ex.max().max(), im.max().max())
#vmin = min(ex.min().min(), im.min().min())
axs[0,0] = sns.heatmap(
    data=hydro_[scenario1].sort_index(ascending=False),
    xticklabels=False,
    yticklabels=4,
    cmap="bwr",
    vmax=max(hydro_[scenario1].max().max(),hydro_[scenario2].max().max()),
    vmin=min(hydro_[scenario1].min().min(), hydro_[scenario2].min().min()),
    ax=axs[0,0],
    #cbar_kws={"label": "PHS in MWW"},
)
axs[1,0] = sns.heatmap(
    data=bio_[scenario1].sort_index(ascending=False),
    xticklabels=40,
    yticklabels=4,
    cmap="summer",
    vmax=max(bio_[scenario1].max().max(),bio_[scenario2].max().max()),
    vmin=min(bio_[scenario1].min().min(), bio_[scenario2].min().min()),
    ax=axs[1,0],
    #cbar_kws={"label": "Bagasse in MW"},
)
axs[0,1] = sns.heatmap(
    data=hydro_[scenario2].sort_index(ascending=False),
    xticklabels=False,
    yticklabels=4,
    cmap="bwr",
    vmax=max(hydro_[scenario1].max().max(),hydro_[scenario2].max().max()),
    vmin=min(hydro_[scenario1].min().min(), hydro_[scenario2].min().min()),
    ax=axs[0,1],
    cbar_kws={"label": "PHS in MWW"},
)
axs[1,1] = sns.heatmap(
    data=bio_[scenario2].sort_index(ascending=False),
    xticklabels=40,
    yticklabels=4,
    cmap="summer",
    vmax=max(bio_[scenario1].max().max(),bio_[scenario2].max().max()),
    vmin=min(bio_[scenario1].min().min(), bio_[scenario2].min().min()),
    ax=axs[1,1],
    cbar_kws={"label": "Bagasse in MW"},
)

#for a in axs:
    #a.set_yticklabels(axs[1].get_yticklabels(), rotation=0, fontsize=8)
    #a.set_xticklabels(axs[1].get_xticklabels(), rotation=0, fontsize=8)
# axs[0,0].set_ylim(0, 24)
# axs[1,0].set_ylim(0, 24)
#
# axs[1,0].set_xlim(0, 365)
# axs[1,1].set_xlim(0, 365)

axs[0,0].set_ylabel("Hour of Day", fontsize=8)
axs[1,0].set_ylabel("Hour of Day", fontsize=8)
axs[0,1].set_ylabel("", fontsize=8)
axs[1,1].set_ylabel("", fontsize=8)

axs[0,0].set_title(scenario1)
axs[0,1].set_title(scenario2)
axs[1,0].set_xlabel("Day of Year")
axs[1,1].set_xlabel("Day of Year")
axs[0, 1].set_xlabel("")
axs[0, 0].set_xlabel("")
axs[0, 0].set_xticklabels("")


# plt.suptitle("Transmission Deviation for \n {0} vs. {1}".format(compare[0], compare[1]))
plt.savefig(
    "visualization/figures/heatmap-{}.pdf".format(scenario1),
    # bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)
