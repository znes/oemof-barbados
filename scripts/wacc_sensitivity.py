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
scenarios += ["NPHS"] + ["NPHS-" + name for name in ["100"]]
scenarios += ["EVUC"] + ["EVUC-" + name for name in ["100"]]
scenarios += ["LOP"] + ["LOP-" + name for name in ["100"]]
scenarios += ["LRC"] + ["LRC-" + name for name in ["100"]]
scenarios += ["MRC"] + ["MRC-" + name for name in ["100"]]
scenarios += ["HBC"] + ["HBC-" + name for name in ["100"]]

bus = "BB-electricity"
all_capacities = pd.DataFrame()
all_capacities_wacc = pd.DataFrame()
all_capacities_wacc_low = pd.DataFrame()

for dir in os.listdir(path):
    if "wacc" not in dir:
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

        capacities.columns = capacities.columns.droplevel(0)
        capacities.columns = [dir]
        all_capacities = pd.concat(
            [all_capacities, capacities], axis=1, sort=False
        )

        #capacities.groupby(level=[0]).sum()
for dir in os.listdir(path + "/wacc"):
        capacities_wacc = pd.read_csv(
            os.path.join(path, "wacc", dir, "capacities.csv"), index_col=0
        )
        capacities_wacc.set_index("to", append=True, inplace=True)
        capacities_wacc = (
            capacities_wacc.groupby(["to", "carrier", "tech"])
            .sum()
            .unstack("to")
        )
        capacities_wacc.index = ["-".join(i) for i in capacities_wacc.index]

        temp = pd.read_csv(
            os.path.join(path, dir, bus + ".csv"), index_col=0
        )
        temp = temp.sum()
        temp.name = dir

        capacities_wacc.columns = capacities_wacc.columns.droplevel(0)
        capacities_wacc.columns = [dir]
        all_capacities_wacc = pd.concat(
            [all_capacities_wacc, capacities_wacc], axis=1, sort=False
        )

for dir in os.listdir(path + "/wacc_low"):
        capacities_wacc_low = pd.read_csv(
            os.path.join(path, "wacc_low", dir, "capacities.csv"), index_col=0
        )
        capacities_wacc_low.set_index("to", append=True, inplace=True)
        capacities_wacc_low = (
            capacities_wacc_low.groupby(["to", "carrier", "tech"])
            .sum()
            .unstack("to")
        )
        capacities_wacc_low.index = ["-".join(i) for i in capacities_wacc_low.index]

        temp = pd.read_csv(
            os.path.join(path, dir, bus + ".csv"), index_col=0
        )
        temp = temp.sum()
        temp.name = dir

        capacities_wacc_low.columns = capacities_wacc_low.columns.droplevel(0)
        capacities_wacc_low.columns = [dir]
        all_capacities_wacc_low = pd.concat(
            [all_capacities_wacc_low, capacities_wacc_low], axis=1, sort=False
        )
        #capacities.groupby(level=[0]).sum()

all_capacities = all_capacities.sort_index(axis=1)
all_capacities_wacc = all_capacities_wacc.sort_index(axis=1)
all_capacities_wacc_low = all_capacities_wacc_low.sort_index(axis=1)

deviation = all_capacities_wacc.sub(all_capacities)
deviation_low = all_capacities_wacc_low.sub(all_capacities)

deviation.fillna(0, inplace=True)
deviation_low.fillna(0, inplace=True)

vmax=pd.concat([deviation_low, deviation]).max().max()
vmin=pd.concat([deviation_low, deviation]).min().min()
fmt = ".1f"
fig, (ax1, ax2) = plt.subplots(2,2, figsize=(10, 6), sharex=True, sharey=True)
cbar_ax = fig.add_axes([.91, .4, .03, .4])
sns.heatmap(
    deviation[[c for c in deviation.columns if not "-100" in c]].T,
    cmap="YlGnBu_r",
    cbar_ax=cbar_ax,
    vmin=vmin,
    vmax=vmax,
    annot=True,
    ax=ax1[0],
    fmt=fmt,
)
ax1[0].set_ylabel("COPT")
ax1[0].set_title("10% WACC")


