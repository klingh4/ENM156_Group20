# Group 20 project repository

This repository contains code related to ROC and ship simulation.


## How to set up the ship simulator submodule

Run the following commands in a terminal:
1. cd ship_simulator_zenoh
2. git submodule init
3. cd ..
4. git submodule update --remote


## Running the python-tkinter ROC simulator GUI

You need to have tk support installed on your machine (for example by installing your distribution's
tk and/or python3-tk package).

You also need to have the following python packages, which can be installed via pip:
```pip install tkintermapview eclipse-zenoh keelson protobuf matplotlib```

If you cannot install them system-wide you may need to create a virtual environment using venv:
```python -m venv <venvdir>```

Followed by activating the environment. In bash, cd to <venvdir> and ```source bin/activate```.

Finally, run ```python3 roc_simulator/src/roc_main.py```.

Then, in another terminal with the environment setup, run ```python3 ship_simulator_zenoh/src/ship_sim.py```

TODO: Make dependencies portable somehow.


## Running the CLI ROC simulator (not compatible with later ship simulator versions anymore)

### How to set up the Docker image

```cd ship_simulator_zenoh_extras```
```docker build -t riseship . (might take a while)```

### How to run the Docker image

```docker run -it riseship```

### How to connect a second terminal to the running Docker container

```docker ps # note the Container ID```
```docker exec -it <container ID> /bin/sh```

### How to run multiple Docker containers

```docker run -it --network=host <image> # In one terminal```
```docker run -it --network=host <image> # In another terminal```

