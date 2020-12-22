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

# Scenarios

Different weather/wind years have been selected: 

* AVG: 2006
* LOW: 2010
* High: 2002
