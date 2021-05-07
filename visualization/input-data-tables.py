import pandas as pd
import numpy as np
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.pyplot as plt
carrier = pd.read_excel("scenarios/carrier-technology.xls", sheet_name="carrier", index_col=[0,1])

carrier = carrier.rename(columns={"cost": "Cost (BBD/MWh)", "emission_factor": "CO\textsubscript{2} (t/MWh)"})
carrier =carrier.drop("source", axis=1)
carrier.loc[(["hfo", "diesel", "bagasse", "waste"], "base"), :].round(2).to_latex(
 caption="Cost of energy carriers in different scenarios",
 label="tab:carrier_cost",
 buf="visualization/tables/carrier_cost.tex"
)

tech = pd.read_excel("scenarios/carrier-technology.xls", sheet_name="technology-data", index_col=[0,1,2])
tech =tech.loc[(["wind", "solar", "bagasse", "hfo", "waste", "lithium", "hydro"], slice(None), "base")]
tech[["fom", "avf", "efficiency"]] = tech[["fom", "avf", "efficiency"]] * 100
tech = tech.round({'fom': 1, "avf": 1, "efficiency": 1})
tech = tech.drop(["source", "avf", "storage_capex", "name"], axis=1)
tech.index = tech.index.droplevel(2)
tech = tech.rename(columns={
    "capex": "capex ($/kW)",
    "lifetime": "lifetime (a)",
    "wacc": "wacc (-)",
    "efficiency":"eta (%)",
    "vom": "vom ($/MWh)",
    "fom": "fom (%)"})
tech.to_latex(
 caption="Cost and technical data for supply units. All costs are in BB\$.",
 #escape=False,
 #index_names=False,
 #bold_rows=True,
 column_format="llp{1.5cm}p{1.5cm}p{1cm}p{1cm}p{0.75cm}p{1.5cm}",
 label="tab:tech_data",
 buf="visualization/tables/tech_data.tex"
)
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
    ["el-dmand", "ev-demand", "cruise-demand", "aggregated-demand"],
    loc="lower left",
    bbox_to_anchor=(0.1, -0.45),
    ncol=2,
    borderaxespad=0,
    frameon=False,
)


inset = inset_axes(ax,
                    width="30%", # width = 30% of parent_bbox
                    height=1, # height : 1 inch
                    loc=1)
abs_profiles.iloc[:,2].resample("D").mean().plot(ax=inset, color="skyblue")
inset.set_ylabel("Demand in MW.", backgroundcolor='w')
inset.set_xlabel("Day of year", backgroundcolor='w')
inset.set_xticklabels([""], backgroundcolor='w')

plt.savefig(
    "visualization/figures/load-profiles-input.pdf",
    #bbox_extra_artists=(lgd,),
    bbox_inches="tight",
)
