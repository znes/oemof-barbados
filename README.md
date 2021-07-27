# oemof-barbados

Energy system model for Barbados based on the Open Energy Modelling Framework (oemof).


## Installation

To install create an virtualenv, activate the env and install the requirements:

```
virtualenv -p python3 oemof-barbados-env
source oemof-barbados-env/bin/activate
pip install -r requirements.txt
```


Then run make sure that the kernel can be selected inside the Jupyter-notebook:

```
python -m ipykernel install --user --name oemof-barbabos-env
```

## Usage

To use the model simply start the jupyter notebook:

```
jupyter-notebook
```

Then open the `model.ipynb` file. Inside this file you can specifiy the scenario an run the script
to compute results. Also you may adapt the path for results and other things.

Alternatively you may also run the notebook from your terminal:

```
jupyter nbconvert --excecute model.ipynb
```

# Scenario Assumptions

For the weather data zone1 has been used to illustrate the general pattern (s. `scripts/wind-data-analysis`). Within the model zone 4 has been used as it is the average with
regard to production. The timeindex is local time, therefore, the last four hours
of wind are missing as it has been generated in Barbadian time. These 4 values
haven been add the way pandas ffill() method works.

The weather year 2006 has been used as an average wind and solar year. The
demand profiles are all generic profiles that do not related to a specific year.
