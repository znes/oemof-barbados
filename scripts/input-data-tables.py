import pandas as pd

carrier = pd.read_excel("scenarios/carrier-technology.xls", sheet_name="carrier", index_col=[0,1])

carrier = carrier.rename(columns={"cost": "Cost (BBD/MWh)", "emission_factor": "CO\textsubscript{2} (t/MWh)"})
carrier =carrier.drop("source", axis=1)
carrier.loc[(["hfo", "diesel", "bagasse", "waste"], "base"), :].round(2).to_latex(
 caption="Cost of energy carriers in different scenarios",
 label="tab:carrier_cost",
 buf="visualization/tables/carrier_cost.tex"
)

tech = pd.read_excel("scenarios/carrier-technology.xls", sheet_name="technology-data", index_col=[0,1,2])
tech =tech.loc[(["wind", "solar", "bagasse", "hfo", "waste", "lithium", "hydro"], slice(None), "reference")]
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