sns.heatmap(
    deviation[[c for c in deviation.columns if "-100" in c]].T,
    cmap="YlGnBu_r",
    #cbar_kws={"label": "Deviation to SQ"},
    cbar_ax=cbar_ax,
    annot=True,
    vmin=vmin,
    vmax=vmax,
    ax=ax2[0],
    fmt=fmt,
)
ax2[0].set_ylabel("100% RE")
ax2[0].set_yticklabels([c for c in deviation.columns if not "-100" in c])

sns.heatmap(
    deviation_low[[c for c in deviation_low.columns if not "-100" in c]].T,
    cmap="YlGnBu_r",
    #cbar_kws={"label": "Deviation to SQ"},
    annot=True,
    vmin=vmin,
    vmax=vmax,
    cbar_ax=cbar_ax,
    ax=ax1[1],
    fmt=fmt,
)
ax1[1].set_title("4% WACC")
ax1[1].set_yticklabels([c for c in deviation.columns if not "-100" in c])
sns.heatmap(
    deviation_low[[c for c in deviation_low.columns if "-100" in c]].T,
    cmap="YlGnBu_r",
    cbar_kws={"label": "Absolute deviation in MW"},
    annot=True,
    vmin=vmin,
    vmax=vmax,
    cbar_ax=cbar_ax,
    ax=ax2[1],
    fmt=fmt,
)
ax2[1].set_yticklabels([c for c in deviation.columns if not "-100" in c])

fig.tight_layout(rect=[0, 0, .9, 1])

plt.savefig(
    "visualization/figures/heatmap_wacc_sensitivity_capacity_deviation.pdf",
    bbox_inches="tight",
)







energy = pd.DataFrame()
objective = pd.DataFrame()

for dir in os.listdir(path):
    if "wacc" not in dir:
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


energy_wacc = pd.DataFrame()
objective_wacc = pd.DataFrame()
for dir in os.listdir(path + "/wacc"):
    temp = pd.read_csv(
        os.path.join(path, "wacc", dir, "costs.csv"), index_col=0
    )
    temp = temp.loc["Objective value"]
    temp.name = dir
    temp.index = ["Objective"]
    objective_wacc = pd.concat([objective_wacc, temp], axis=1, sort=False)

    temp = pd.read_csv(
        os.path.join(path, "wacc", dir, "BB-electricity.csv"), index_col=0
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
    energy_wacc = pd.concat([energy_wacc, temp], axis=1, sort=False)

energy_wacc_low = pd.DataFrame()
objective_wacc_low = pd.DataFrame()
for dir in os.listdir(path + "/wacc_low"):
    temp = pd.read_csv(
        os.path.join(path, "wacc_low", dir, "costs.csv"), index_col=0
    )
    temp = temp.loc["Objective value"]
    temp.name = dir
    temp.index = ["Objective"]
    objective_wacc_low = pd.concat([objective_wacc_low, temp], axis=1, sort=False)

    temp = pd.read_csv(
        os.path.join(path, "wacc_low", dir, "BB-electricity.csv"), index_col=0
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
    energy_wacc_low = pd.concat([energy_wacc_low, temp], axis=1, sort=False)



LCOE = (
    objective
    / energy.loc[[c for c in energy.index if "load" in c]].sum()
    / -1000
)

LCOE_wacc = (
    objective_wacc
    / energy_wacc.loc[[c for c in energy_wacc.index if "load" in c]].sum()
    / -1000
)

LCOE_wacc_low = (
    objective_wacc_low
    / energy_wacc_low.loc[[c for c in energy_wacc_low.index if "load" in c]].sum()
    / -1000
)
#LCOE_wacc.columns = [c + "-wacc" for c in LCOE_wacc]
#ax = LCOE[scenarios].T.plot(kind="bar")
LCOE_tab  = pd.concat([LCOE_wacc_low, LCOE, LCOE_wacc])
LCOE_tab.index = ["WACC 4%", "WACC 7%", "WACC 10%"]
ax = LCOE_tab.T.sort_index().plot(kind="bar")
ax.set_ylabel("LCOE in BBD/kWh")
ax.grid(linestyle="--", lw=0.2)
lgd = ax.legend(
    loc="upper right",
    # bbox_to_anchor=(-0.05, -0.4),
    ncol=1,
    borderaxespad=0,
    frameon=True,
)
plt.savefig(
    "visualization/figures/lcoe_wacc_sensitivity.pdf",
    bbox_inches="tight",
)
